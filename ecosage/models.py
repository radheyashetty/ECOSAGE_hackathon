from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class LandUseType(str, Enum):
    MONOCULTURE = "monoculture"
    AGROFORESTRY = "agroforestry"
    PASTURE = "pasture"
    FOREST = "forest"
    DEGRADED = "degraded"
    MIXED_CROPPING = "mixed_cropping"
    WETLAND = "wetland"


class RainfallCategory(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class TimeHorizon(str, Enum):
    SHORT = "short"  # <1 year
    MEDIUM = "medium"  # 1-3 years
    LONG = "long"  # 3+ years


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class GeoCoordinates(BaseModel):
    """Optional geographic coordinates for regional inference."""
    lat: Optional[float] = None
    lng: Optional[float] = None


class EnvironmentalMetrics(BaseModel):
    """Core environmental metrics schema (PRD Section 8.1)."""
    model_config = ConfigDict(str_strip_whitespace=True)

    soil_ph: Optional[float] = Field(None, ge=0, le=14, description="Soil pH level")
    soil_organic_carbon_pct: Optional[float] = Field(None, ge=0, le=100, description="Soil organic carbon percentage")
    soil_moisture_pct: Optional[float] = Field(None, ge=0, le=100, description="Soil moisture percentage")
    land_use_type: Optional[str] = Field(None, description="Current land use type")
    crop: Optional[str] = Field(None, description="Current crop being grown")
    species_richness_index: Optional[float] = Field(None, ge=0, le=1, description="Species richness index (0-1)")
    habitat_diversity_score: Optional[float] = Field(None, ge=0, le=1, description="Habitat diversity score (0-1)")
    rainfall: Optional[str] = Field(None, description="Rainfall pattern or mm/year")
    rainfall_mm_annual: Optional[float] = Field(None, ge=0, description="Annual rainfall in mm")
    temperature_avg_c: Optional[float] = Field(None, description="Average temperature in Celsius")
    pollution_index: Optional[float] = Field(None, ge=0, le=1, description="Pollution index (0-1)")
    deforestation_rate_pct: Optional[float] = Field(None, ge=0, le=100, description="Annual deforestation rate percentage")
    region: Optional[str] = Field(None, description="Geographic region or biome")


class EcoSageInput(BaseModel):
    """Input contract for EcoSage (PRD Section 8.2)."""
    model_config = ConfigDict(str_strip_whitespace=True)

    session_id: Optional[str] = Field(None, description="Session ID for multi-turn conversation")
    metrics: Optional[EnvironmentalMetrics] = Field(None, description="Structured environmental metrics")
    geo: Optional[GeoCoordinates] = Field(None, description="Geographic coordinates")
    query_text: Optional[str] = Field(None, description="Free-text query")


class Source(BaseModel):
    """A citation source."""
    name: str = Field(..., description="Human-readable source name")
    id: str = Field(..., description="Source document identifier")


class Recommendation(BaseModel):
    """A single evidence-backed recommendation (PRD Section 8.3)."""
    action: str = Field(..., description="What to do")
    mechanism: str = Field(..., description="Scientific mechanism / why it works")
    impacted_metrics: list[str] = Field(..., min_length=2, description="Environmental metrics affected")
    quantified_estimate: str = Field(..., description="Quantified impact estimate")
    time_horizon: TimeHorizon = Field(..., description="Expected timeframe for results")
    confidence: ConfidenceLevel = Field(..., description="Confidence level")
    sources: list[Source] = Field(..., min_length=1, description="Supporting citations")


class EcoSageResponse(BaseModel):
    """Output contract for EcoSage (PRD Section 8.3)."""
    session_id: str = Field(..., description="Session identifier")
    clarifying_questions: list[str] = Field(default_factory=list, description="Questions to ask if input is incomplete")
    recommendations: list[Recommendation] = Field(default_factory=list, description="Evidence-backed recommendations")
    reasoning_trace: Optional[dict] = Field(None, description="Debug: causal chain and retrieval trace")


class RetrievalResult(BaseModel):
    """A single retrieval result with trace info."""
    chunk_text: str
    source_id: str
    source_name: str
    similarity_score: float
    metadata: dict = Field(default_factory=dict)
    is_below_threshold: bool = False


class RetrievalTrace(BaseModel):
    """Full retrieval trace for debugging/auditability (FR-1.3, FR-1.4)."""
    session_id: str = ""
    query: str
    results: list[RetrievalResult]
    timestamp: str = ""
    usage_downstream: Optional[str] = None
    error: Optional[str] = None
