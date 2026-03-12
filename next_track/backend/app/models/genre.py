from sqlmodel import SQLModel, Field
import uuid


# shared properties
class GenreBase(SQLModel):
    name: str = Field(min_length=1, max_length=255)


class Genre(GenreBase, table=True):
    genre_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    
# individual genre table models    
class RockGenre(GenreBase, table=True):
    rock_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
   
class PopGenre(GenreBase, table=True):
    pop_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class JazzFolkGenre(GenreBase, table=True):
    jazz_folk_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class MetalGenre(GenreBase, table=True):
    metal_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class HipHopGenre(GenreBase, table=True):
    hip_hop_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ElectronicGenre(GenreBase, table=True):
    electronic_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class ExperimentalGenre(GenreBase, table=True):
    experimental_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

class OtherGenre(GenreBase, table=True):
    other_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
