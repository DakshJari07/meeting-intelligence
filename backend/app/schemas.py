from datetime import date, datetime
from uuid import UUID

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MeetingAnalysisRequest(BaseModel):
    project_id: UUID
    meeting_id: UUID
    transcript: str

    @field_validator("transcript")
    @classmethod
    def transcript_must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Transcript must not be empty")
        return value


class ExtractedCommitment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    owner: str | None
    due_date: date | None


class ExtractedDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str


class ExtractedQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: str


class ExtractedRisk(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str
    severity: Literal["low", "medium", "high"]


class MeetingAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(description="A factual summary of two to four concise sentences")
    commitments: list[ExtractedCommitment]
    decisions: list[ExtractedDecision]
    open_questions: list[ExtractedQuestion]
    risks: list[ExtractedRisk]


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime


class MeetingCreate(BaseModel):
    title: str
    meeting_date: date
    transcript: str | None = None


class MeetingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    meeting_date: date
    transcript: str | None
    summary: str | None
    created_at: datetime


class CommitmentCreate(BaseModel):
    meeting_id: UUID | None = None
    description: str
    owner: str | None = None
    due_date: date | None = None
    status: str = "open"


class CommitmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID | None
    description: str
    owner: str | None
    due_date: date | None
    status: str
    completed_at: datetime | None
    created_at: datetime


class DecisionCreate(BaseModel):
    meeting_id: UUID | None = None
    description: str


class DecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID | None
    description: str
    created_at: datetime


class OpenQuestionCreate(BaseModel):
    meeting_id: UUID | None = None
    question: str
    status: str = "open"


class OpenQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID | None
    question: str
    status: str
    created_at: datetime


class RiskCreate(BaseModel):
    meeting_id: UUID | None = None
    description: str
    severity: str = "medium"


class RiskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    meeting_id: UUID | None
    description: str
    severity: str
    created_at: datetime
