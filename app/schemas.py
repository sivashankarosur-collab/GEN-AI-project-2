from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

MIN_CHARS = 10
MAX_CHARS = 10000


class AnalyzeRequest(BaseModel):
    mode: Literal["profile", "career_plan", "job_match"] = "profile"
    input_text: str = ""
    profile_text: str = ""
    target_role: str = ""

    @field_validator("input_text", "profile_text", "target_role", mode="before")
    @classmethod
    def _strip(cls, v: Any) -> str:
        return "" if v is None else str(v).strip()

    @model_validator(mode="after")
    def _check(self) -> "AnalyzeRequest":
        labels = {"profile": "Resume / profile text", "career_plan": "Career goal",
                  "job_match": "Job description"}
        label = labels[self.mode]
        if not self.input_text:
            raise ValueError(f"{label} cannot be empty.")
        if len(self.input_text) < MIN_CHARS:
            raise ValueError(f"{label} is too short (minimum {MIN_CHARS} characters).")
        if len(self.input_text) > MAX_CHARS or len(self.profile_text) > MAX_CHARS:
            raise ValueError(f"Text is too long (maximum {MAX_CHARS} characters).")
        if self.mode == "job_match" and len(self.profile_text) < MIN_CHARS:
            raise ValueError("Job Match needs your profile/skills text as well (minimum 10 characters).")
        if len(self.target_role) > 100:
            raise ValueError("Target role is too long (maximum 100 characters).")
        return self


class _Base(BaseModel):
    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    @classmethod
    def _drop_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: v for k, v in data.items() if v is not None}
        return data


class Experience(_Base):
    role: str = ""
    organization: str = ""
    duration: str = ""
    highlights: List[str] = []


class Milestone(_Base):
    title: str
    timeframe: str = ""
    actions: List[str] = []


class JobMatch(_Base):
    matched_skills: List[str] = []
    missing_skills: List[str] = []
    match_percent: Optional[int] = Field(default=None, ge=0, le=100)
    match_summary: str = ""


class AnalysisResult(_Base):
    profile_summary: str
    skills: List[str] = []
    education: List[str] = []
    experience: List[Experience] = []
    target_role: str = ""
    skill_gaps: List[str] = []
    milestones: List[Milestone] = []
    job_match: JobMatch = JobMatch()
    missing_info: List[str] = []
