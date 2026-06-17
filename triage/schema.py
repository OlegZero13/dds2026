"""Structured output contract for the triage agent. Off-limits to attendees."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

VALID_CATEGORIES: tuple[str, ...] = (
    "billing",
    "technical",
    "feature_request",
    "complaint",
    "off_topic",
)

Category = Literal["billing", "technical", "feature_request", "complaint", "off_topic"]


class TriageResult(BaseModel):
    category: Category = Field(description="One of: billing, technical, feature_request, complaint")
    keywords: list[str] = Field(default_factory=list, description="Keywords extracted from the ticket")
    disputed_amount: float | None = Field(
        default=None, description="Disputed money amount for billing disputes, else null"
    )
