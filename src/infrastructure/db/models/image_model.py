import datetime
import uuid

from sqlalchemy import String, Integer,ForeignKey, func, DateTime, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column


from src.infrastructure.db.models.base import Base

class ImageModel(Base):
    __tablename__ = 'images'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    image_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(
        String(25),
        index=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(250),
        nullable=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user: Mapped["UserModel"] = relationship("UserModel", back_populates="images")
