from pydantic import BaseModel


class ScheduleCreate(BaseModel):

    task_id: int
    start_time: str
    end_time: str
    allocated_track: str


class ScheduleResponse(ScheduleCreate):

    id: int
    status: str


    class Config:
        from_attributes = True
