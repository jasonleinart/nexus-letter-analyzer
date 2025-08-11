"""
FastAPI main application for Nexus Letter Analysis API.

This API provides programmatic access to the nexus letter analysis engine
for automation and integration with external systems.
"""

import os
import sys
import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import asyncio
from contextlib import asynccontextmanager

# Import our auth components
try:
    from .auth import key_manager, check_rate_limit, validate_permission
except ImportError:
    from auth import key_manager, check_rate_limit, validate_permission

# Import our existing analysis components
from models.ai_analyzer import create_analyzer
from models.text_processor import create_processor
from models.scoring_engine import create_scorer
from models.recommendation_engine import create_recommendation_engine
from data.database import create_database
from utils.config import get_settings, validate_openai_key

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global components (initialized on startup)
analyzer = None
processor = None
scorer = None
rec_engine = None
database = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources."""
    global analyzer, processor, scorer, rec_engine, database

    logger.info("🚀 Starting Nexus Letter Analysis API...")

    # Validate configuration
    if not validate_openai_key():
        logger.error("❌ OpenAI API key not configured")
        raise RuntimeError("OpenAI API key required")

    # Initialize components
    try:
        analyzer = create_analyzer()
        processor = create_processor()
        scorer = create_scorer()
        rec_engine = create_recommendation_engine()
        database = create_database()

        logger.info("✅ All components initialized successfully")

    except Exception as e:
        logger.error(f"❌ Failed to initialize components: {str(e)}")
        raise RuntimeError(f"Initialization failed: {str(e)}")

    yield

    logger.info("🛑 Shutting down Nexus Letter Analysis API...")


# Create FastAPI app
app = FastAPI(
    title="Nexus Letter Analysis API",
    description="""
    Professional API for automated nexus letter analysis and workflow automation.
    
    ## Features
    - Real-time GPT-4 powered analysis
    - VA compliance scoring (0-100 scale)
    - Automated workflow recommendations
    - Metadata extraction and storage
    - PHI-compliant data handling
    
    ## Use Cases
    - Case management system integration
    - Automated document processing
    - Batch analysis workflows
    - Quality assurance automation
    """,
    version="1.0.0",
    contact={
        "name": "Legal AI Systems",
        "email": "admin@example.com",
    },
    license_info={
        "name": "Internal Use Only",
    },
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8502",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()


# Pydantic models for API
class LetterAnalysisRequest(BaseModel):
    """Request model for letter analysis."""

    letter_text: str = Field(
        ...,
        min_length=100,
        max_length=50000,
        description="Complete nexus letter text for analysis",
    )
    case_id: Optional[str] = Field(
        None, max_length=100, description="Optional case identifier for tracking"
    )
    priority: Optional[str] = Field(
        "normal",
        pattern="^(low|normal|high|urgent)$",
        description="Processing priority level",
    )

    @validator("letter_text")
    def validate_letter_text(cls, v):
        if not v.strip():
            raise ValueError("Letter text cannot be empty")
        return v.strip()


class BatchAnalysisRequest(BaseModel):
    """Request model for batch analysis."""

    letters: List[LetterAnalysisRequest] = Field(
        ..., max_items=10, description="List of letters to analyze (max 10)"
    )


class AnalysisResponse(BaseModel):
    """Response model for analysis results."""

    analysis_id: int
    overall_score: int
    nexus_strength: str
    workflow_decision: str
    workflow_message: str
    processing_time_seconds: float
    metadata: Dict[str, Optional[str]]
    critical_issues_count: int
    improvement_count: int
    created_at: str


class BatchAnalysisResponse(BaseModel):
    """Response model for batch analysis."""

    total_processed: int
    successful: int
    failed: int
    results: List[AnalysisResponse]
    processing_time_seconds: float


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    version: str
    components: Dict[str, str]


class AnalysisListResponse(BaseModel):
    """Response model for analysis listing."""

    total: int
    results: List[AnalysisResponse]


async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key authentication and check rate limits."""
    api_key = credentials.credentials

    # Validate API key
    key_info = key_manager.validate_key(api_key)
    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key"
        )

    # Check rate limits
    rate_info = check_rate_limit(api_key, key_info["environment"])

    return {
        "api_key": api_key,
        "environment": key_info["environment"],
        "key_name": key_info["name"],
        "rate_info": rate_info,
    }


