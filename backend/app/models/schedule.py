from sqlalchemy import Column, Integer, String

from app.database.connection import Base


class Schedule(Base):

    __tablename__ = "block_schedule"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    task_id = Column(
        Integer
    )

    start_time = Column(
        String
    )

    end_time = Column(
        String
    )

    allocated_track = Column(
        String
    )

    status = Column(
        String,
        default="Pending"
    )
