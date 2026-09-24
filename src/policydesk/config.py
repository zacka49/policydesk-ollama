from __future__ import annotations

from datetime import date
from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ReturnRules(BaseModel):
    standard_window_days: int = Field(gt=0, le=365)
    max_order_value_for_draft_gbp: float = Field(gt=0)


class GenerationConfig(BaseModel):
    model: str
    temperature: float = Field(ge=0, le=2)
    timeout_seconds: float = Field(gt=0, le=300)
    max_schema_retries: int = Field(ge=0, le=3)


class RetrievalConfig(BaseModel):
    top_k: int = Field(ge=1, le=20)


class AppConfig(BaseModel):
    policy_version: str
    clock: date
    returns: ReturnRules
    generation: GenerationConfig
    retrieval: RetrievalConfig


def load_config(path: Path) -> AppConfig:
    return AppConfig.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

