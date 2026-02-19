from sqlmodel import SQLModel, Field
from typing import Optional

# dummy model for testing
class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
