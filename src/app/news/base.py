from pydantic import BaseModel

class Article(BaseModel):
    source: str = ""
    time: str = ""
    title: str = ""
    description: str = ""

