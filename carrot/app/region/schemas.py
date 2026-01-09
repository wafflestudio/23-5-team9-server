from pydantic import BaseModel


class RegionResponse(BaseModel):
    id: str
    sido: str
    sigugun: str
    dong: str
    name: str

    class Config:
        from_attributes = True