# API Routes
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        components={
            "ai_analyzer": "ready" if analyzer else "not_initialized",
            "database": "ready" if database else "not_initialized",
            "scorer": "ready" if scorer else "not_initialized",
            "processor": "ready" if processor else "not_initialized",
        },
    )


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_letter(
    request: LetterAnalysisRequest, auth: Dict = Depends(verify_api_key)
):
    """
    Analyze a single nexus letter.

    Returns complete analysis with scoring, recommendations, and metadata.
    """
    start_time = time.time()

    try:
        logger.info(
            f"Processing analysis request (case_id: {request.case_id}, priority: {request.priority})"
        )

        # Preprocess text
        processed_text = processor.preprocess_for_ai(request.letter_text)

        # Perform AI analysis
        ai_results = analyzer.analyze_letter(processed_text)
        if ai_results.get("error"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"AI analysis failed: {ai_results.get('message', 'Unknown error')}",
            )

        # Calculate scores
        scoring_results = scorer.calculate_total_score(ai_results["analysis"])

        # Generate recommendations
        recommendations = rec_engine.generate_recommendations(
            scoring_results["overall_score"], scoring_results, ai_results["analysis"]
        )

        # Calculate processing time
        processing_time = time.time() - start_time

        # Save to database
        try:
            save_result = database.save_analysis(
                request.letter_text,
                ai_results["analysis"],
                scoring_results,
                recommendations,
                processing_time,
            )
            analysis_id = save_result["analysis_id"]
            metadata = save_result["metadata"]

        except Exception as db_error:
            logger.warning(f"Database save failed: {str(db_error)}")
            # Continue without database - don't fail the API call
            analysis_id = -1
            metadata = {}

        # Build response
        workflow_rec = recommendations.get("workflow_recommendation")
        response = AnalysisResponse(
            analysis_id=analysis_id,
            overall_score=scoring_results.get("overall_score", 0),
            nexus_strength=ai_results["analysis"].get("nexus_strength", "Unknown"),
            workflow_decision=workflow_rec.decision if workflow_rec else "unknown",
            workflow_message=(
                workflow_rec.message if workflow_rec else "No recommendation available"
            ),
            processing_time_seconds=round(processing_time, 2),
            metadata=metadata,
            critical_issues_count=len(
                ai_results["analysis"].get("critical_issues", [])
            ),
            improvement_count=len(recommendations.get("improvement_suggestions", [])),
            created_at=datetime.utcnow().isoformat(),
        )

        logger.info(
            f"✅ Analysis completed (ID: {analysis_id}, Score: {response.overall_score})"
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis processing failed: {str(e)}",
        )


@app.post("/api/v1/batch-analyze", response_model=BatchAnalysisResponse)
async def batch_analyze_letters(
    request: BatchAnalysisRequest,
    background_tasks: BackgroundTasks,
    auth: Dict = Depends(verify_api_key),
):
    """
    Analyze multiple nexus letters in batch.

    Processes up to 10 letters concurrently and returns aggregated results.
    """
    start_time = time.time()

    logger.info(f"Processing batch analysis request ({len(request.letters)} letters)")

    results = []
    successful = 0
    failed = 0

    # Process letters concurrently (but limit concurrency)
    semaphore = asyncio.Semaphore(3)  # Max 3 concurrent analyses

    async def analyze_single(letter_request: LetterAnalysisRequest):
        nonlocal successful, failed
        async with semaphore:
            try:
                # Convert to individual request
                response = await analyze_letter(letter_request, auth)
                results.append(response)
                successful += 1
                return response
            except Exception as e:
                logger.error(f"Failed to analyze letter: {str(e)}")
                failed += 1
                return None

    # Process all letters
    tasks = [analyze_single(letter) for letter in request.letters]
    await asyncio.gather(*tasks, return_exceptions=True)

    processing_time = time.time() - start_time

    logger.info(
        f"✅ Batch analysis completed ({successful} successful, {failed} failed)"
    )

    return BatchAnalysisResponse(
        total_processed=len(request.letters),
        successful=successful,
        failed=failed,
        results=results,
        processing_time_seconds=round(processing_time, 2),
    )


