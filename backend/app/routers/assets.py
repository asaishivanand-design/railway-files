from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetCreate, AssetResponse


router = APIRouter(
    prefix="/assets",
    tags=["Assets"]
)


@router.post("/", response_model=AssetResponse)
def create_asset(
    asset: AssetCreate,
    db: Session = Depends(get_db)
):

    new_asset = Asset(
        **asset.model_dump()
    )

    db.add(new_asset)
    db.commit()
    db.refresh(new_asset)

    return new_asset



@router.get("/", response_model=list[AssetResponse])
def get_assets(
    db: Session = Depends(get_db)
):

    return db.query(
        Asset
    ).all()