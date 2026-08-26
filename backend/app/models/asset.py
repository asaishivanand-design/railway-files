from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class Asset(Base):

    __tablename__ = "assets"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    asset_type = Column(
        String
    )

    location = Column(
        String
    )

    condition = Column(
        String
    )
