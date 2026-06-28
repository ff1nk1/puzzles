import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, func, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.DB.database import Base


class Puzzles(Base):
    __tablename__ = "puzzles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[str]
    description: Mapped[str]
    difficulty: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    tests: Mapped[list["Test"]] = relationship(back_populates="puzzle", cascade="all, delete-orphan")
    submissions: Mapped[List["Submission"]] = relationship(
        "Submission",
        back_populates="puzzle",
        cascade="all, delete-orphan"  # Если удалить пазл, удалятся и все его попытки
    )


class Test(Base):
    __tablename__ = "tests"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('puzzles.id',ondelete="CASCADE"), nullable=False, index=True)
    input_data: Mapped[str] = mapped_column(nullable=False)
    expected_output: Mapped[str] = mapped_column(nullable=False)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    puzzle: Mapped["Puzzles"] = relationship(back_populates="tests")


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(nullable=False,unique=True)
    email: Mapped[str] = mapped_column(nullable=False,unique=True)
    password: Mapped[str]


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey('puzzles.id',ondelete="CASCADE"), nullable=False, index=True)
    language: Mapped[str] = mapped_column(nullable=False)
    code: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    verdict: Mapped[str] = mapped_column(nullable=True)
    detail: Mapped[Optional[str]] = mapped_column(nullable=True)
    puzzle: Mapped["Puzzles"] = relationship("Puzzles", back_populates="submissions")