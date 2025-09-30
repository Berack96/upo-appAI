from pydantic import BaseModel


class SocialPost(BaseModel):
    time: str = ""
    title: str = ""
    description: str = ""
    comments: list["SocialComment"] = []

    def __str__(self):
        return f"Title: {self.title}\nDescription: {self.description}\nComments: {len(self.comments)}\n[{" | ".join(str(c) for c in self.comments)}]"

class SocialComment(BaseModel):
    time: str = ""
    description: str = ""

    def __str__(self):
        return f"Time: {self.time}\nDescription: {self.description}"

# TODO IMPLEMENTARLO SE SI USANO PIU' WRAPPER (E QUINDI PIU' SOCIAL)
class SocialWrapper:
    pass
