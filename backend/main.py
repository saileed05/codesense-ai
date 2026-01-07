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

# Parse ALLOWED_ORIGINS and strip whitespace
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in allowed_origins_str.split(",")]

# Log for debugging
logger.info(f"🌐 Configured CORS origins: {ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://codesense-2yre28va2-saileed05s-projects.vercel.app",
        "https://codesense-ai-one.vercel.app",
        "https://codesense-ai-saileed05-saileed05s-projects.vercel.app",
        "https://*.vercel.app",  # This allows all your Vercel deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"], # Expose all headers
    max_age=3600  
)

# Gemini API configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MAX_CODE_LENGTH = int(os.getenv("MAX_CODE_LENGTH", "10000"))
ALLOWED_LANGUAGES = ["python", "javascript", "java", "cpp", "typescript", "go", "c", "ruby"]
ALLOWED_LEVELS = ["eli5", "beginner", "intermediate", "expert"]

# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 2  # seconds
MAX_DELAY = 60  # seconds

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        logger.info("✅ Gemini API configured successfully")
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
            "Universal code visualization (BFS, DFS, Sorting, Arrays, Stacks)"
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

async def call_gemini_with_timeout(prompt: str, timeout: int = 30):
    """Call Gemini API with timeout protection"""
    try:
        loop = asyncio.get_event_loop()
        
        # Run in executor with timeout
        result = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: model.generate_content(prompt)
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
    """Explain code with AI-powered analysis (with caching)"""
    
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
        
        prompt = f"""You are an expert coding instructor. Explain this {code_request.language} code at a {code_request.level} level.

CODE:
```{code_request.language}
{code_request.code}
```

Return a JSON response with this EXACT structure (no additional text):
{{
  "summary": "Brief 2-3 sentence overview",
  "line_by_line": [
    {{
      "line_number": 1,
      "code": "actual code line",
      "explanation": "clear explanation"
    }}
  ],
  "key_concepts": [
    {{
      "concept": "Concept Name",
      "explanation": "Why it matters"
    }}
  ],
  "complexity": {{
    "time": "O(n)",
    "space": "O(1)",
    "explanation": "Brief reasoning"
  }}
}}

Level guidelines for {code_request.level}:
- eli5: Use simple analogies (cookies, toys, games), no jargon
- beginner: Clear explanations, define technical terms
- intermediate: Assume basic programming knowledge
- expert: Focus on performance, patterns, edge cases
"""

        logger.debug("Calling Gemini API with timeout...")
        response = await call_gemini_with_timeout(prompt, timeout=30)
        logger.debug("Gemini API responded")
        
        explanation = parse_ai_json_response(response.text)
        
        # Cache the response
        cache_response(cache_key, explanation)
        
        elapsed = time.time() - start_time
        logger.info(f"✅ Successfully generated explanation in {elapsed:.2f}s and cached")
        
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
    """Detect potential bugs and suggest fixes (with caching)"""
    
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
        
        prompt = f"""Analyze this {code_request.language} code for bugs, issues, and improvements.

CODE:
```{code_request.language}
{code_request.code}
```

Return JSON (no markdown):
{{
  "bugs_found": [
    {{
      "severity": "high|medium|low",
      "line": 3,
      "issue": "Brief description",
      "explanation": "Why this is a problem",
      "fix": "How to fix it"
    }}
  ],
  "code_smells": [
    {{
      "type": "performance|readability|maintainability",
      "line": 5,
      "issue": "What's wrong",
      "suggestion": "How to improve"
    }}
  ],
  "improvements": [
    {{
      "category": "readability|performance|security",
      "suggestion": "General improvement",
      "example": "Code example if applicable"
    }}
  ],
  "refactored_code": "Improved version of the code (optional)"
}}

Look for:
- Syntax/logic errors
- Performance issues
- Security vulnerabilities
- Missing error handling
- Edge cases
- Code smells
- Best practices violations

Return empty arrays if no issues found.
"""

        logger.debug("Calling Gemini API for bug detection...")
        response = await call_gemini_with_timeout(prompt, timeout=30)
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
    ✅ FIXED: Use code_analyzer as PRIMARY (supports stacks correctly!)
    Fall back to universal_visualizer only if code_analyzer fails
    """
    
    logger.info(f"🎬 Visualization request - Language: {code_request.language}")
    
    if code_request.language.lower() != 'python':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Visualization only supports Python. Got: {code_request.language}"
        )
    
    try:
        # ✅ ALWAYS try code_analyzer FIRST (it handles stacks, arrays, graphs correctly!)
        logger.info("🔍 Attempting static analysis with code_analyzer...")
        
        try:
            static_steps = generate_execution_steps(code_request.code, code_request.language)
            
            # ✅ Use code_analyzer if it generated ANY valid steps (not just errors)
            if static_steps and len(static_steps) > 0:
                first_step = static_steps[0]
                viz_type = first_step.get('visualization', {}).get('type', 'none')
                
                logger.info(f"📊 code_analyzer detected type: {viz_type}")
                
                # ✅ CRITICAL FIX: Accept ANY type except 'none' and 'error'
                # This includes: 'stack', 'array', 'queue', 'graph', 'dict', etc.
                if viz_type not in ['none', 'error']:
                    logger.info(f"✅ Using code_analyzer (detected {viz_type} with {len(static_steps)} steps)")
                    return {
                        "success": True,
                        "steps": static_steps,
                        "total_steps": len(static_steps),
                        "language": code_request.language,
                        "analyzer": "code_analyzer"
                    }
                else:
                    logger.info(f"⚠️ code_analyzer returned {viz_type}, trying universal_visualizer...")
            else:
                logger.warning("⚠️ code_analyzer returned empty steps")
                
        except Exception as e:
            logger.warning(f"⚠️ code_analyzer failed: {e}")
            import traceback
            logger.debug("Full traceback:")
            logger.debug(traceback.format_exc())
        
        # Fall back to universal_visualizer only if code_analyzer failed or returned none/error
        logger.info("🔄 Falling back to universal_visualizer...")
        tracer = UniversalCodeTracer(code_request.code)
        result = tracer.execute(max_steps=100)
        
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
        
    except Exception as e:
        logger.exception(f"❌ Visualization error: {e}")
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
    logger.info(f"🎨 Visualizers: code_analyzer (PRIMARY) + universal_visualizer (FALLBACK)")
    logger.info(f"📚 Stack support: ✅ ENABLED via code_analyzer")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=debug,
        log_level="info"
    )