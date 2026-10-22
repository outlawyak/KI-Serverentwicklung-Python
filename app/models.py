"""SQLAlchemy models mapping the existing tables from `db/schema.sql`.

The schema is owned by the SQL script; these models only map it and are not
used to create or migrate tables.
"""

from datetime import date, datetime

from sqlalchemy import DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "game"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    genre: Mapped[str] = mapped_column(String(50))
    release_date: Mapped[date | None]
    version: Mapped[int] = mapped_column(server_default="0")

    # 1:1, the unique FK lives in game_details
    details: Mapped[GameDetails | None] = relationship(
        back_populates="game", cascade="all, delete-orphan", passive_deletes=True
    )
    # 1:N
    reviews: Mapped[list[Review]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Review.id",
    )

    # Optimistic locking: SQLAlchemy increments `version` on every UPDATE and
    # adds it to the WHERE clause, so a concurrent change raises
    # StaleDataError instead of being overwritten.
    __mapper_args__ = {"version_id_col": version}


class GameDetails(Base):
    __tablename__ = "game_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), unique=True
    )
    description: Mapped[str | None] = mapped_column(Text)
    developer: Mapped[str | None] = mapped_column(String(100))
    publisher: Mapped[str | None] = mapped_column(String(100))

    game: Mapped[Game] = relationship(back_populates="details")


class Review(Base):
    __tablename__ = "review"

    id: Mapped[int] = mapped_column(primary_key=True)
    game_id: Mapped[int] = mapped_column(
        ForeignKey("game.id", ondelete="CASCADE"), index=True
    )
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    game: Mapped[Game] = relationship(back_populates="reviews")
