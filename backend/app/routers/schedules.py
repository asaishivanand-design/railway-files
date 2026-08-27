from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleResponse


router = APIRouter(
    prefix="/schedules",
    tags=["Schedules"]
)



@router.post("/", response_model=ScheduleResponse)
def create_schedule(
    schedule: ScheduleCreate,
    db: Session = Depends(get_db)
):

    new_schedule = Schedule(
        **schedule.model_dump()
    )

    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)

    return new_schedule



@router.get("/", response_model=list[ScheduleResponse])
def get_schedules(
    db: Session = Depends(get_db)
):

    return db.query(
        Schedule
    ).all()



@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):

    schedule = db.query(
        Schedule
    ).filter(
        Schedule.id == schedule_id
    ).first()


    if not schedule:
        raise HTTPException(
            status_code=404,
            detail="Schedule not found"
        )


    return schedule