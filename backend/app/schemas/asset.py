from pydantic import BaseModel


class AssetCreate(BaseModel):

    asset_type: str
    location: str
    condition: str


class AssetResponse(AssetCreate):

    id: int


    class Config:
        from_attributes = True
