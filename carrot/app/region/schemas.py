from pydantic import BaseModel

class RegionResponse(BaseModel):
    id: str
    name: str

    class Config:
        from_attributes = True
