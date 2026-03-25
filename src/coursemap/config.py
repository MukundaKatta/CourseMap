"""Configuration for CourseMap."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class CourseMapConfig(BaseModel):
    """Application configuration loaded from environment or defaults."""

    log_level: str = Field(default="INFO", description="Logging level")
    max_recommendations: int = Field(default=10, description="Max recommendations to return")
    min_score: float = Field(
        default=0.1, ge=0.0, le=1.0, description="Minimum relevance score threshold"
    )
    export_format: str = Field(default="json", description="Default export format")
    catalog_path: str | None = Field(default=None, description="Path to course catalog file")

    @classmethod
    def from_env(cls) -> CourseMapConfig:
        """Load configuration from environment variables."""
        return cls(
            log_level=os.getenv("COURSEMAP_LOG_LEVEL", "INFO"),
            max_recommendations=int(os.getenv("COURSEMAP_MAX_RECOMMENDATIONS", "10")),
            min_score=float(os.getenv("COURSEMAP_MIN_SCORE", "0.1")),
            export_format=os.getenv("COURSEMAP_EXPORT_FORMAT", "json"),
            catalog_path=os.getenv("COURSEMAP_CATALOG_PATH") or None,
        )


# Singleton config instance
config = CourseMapConfig.from_env()
