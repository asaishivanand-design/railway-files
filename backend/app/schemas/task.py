from pydantic import BaseModel


class TaskCreate(BaseModel):

    track_id: str
    department: str
    task_type: str
    description: str
    risk_level: float
    duration: float


class TaskResponse(TaskCreate):

    id: int
    priority_score: float
    status: str


    class Config:
        from_attributes = True
