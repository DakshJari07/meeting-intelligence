import os

from openai import OpenAI
from pydantic import ValidationError

from app.schemas import MeetingAnalysisResponse


MODEL = "gpt-5-mini"

SYSTEM_PROMPT = """You extract meeting intelligence from a transcript.

Return only facts explicitly supported by the transcript.
- Summary: 2 to 4 concise, factual sentences. Do not invent information.
- Commitments: only specific tasks or responsibilities. Set owner and due_date to
  null unless each is explicitly stated. Dates must be ISO 8601 (YYYY-MM-DD).
- Decisions: only actual agreed decisions, never suggestions or proposals.
- Open questions: unresolved questions, pending approvals, and unclear next steps.
- Risks: only issues that could delay, block, or negatively affect the project.
  Severity must be low, medium, or high and should reflect the transcript.
- Return an empty array for every item type absent from the transcript.

Never invent people, deadlines, commitments, decisions, risks, or answers to
unresolved questions."""


class MissingAPIKeyError(RuntimeError):
    pass


class LLMAPIError(RuntimeError):
    pass


class InvalidStructuredResponseError(RuntimeError):
    pass


def analyze_transcript(transcript: str) -> MeetingAnalysisResponse:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise MissingAPIKeyError("OPENAI_API_KEY is not configured")

    try:
        response = OpenAI(api_key=api_key).responses.parse(
            model=MODEL,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": transcript},
            ],
            text_format=MeetingAnalysisResponse,
        )
    except ValidationError as exc:
        raise InvalidStructuredResponseError(
            "The model returned an invalid structured response"
        ) from exc
    except Exception as exc:
        raise LLMAPIError("The meeting analysis provider request failed") from exc

    parsed = response.output_parsed
    if parsed is None:
        raise InvalidStructuredResponseError(
            "The model did not return a structured response"
        )

    try:
        return MeetingAnalysisResponse.model_validate(parsed)
    except ValidationError as exc:
        raise InvalidStructuredResponseError(
            "The model returned an invalid structured response"
        ) from exc
