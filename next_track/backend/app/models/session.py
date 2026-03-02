from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from sqlalchemy import DateTime
from ..utils.helpers import get_datetime_now

import uuid


class Session(SQLModel, table=True):
    session_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(
        default_factory=get_datetime_now,
        sa_type=DateTime(timezone=True), 
    )