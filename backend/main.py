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
from typing import Optional, List, Dict, Any
from datetime import datetime
from code_analyzer import generate_execution_steps

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

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        logger.info("✅ Gemini API configured successfully")
    except Exception as e:
        logger.error(f"❌ Gemini API configuration failed: {e}")
        model = None
else:
    logger.error("❌ GEMINI_API_KEY not found in environment!")
    model = None

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
            "Input validation"
        ],
        "endpoints": {
            "/": "API information",
            "/health": "Health check",
            "/explain": "AI-powered code explanation",
            "/detect-bugs": "Bug detection and analysis",
            "/visualize": "Step-by-step execution visualization"
        },
        "rate_limits": {
            "/explain": "10 requests/minute",
            "/detect-bugs": "10 requests/minute",
            "/visualize": "5 requests/minute"
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
            "code_analyzer": "operational"
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

@app.post("/explain")
@limiter.limit("10/minute")
async def explain_code(request: Request, code_request: CodeRequest):
    """Explain code with AI-powered analysis"""
    
    if not API_KEY or not model:
        logger.error("API key not configured")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set GEMINI_API_KEY in environment."
        )
    
    logger.info(f"📝 Explain request - Language: {code_request.language}, "
                f"Level: {code_request.level}, Code length: {len(code_request.code)}")
    
    try:
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

        logger.debug("Calling Gemini API...")
        response = model.generate_content(prompt)
        logger.debug("Gemini API responded")
        
        explanation = parse_ai_json_response(response.text)
        
        logger.info("✅ Successfully generated explanation")
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
@limiter.limit("10/minute")
async def detect_bugs(request: Request, code_request: CodeRequest):
    """Detect potential bugs and suggest fixes"""
    
    if not API_KEY or not model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service not configured. Please set GEMINI_API_KEY in environment."
        )
    
    logger.info(f"🐛 Bug detection request - Language: {code_request.language}")
    
    try:
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

        response = model.generate_content(prompt)
        bug_analysis = parse_ai_json_response(response.text)
        
        logger.info("✅ Bug analysis complete")
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
@limiter.limit("5/minute")
async def visualize_code(request: Request, code_request: CodeRequest):
    """Generate step-by-step execution visualization"""
    
    logger.info(f"🎬 Visualization request - Language: {code_request.language}")
    
    try:
        execution_steps = generate_execution_steps(
            code_request.code, 
            code_request.language
        )
        
        logger.info(f"✅ Generated {len(execution_steps)} execution steps")
        
        return {
            "success": True,
            "steps": execution_steps,
            "total_steps": len(execution_steps),
            "language": code_request.language
        }
        
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
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=port,
        reload=debug,
        log_level="info"
    )