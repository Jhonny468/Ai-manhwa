from pydantic import BaseModel, Field

class Character(BaseModel):
    name: str
    role: str
    description: str
    visual_traits: list[str] = Field(default_factory=list)
    relationships: list[str] = Field(default_factory=list)

class Location(BaseModel):
    name: str
    description: str
    visual_mood: str

class StoryAnalysisResult(BaseModel):
    title: str
    logline: str
    genre: list[str]
    tone: str
    synopsis: str
    major_themes: list[str]
    characters: list[Character]
    locations: list[Location]
    important_objects: list[str]
    chapter_breakdown: list[str]
