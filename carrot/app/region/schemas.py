from pydantic import BaseModel


class RegionResponse(BaseModel):
    id: str
    sido: str
    sigugun: str
    dong: str

    class Config:
        from_attributes = True