@app.get("/api/v1/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: int, auth: Dict = Depends(verify_api_key)):
    """Retrieve a specific analysis by ID."""
    try:
        analysis_data = database.get_analysis(analysis_id)

        if not analysis_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis {analysis_id} not found",
            )

        # Convert database result to response format
        return AnalysisResponse(
            analysis_id=analysis_data["id"],
            overall_score=analysis_data["overall_score"],
            nexus_strength=analysis_data.get("nexus_strength", "Unknown"),
            workflow_decision=analysis_data.get("workflow_decision", "unknown"),
            workflow_message=f"Score: {analysis_data['overall_score']}/100",
            processing_time_seconds=analysis_data.get("processing_time_seconds", 0),
            metadata={
                "patient_name": analysis_data.get("patient_name"),
                "patient_anonymized": analysis_data.get("patient_anonymized"),
                "doctor_name": analysis_data.get("doctor_name"),
                "facility_name": analysis_data.get("facility_name"),
            },
            critical_issues_count=analysis_data.get("critical_issues_count", 0),
            improvement_count=analysis_data.get("improvement_count", 0),
            created_at=analysis_data.get("created_at", datetime.utcnow().isoformat()),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve analysis {analysis_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis",
        )


@app.get("/api/v1/analyses", response_model=AnalysisListResponse)
async def list_analyses(
    limit: int = 10,
    offset: int = 0,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    auth: Dict = Depends(verify_api_key),
):
    """List recent analyses with optional filtering."""
    try:
        # Get recent analyses (simplified - would implement proper filtering)
        analyses = database.get_recent_analyses(limit + offset)

        # Apply offset and filtering
        filtered = analyses[offset : offset + limit]

        if min_score is not None:
            filtered = [a for a in filtered if a["overall_score"] >= min_score]
        if max_score is not None:
            filtered = [a for a in filtered if a["overall_score"] <= max_score]

        # Convert to response format
        results = []
        for analysis in filtered:
            results.append(
                AnalysisResponse(
                    analysis_id=analysis["id"],
                    overall_score=analysis["overall_score"],
                    nexus_strength=analysis.get("nexus_strength", "Unknown"),
                    workflow_decision=analysis.get("workflow_decision", "unknown"),
                    workflow_message=f"Score: {analysis['overall_score']}/100",
                    processing_time_seconds=analysis.get("processing_time_seconds", 0),
                    metadata={
                        "patient_anonymized": analysis.get("patient_anonymized"),
                        "doctor_name": analysis.get("doctor_name"),
                        "facility_name": analysis.get("facility_name"),
                    },
                    critical_issues_count=analysis.get("critical_issues_count", 0),
                    improvement_count=analysis.get("improvement_count", 0),
                    created_at=analysis.get(
                        "created_at", datetime.utcnow().isoformat()
                    ),
                )
            )

        return AnalysisListResponse(total=len(analyses), results=results)

    except Exception as e:
        logger.error(f"Failed to list analyses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list analyses",
        )


@app.get("/api/v1/alerts/pending")
async def get_pending_alerts(auth: Dict = Depends(verify_api_key)):
    """Get letters requiring immediate attention."""
    try:
        # Get recent analyses that need attention
        recent = database.get_recent_analyses(50)

        alerts = {
            "critical": [a for a in recent if a["overall_score"] < 50],
            "attorney_review": [a for a in recent if 50 <= a["overall_score"] < 70],
            "high_quality": [a for a in recent if a["overall_score"] >= 85],
        }

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "critical_count": len(alerts["critical"]),
            "review_count": len(alerts["attorney_review"]),
            "success_count": len(alerts["high_quality"]),
            "alerts": alerts,
        }

    except Exception as e:
        logger.error(f"Failed to get alerts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve alerts",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
