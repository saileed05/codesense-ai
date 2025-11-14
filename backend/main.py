from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator, Field
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
import logging
import hashlib
import asyncio
import time
from typing import Optional, List, Dict, Any
from datetime import datetime
from code_analyzer import generate_execution_steps
from universal_visualizer import UniversalCodeTracer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="CodeSense AI API",
    version="2.0.0",
    description="AI-powered code explanation, debugging, and visualization"
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS with environment-based configuration
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Gemini API configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
ALLOWED_LANGUAGES = ["python", "javascript", "java", "cpp", "typescript", "go", "c", "ruby"]
ALLOWED_LEVELS = ["eli5", "beginner", "intermediate", "expert"]

# Retry configuration - REDUCED for faster response
MAX_RETRIES = 2  # Reduced from 3
BASE_DELAY = 1  # Reduced from 2
MAX_DELAY = 30  # Reduced from 60

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')  # FASTER MODEL
        logger.info("✅ Gemini API configured successfully with Flash model")
    except Exception as e:
        logger.error(f"❌ Gemini API configuration failed: {e}")
        model = None
else:
    logger.error("❌ GEMINI_API_KEY not found in environment!")
    model = None

# Response caching (in-memory)
response_cache = {}
MAX_CACHE_SIZE = 100

def generate_cache_key(code: str, language: str, level: str = "") -> str:
    """Generate cache key from request parameters"""
    cache_string = f"{code}|{language}|{level}"
    return hashlib.md5(cache_string.encode()).hexdigest()

def get_cached_response(cache_key: str):
    """Get response from cache"""
    return response_cache.get(cache_key)

