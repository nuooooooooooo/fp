from sqlmodel import SQLModel, Field
import uuid

# shared properties
class GenreSongBase(SQLModel):
    song_id: uuid.UUID = Field(default=None, foreign_key="song.song_id", primary_key=True)
    
# individual genre table models    
class RockGenreSong(GenreSongBase, table=True):
    rock_id: uuid.UUID = Field(default=None, foreign_key="rockgenre.rock_id", primary_key=True)

class PopGenreSong(GenreSongBase, table=True):
    pop_id: uuid.UUID = Field(default=None, foreign_key="popgenre.pop_id", primary_key=True)

class JazzFolkGenreSong(GenreSongBase, table=True):
    jazz_folk_id: uuid.UUID = Field(default=None, foreign_key="jazzfolkgenre.jazz_folk_id", primary_key=True)
    
class MetalGenreSong(GenreSongBase, table=True):
    metal_id: uuid.UUID = Field(default=None, foreign_key="metalgenre.metal_id", primary_key=True)

class HipHopGenreSong(GenreSongBase, table=True):
    hip_hop_id: uuid.UUID = Field(default=None, foreign_key="hiphopgenre.hip_hop_id", primary_key=True)

class ElectronicGenreSong(GenreSongBase, table=True):
    electronic_id: uuid.UUID = Field(default=None, foreign_key="electronicgenre.electronic_id", primary_key=True)

class ExperimentalGenreSong(GenreSongBase, table=True):
    experimental_id: uuid.UUID = Field(default=None, foreign_key="experimentalgenre.experimental_id", primary_key=True)

class OtherGenreSong(GenreSongBase, table=True):
    other_id: uuid.UUID = Field(default=None, foreign_key="othergenre.other_id", primary_key=True)
