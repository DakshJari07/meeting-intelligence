from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.database import get_db
from app.main import app
from app.models import Meeting, Project
from app.schemas import (
    ExtractedCommitment,
    ExtractedDecision,
    ExtractedQuestion,
    ExtractedRisk,
    MeetingAnalysisResponse,
)


class FakeQuery:
    def __init__(self, result):
        self.result = result

    def filter(self, *args):
        return self

    def first(self):
        return self.result


class FakeSession:
    def __init__(self, project=None, meeting=None):
        self.results = {Project: project, Meeting: meeting}

    def query(self, model):
        return FakeQuery(self.results[model])


@pytest.fixture
def ids():
    return SimpleNamespace(project_id=uuid4(), meeting_id=uuid4())


@pytest.fixture
def client(ids):
    project = SimpleNamespace(id=ids.project_id)
    meeting = SimpleNamespace(id=ids.meeting_id, project_id=ids.project_id)
    app.dependency_overrides[get_db] = lambda: FakeSession(project, meeting)
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def payload(ids, transcript="A substantive meeting transcript."):
    return {
        "project_id": str(ids.project_id),
        "meeting_id": str(ids.meeting_id),
        "transcript": transcript,
    }


def test_valid_transcript_returns_all_item_types(client, ids, monkeypatch):
    expected = MeetingAnalysisResponse(
        summary="The team reviewed launch readiness. Several follow-ups remain.",
        commitments=[
            ExtractedCommitment(
                description="Complete pricing analysis",
                owner="Sarah",
                due_date=date(2026, 8, 21),
            )
        ],
        decisions=[
            ExtractedDecision(description="Move the product launch to September 15")
        ],
        open_questions=[
            ExtractedQuestion(question="Has legal approved the launch plan?")
        ],
        risks=[
            ExtractedRisk(
                description="Legal approval may delay the launch",
                severity="high",
            )
        ],
    )
    monkeypatch.setattr("app.main.analyze_transcript", lambda transcript: expected)

    response = client.post("/analyze-meeting", json=payload(ids))

    assert response.status_code == 200
    assert response.json() == expected.model_dump(mode="json")


def test_transcript_with_no_actionable_items(client, ids, monkeypatch):
    expected = MeetingAnalysisResponse(
        summary="The team exchanged routine status updates. No actions were agreed.",
        commitments=[],
        decisions=[],
        open_questions=[],
        risks=[],
    )
    monkeypatch.setattr("app.main.analyze_transcript", lambda transcript: expected)

    response = client.post("/analyze-meeting", json=payload(ids))

    assert response.status_code == 200
    assert response.json()["commitments"] == []
    assert response.json()["decisions"] == []
    assert response.json()["open_questions"] == []
    assert response.json()["risks"] == []


def test_empty_transcript_is_rejected_before_llm_call(client, ids, monkeypatch):
    analyzer = lambda transcript: pytest.fail("LLM should not be called")
    monkeypatch.setattr("app.main.analyze_transcript", analyzer)

    response = client.post("/analyze-meeting", json=payload(ids, "   \n"))

    assert response.status_code == 422
    assert "Transcript must not be empty" in response.text


def test_invalid_project_returns_404(ids, monkeypatch):
    app.dependency_overrides[get_db] = lambda: FakeSession(None, None)
    monkeypatch.setattr(
        "app.main.analyze_transcript",
        lambda transcript: pytest.fail("LLM should not be called"),
    )
    with TestClient(app) as test_client:
        response = test_client.post("/analyze-meeting", json=payload(ids))
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Project not found"}


def test_invalid_meeting_returns_404(ids, monkeypatch):
    project = SimpleNamespace(id=ids.project_id)
    app.dependency_overrides[get_db] = lambda: FakeSession(project, None)
    monkeypatch.setattr(
        "app.main.analyze_transcript",
        lambda transcript: pytest.fail("LLM should not be called"),
    )
    with TestClient(app) as test_client:
        response = test_client.post("/analyze-meeting", json=payload(ids))
    app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Meeting not found"}


def test_meeting_from_another_project_returns_400(ids, monkeypatch):
    project = SimpleNamespace(id=ids.project_id)
    meeting = SimpleNamespace(id=ids.meeting_id, project_id=uuid4())
    app.dependency_overrides[get_db] = lambda: FakeSession(project, meeting)
    monkeypatch.setattr(
        "app.main.analyze_transcript",
        lambda transcript: pytest.fail("LLM should not be called"),
    )
    with TestClient(app) as test_client:
        response = test_client.post("/analyze-meeting", json=payload(ids))
    app.dependency_overrides.clear()

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Meeting does not belong to this project"
    }