def cache_response(cache_key: str, response_data: dict):
    """Store response in cache with size limit"""
    if len(response_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry (simple FIFO)
        response_cache.pop(next(iter(response_cache)))
    response_cache[cache_key] = response_data

# Pydantic models with validation
class CodeRequest(BaseModel):
    code: str = Field(..., min_length=1, max_length=MAX_CODE_LENGTH)
    language: str
    level: str = "beginner"

    @validator('code')
    def validate_code(cls, v):
        if not v.strip():
            raise ValueError('Code cannot be empty or whitespace only')
        # Basic security checks
        dangerous_patterns = ['__import__', 'eval(', 'exec(', 'compile(']
        if any(pattern in v.lower() for pattern in dangerous_patterns):
            raise ValueError('Code contains potentially dangerous patterns')
        return v.strip()

    @validator('language')
    def validate_language(cls, v):
        if v.lower() not in ALLOWED_LANGUAGES:
            raise ValueError(f'Language must be one of {ALLOWED_LANGUAGES}')
        return v.lower()

    @validator('level')
    def validate_level(cls, v):
        if v.lower() not in ALLOWED_LEVELS:
            raise ValueError(f'Level must be one of {ALLOWED_LEVELS}')
        return v.lower()

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# Custom rate limit exception handler
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Custom rate limit error with helpful message"""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Rate limit exceeded",
            "detail": f"Too many requests to {request.url.path}. Please wait a minute and try again.",
            "retry_after": "60 seconds",
            "tip": "Try caching responses or spacing out your requests"
        }
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An unexpected error occurred",
            code="INTERNAL_ERROR"
        ).dict()
    )

@app.get("/")
async def root():
    return {
        "message": "🧠 CodeSense AI API v2.0",
        "status": "online",
        "features": [
            "Custom AST parsing",
            "Pattern detection",
            "Bug detection with AI",
            "Complexity calculation",
            "Visual execution tracking",
            "Rate limiting",
            "Input validation",
            "Response caching",
            "Async AI calls with timeout",
            "Universal code visualization (BFS, DFS, Sorting, Arrays)"
        ],
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/explain": "AI-powered code explanation",
            "/detect-bugs": "Bug detection and analysis",
            "/visualize": "Step-by-step execution visualization",
            "/cache/stats": "Cache statistics"
        },
        "rate_limits": {
            "/explain": "15 requests/minute",
            "/detect-bugs": "15 requests/minute",
            "/visualize": "15 requests/minute"
        },
        "supported_languages": ALLOWED_LANGUAGES
    }

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with service status"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "services": {
            "api": "operational",
            "gemini_ai": "operational" if (API_KEY and model) else "unavailable",
            "code_analyzer": "operational",
            "universal_visualizer": "operational",
            "cache": f"{len(response_cache)}/{MAX_CACHE_SIZE} items"
        },
        "configuration": {
            "max_code_length": MAX_CODE_LENGTH,
            "allowed_languages": len(ALLOWED_LANGUAGES),
            "cors_origins": len(ALLOWED_ORIGINS)
        }
    }
    
    # Log health check
    logger.info(f"Health check performed - Gemini: {'✅' if (API_KEY and model) else '❌'}")
    
    return health_status

@app.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "cached_responses": len(response_cache),
        "max_capacity": MAX_CACHE_SIZE,
        "utilization_percent": f"{(len(response_cache)/MAX_CACHE_SIZE)*100:.1f}%",
        "status": "healthy" if len(response_cache) < MAX_CACHE_SIZE * 0.9 else "near_full"
    }

def parse_ai_json_response(text: str) -> dict:
    """Safely parse JSON from AI response, handling markdown code blocks"""
    try:
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
        
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}")
        logger.debug(f"Raw text (first 500 chars): {text[:500]}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse AI response: {str(e)}"
        )

async def call_gemini_with_timeout(prompt: str, timeout: int = 15):  # REDUCED from 30s to 15s
    """Call Gemini API with timeout protection - OPTIMIZED"""
    try:
        loop = asyncio.get_event_loop()
        
        # CRITICAL: Set shorter generation config for faster response
        generation_config = {
            "temperature": 0.3,  # Lower temp = faster, more focused
            "top_p": 0.8,
            "top_k": 20,
            "max_output_tokens": 2048,  # Limit output size
        }
        
        # Run in executor with timeout
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
            ),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        logger.error(f"AI request timed out after {timeout}s")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=f"AI service timeout - request took longer than {timeout} seconds"
        )

@app.post("/explain")
@limiter.limit("15/minute")
async def explain_code(request: Request, code_request: CodeRequest):
    """Explain code with AI-powered analysis (with caching) - OPTIMIZED"""
    
    if not API_KEY or not model:
        logger.error("API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set GEMINI_API_KEY in environment."
        )
    
    # Check cache first
    cache_key = generate_cache_key(code_request.code, code_request.language, code_request.level)
    cached = get_cached_response(cache_key)
    
    if cached:
        logger.info(f"✅ Cache hit for {code_request.language} code")
        return cached
    
    logger.info(f"🔍 Explain request - Language: {code_request.language}, "
                f"Level: {code_request.level}, Code length: {len(code_request.code)}")
    
    try:
        start_time = time.time()
        
        # SHORTER, MORE FOCUSED PROMPT
        prompt = f"""Explain this {code_request.language} code at {code_request.level} level. Be concise.

CODE:
```{code_request.language}
{code_request.code}
```

Return JSON (no markdown):
{{
  "summary": "Brief 1-2 sentence overview",
  "line_by_line": [
    {{"line_number": 1, "code": "line", "explanation": "short explanation"}}
  ],
  "key_concepts": [
    {{"concept": "Name", "explanation": "Brief why it matters"}}
  ],
  "complexity": {{
    "time": "O(n)",
    "space": "O(1)",
    "explanation": "One sentence"
  }}
}}

Keep explanations SHORT and FOCUSED."""

        logger.debug("Calling Gemini API...")
        response = await call_gemini_with_timeout(prompt, timeout=15)  # 15s timeout
        logger.debug("Gemini API responded")
        
        explanation = parse_ai_json_response(response.text)
        
        # Cache the response
        cache_response(cache_key, explanation)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Explanation generated in {elapsed:.2f}s and cached")
        
        return explanation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error explaining code: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to explain code: {str(e)}"
        )

@app.post("/detect-bugs")
@limiter.limit("15/minute")
async def detect_bugs(request: Request, code_request: CodeRequest):
    """Detect potential bugs and suggest fixes (with caching) - OPTIMIZED"""
    
    if not API_KEY or not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set GEMINI_API_KEY in environment."
        )
    
    # Check cache first
    cache_key = generate_cache_key(code_request.code, code_request.language, "bugs")
    cached = get_cached_response(cache_key)
    
    if cached:
        logger.info(f"✅ Cache hit for bug detection")
        return cached
    
    logger.info(f"🐛 Bug detection request - Language: {code_request.language}")
    
    try:
        start_time = time.time()
        
        # SHORTER PROMPT
        prompt = f"""Analyze this {code_request.language} code for bugs. Be concise.

CODE:
```{code_request.language}
{code_request.code}
```

Return JSON (no markdown):
{{
  "bugs_found": [
    {{"severity": "high|medium|low", "line": 3, "issue": "Brief", "explanation": "Short", "fix": "How to fix"}}
  ],
  "code_smells": [
    {{"type": "performance|readability", "line": 5, "issue": "What", "suggestion": "How"}}
  ],
  "improvements": [
    {{"category": "performance|security", "suggestion": "Brief", "example": "optional"}}
  ],
  "refactored_code": "Improved version (optional, only if needed)"
}}

Be CONCISE. Return empty arrays if no issues."""

        logger.debug("Calling Gemini API for bug detection...")
        response = await call_gemini_with_timeout(prompt, timeout=15)  # 15s timeout
        bug_analysis = parse_ai_json_response(response.text)
        
        # Cache the response
        cache_response(cache_key, bug_analysis)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Bug analysis complete in {elapsed:.2f}s and cached")
        
        return bug_analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error detecting bugs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze bugs: {str(e)}"
        )

@app.post("/visualize")
@limiter.limit("15/minute")
async def visualize_code(request: Request, code_request: CodeRequest):
    """
    Hybrid visualization - OPTIMIZED FOR SPEED
    Uses code_analyzer (fast) first, falls back to universal_visualizer
    """
    
    logger.info(f"🎬 Visualization request - Language: {code_request.language}")
    
    if code_request.language.lower() != 'python':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization only supports Python. Got: {code_request.language}"
        )
    
    try:
        # STEP 1: Try code_analyzer FIRST (it's faster, no execution)
        logger.debug("Attempting static analysis (code_analyzer)...")
        
        try:
            from code_analyzer import generate_execution_steps
            static_steps = generate_execution_steps(code_request.code, code_request.language)
            
            # Check if we got meaningful results
            if static_steps and len(static_steps) > 0:
                first_step = static_steps[0]
                viz_type = first_step.get('visualization', {}).get('type', 'none')
                
                # code_analyzer is good for: graphs, BFS, DFS, queues, arrays
                if viz_type in ['graph', 'graph_with_ds', 'queue', 'dict', 'array', 'stack']:
                    logger.info(f"✅ Using code_analyzer (detected {viz_type})")
                    return {
                        "success": True,
                        "steps": static_steps,
                        "total_steps": len(static_steps),
                        "language": code_request.language,
                        "analyzer": "code_analyzer"
                    }
        except Exception as e:
            logger.debug(f"code_analyzer failed: {e}")
        
        # STEP 2: Fall back to universal_visualizer (slower, but handles more cases)
        logger.debug("Using universal_visualizer...")
        
        # RUN IN BACKGROUND THREAD to avoid blocking
        loop = asyncio.get_event_loop()
        
        def run_visualizer():
            tracer = UniversalCodeTracer(code_request.code)
            return tracer.execute(max_steps=50)  # Limit to 50 steps for speed
        
        # Run with 10 second timeout
        result = await asyncio.wait_for(
            loop.run_in_executor(None, run_visualizer),
            timeout=10.0
        )
        
        if result['success']:
            logger.info(f"✅ Generated {result['total_steps']} steps (universal_visualizer)")
            return {
                "success": True,
                "steps": result['steps'],
                "total_steps": result['total_steps'],
                "language": code_request.language,
                "analyzer": "universal_visualizer"
            }
        else:
            logger.warning(f"⚠️ Partial execution: {result.get('error', 'Unknown error')}")
            return {
                "success": False,
                "steps": result.get('steps', []),
                "total_steps": len(result.get('steps', [])),
                "error": result.get('error', 'Execution failed'),
                "partial": True,
                "language": code_request.language,
                "analyzer": "universal_visualizer"
            }
        
    except asyncio.TimeoutError:
        logger.error("Visualization timeout after 10s")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Visualization took too long (>10s). Try simpler code or fewer iterations."
        )
    except Exception as e:
        logger.exception(f"Visualization error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Visualization failed: {str(e)}"
        )
    
if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"🚀 Starting CodeSense AI API on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    logger.info(f"🌐 Allowed origins: {ALLOWED_ORIGINS}")
    logger.info(f"💾 Cache enabled: {MAX_CACHE_SIZE} items max")
    logger.info(f"🎨 Universal visualizer: ENABLED (BFS, DFS, Sorting, Arrays)")
    logger.info(f"⚡ Using Gemini Flash model for faster responses")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=debug,
        log_level="info"
    )