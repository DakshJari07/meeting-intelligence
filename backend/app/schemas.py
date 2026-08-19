from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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