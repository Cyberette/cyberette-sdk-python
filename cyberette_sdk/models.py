"""Pydantic data models for Cyberette SDK responses."""

from typing import Optional, List
from pydantic import BaseModel, Field


class Segment(BaseModel):
    """Represents a time segment in audio or video with detection info."""

    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    score: float = Field(..., description="Detection score/confidence (0-100)")
    verdict: str = Field(
        ..., description="Detection verdict (REAL, DEEPFAKE, SUSPICIOUS)"
    )


class Detection(BaseModel):
    """Core detection results."""

    verdict: str = Field(
        ..., description="Overall verdict (REAL, DEEPFAKE, SUSPICIOUS)"
    )
    percentage: Optional[float] = Field(
        None, description="Confidence percentage (0-100)"
    )
    score: Optional[float] = Field(None, description="Detection score for images")
    segments: List[Segment] = Field(
        default_factory=list, description="Time-based segments"
    )


class DeepfakeAnalysis(BaseModel):
    """Deepfake detection analysis results."""

    name: str = Field(..., description="Model name used for detection")
    version: int = Field(..., description="Model version")
    detection: Detection = Field(..., description="Detection results")


class ImageResponse(BaseModel):
    """Response model for image classification."""

    metadata: Optional[dict] = Field(None)
    deepfake: DeepfakeAnalysis
    interpretability: Optional[dict] = Field(None)


class AudioResponse(BaseModel):
    """Response model for audio classification."""

    sample_rate: int
    deepfake: DeepfakeAnalysis


class VideoResponse(BaseModel):
    """Response model for video (visual only) classification."""

    frame_rate: int
    deepfake: DeepfakeAnalysis


class MultimodalVideoResponse(BaseModel):
    """Response model for video with both audio and visual tracks."""

    verdict: str
    percentage: float
    audio: AudioResponse
    video: VideoResponse


class BatchResultItem(BaseModel):
    """Individual item in batch processing result."""

    file: str
    verdict: Optional[str] = None
    percentage: Optional[float] = None
    error: Optional[str] = None


class BatchResult(BaseModel):
    """Batch processing results."""

    results: List[BatchResultItem]
    total: int
    successful: int
    failed: int


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str
    code: str
    details: Optional[dict] = None
