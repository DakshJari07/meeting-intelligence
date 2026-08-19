import uuid

from sqlalchemy import Column, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name = Column(
        String,
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    meetings = relationship(
        "Meeting",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    commitments = relationship(
        "Commitment",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    decisions = relationship(
        "Decision",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    open_questions = relationship(
        "OpenQuestion",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    risks = relationship(
        "Risk",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    title = Column(
        String,
        nullable=False,
    )

    meeting_date = Column(
        Date,
        nullable=False,
    )

    transcript = Column(
        Text,
        nullable=True,
    )

    summary = Column(
        Text,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="meetings",
    )

    commitments = relationship(
        "Commitment",
        back_populates="meeting",
    )

    decisions = relationship(
        "Decision",
        back_populates="meeting",
    )

    open_questions = relationship(
        "OpenQuestion",
        back_populates="meeting",
    )

    risks = relationship(
        "Risk",
        back_populates="meeting",
    )


class Commitment(Base):
    __tablename__ = "commitments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    owner = Column(
        String,
        nullable=True,
    )

    due_date = Column(
        Date,
        nullable=True,
    )

    status = Column(
        String,
        nullable=False,
        default="open",
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="commitments",
    )

    meeting = relationship(
        "Meeting",
        back_populates="commitments",
    )


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="decisions",
    )

    meeting = relationship(
        "Meeting",
        back_populates="decisions",
    )


class OpenQuestion(Base):
    __tablename__ = "open_questions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )

    question = Column(
        Text,
        nullable=False,
    )

    status = Column(
        String,
        nullable=False,
        default="open",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="open_questions",
    )

    meeting = relationship(
        "Meeting",
        back_populates="open_questions",
    )


class Risk(Base):
    __tablename__ = "risks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    meeting_id = Column(
        UUID(as_uuid=True),
        ForeignKey("meetings.id", ondelete="SET NULL"),
        nullable=True,
    )

    description = Column(
        Text,
        nullable=False,
    )

    severity = Column(
        String,
        nullable=False,
        default="medium",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship(
        "Project",
        back_populates="risks",
    )

    meeting = relationship(
        "Meeting",
        back_populates="risks",
    )