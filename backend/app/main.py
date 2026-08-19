from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db, test_database_connection
from app.models import (
    Commitment,
    Decision,
    Meeting,
    OpenQuestion,
    Project,
    Risk,
)
from app.schemas import (
    CommitmentCreate,
    CommitmentResponse,
    DecisionCreate,
    DecisionResponse,
    MeetingCreate,
    MeetingAnalysisRequest,
    MeetingAnalysisResponse,
    MeetingResponse,
    OpenQuestionCreate,
    OpenQuestionResponse,
    ProjectCreate,
    ProjectResponse,
    RiskCreate,
    RiskResponse,
)
from app.services.meeting_analyzer import (
    InvalidStructuredResponseError,
    LLMAPIError,
    MissingAPIKeyError,
    analyze_transcript,
)

app = FastAPI(
    title="Meeting Intelligence API",
    version="0.2.0",
)


@app.get("/")
def root():
    return {
        "message": "Meeting Intelligence API",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.post(
    "/analyze-meeting",
    response_model=MeetingAnalysisResponse,
)
def analyze_meeting(
    analysis_request: MeetingAnalysisRequest,
    db: Session = Depends(get_db),
):
    project = (
        db.query(Project)
        .filter(Project.id == analysis_request.project_id)
        .first()
    )
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == analysis_request.meeting_id)
        .first()
    )
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.project_id != analysis_request.project_id:
        raise HTTPException(
            status_code=400,
            detail="Meeting does not belong to this project",
        )

    try:
        return analyze_transcript(analysis_request.transcript)
    except MissingAPIKeyError:
        raise HTTPException(
            status_code=500,
            detail="Meeting analysis is not configured",
        )
    except LLMAPIError:
        raise HTTPException(
            status_code=502,
            detail="Meeting analysis service is unavailable",
        )
    except InvalidStructuredResponseError:
        raise HTTPException(
            status_code=502,
            detail="Meeting analysis returned an invalid response",
        )


@app.get("/db-health")
def db_health():
    try:
        result = test_database_connection()

        return {
            "status": "connected",
            "database_test": result,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {type(exc).__name__}",
        )


def get_project_or_404(
    project_id: UUID,
    db: Session,
):
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


def validate_meeting_for_project(
    meeting_id: UUID | None,
    project_id: UUID,
    db: Session,
):
    if meeting_id is None:
        return None

    meeting = (
        db.query(Meeting)
        .filter(
            Meeting.id == meeting_id,
            Meeting.project_id == project_id,
        )
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=400,
            detail="Meeting does not belong to this project",
        )

    return meeting


@app.post(
    "/projects",
    response_model=ProjectResponse,
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    project = Project(
        name=project_data.name,
        description=project_data.description,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


@app.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
):
    return (
        db.query(Project)
        .order_by(Project.created_at.desc())
        .all()
    )


@app.get(
    "/projects/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    return get_project_or_404(
        project_id=project_id,
        db=db,
    )


@app.post(
    "/projects/{project_id}/meetings",
    response_model=MeetingResponse,
)
def create_meeting(
    project_id: UUID,
    meeting_data: MeetingCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(
        project_id=project_id,
        db=db,
    )

    meeting = Meeting(
        project_id=project_id,
        title=meeting_data.title,
        meeting_date=meeting_data.meeting_date,
        transcript=meeting_data.transcript,
    )

    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return meeting


@app.get(
    "/projects/{project_id}/meetings",
    response_model=list[MeetingResponse],
)
def list_project_meetings(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project_or_404(
        project_id=project_id,
        db=db,
    )

    return (
        db.query(Meeting)
        .filter(Meeting.project_id == project_id)
        .order_by(
            Meeting.meeting_date.desc(),
            Meeting.created_at.desc(),
        )
        .all()
    )


@app.get(
    "/meetings/{meeting_id}",
    response_model=MeetingResponse,
)
def get_meeting(
    meeting_id: UUID,
    db: Session = Depends(get_db),
):
    meeting = (
        db.query(Meeting)
        .filter(Meeting.id == meeting_id)
        .first()
    )

    if not meeting:
        raise HTTPException(
            status_code=404,
            detail="Meeting not found",
        )

    return meeting


@app.post(
    "/projects/{project_id}/commitments",
    response_model=CommitmentResponse,
)
def create_commitment(
    project_id: UUID,
    commitment_data: CommitmentCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    validate_meeting_for_project(
        meeting_id=commitment_data.meeting_id,
        project_id=project_id,
        db=db,
    )

    commitment = Commitment(
        project_id=project_id,
        meeting_id=commitment_data.meeting_id,
        description=commitment_data.description,
        owner=commitment_data.owner,
        due_date=commitment_data.due_date,
        status=commitment_data.status,
    )

    db.add(commitment)
    db.commit()
    db.refresh(commitment)

    return commitment


@app.get(
    "/projects/{project_id}/commitments",
    response_model=list[CommitmentResponse],
)
def list_project_commitments(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    return (
        db.query(Commitment)
        .filter(Commitment.project_id == project_id)
        .order_by(Commitment.created_at.desc())
        .all()
    )


@app.post(
    "/projects/{project_id}/decisions",
    response_model=DecisionResponse,
)
def create_decision(
    project_id: UUID,
    decision_data: DecisionCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    validate_meeting_for_project(
        meeting_id=decision_data.meeting_id,
        project_id=project_id,
        db=db,
    )

    decision = Decision(
        project_id=project_id,
        meeting_id=decision_data.meeting_id,
        description=decision_data.description,
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision


@app.get(
    "/projects/{project_id}/decisions",
    response_model=list[DecisionResponse],
)
def list_project_decisions(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    return (
        db.query(Decision)
        .filter(Decision.project_id == project_id)
        .order_by(Decision.created_at.desc())
        .all()
    )


@app.post(
    "/projects/{project_id}/questions",
    response_model=OpenQuestionResponse,
)
def create_open_question(
    project_id: UUID,
    question_data: OpenQuestionCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    validate_meeting_for_project(
        meeting_id=question_data.meeting_id,
        project_id=project_id,
        db=db,
    )

    question = OpenQuestion(
        project_id=project_id,
        meeting_id=question_data.meeting_id,
        question=question_data.question,
        status=question_data.status,
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return question


@app.get(
    "/projects/{project_id}/questions",
    response_model=list[OpenQuestionResponse],
)
def list_project_questions(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    return (
        db.query(OpenQuestion)
        .filter(OpenQuestion.project_id == project_id)
        .order_by(OpenQuestion.created_at.desc())
        .all()
    )


@app.post(
    "/projects/{project_id}/risks",
    response_model=RiskResponse,
)
def create_risk(
    project_id: UUID,
    risk_data: RiskCreate,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    validate_meeting_for_project(
        meeting_id=risk_data.meeting_id,
        project_id=project_id,
        db=db,
    )

    risk = Risk(
        project_id=project_id,
        meeting_id=risk_data.meeting_id,
        description=risk_data.description,
        severity=risk_data.severity,
    )

    db.add(risk)
    db.commit()
    db.refresh(risk)

    return risk


@app.get(
    "/projects/{project_id}/risks",
    response_model=list[RiskResponse],
)
def list_project_risks(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    get_project_or_404(project_id, db)

    return (
        db.query(Risk)
        .filter(Risk.project_id == project_id)
        .order_by(Risk.created_at.desc())
        .all()
    )
