from sqlalchemy import Column, Integer, String, Float
from app.database.connection import Base


class MaintenanceTask(Base):

    __tablename__ = "maintenance_tasks"


    id = Column(
        Integer,
        primary_key=True
    )

    track_id = Column(
        String
    )

    department = Column(
        String
    )

    task_type = Column(
        String
    )

    description = Column(
        String
    )

    risk_level = Column(
        Float
    )

    priority_score = Column(
        Float,
        default=0
    )

    duration = Column(
        Float
    )

    status = Column(
        String,
        default="Pending"
    )