from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.task import TaskCreate, TaskResponse
from app.database.connection import get_db
from app.models.task import MaintenanceTask


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=TaskResponse)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):

    new_task = MaintenanceTask(**task.model_dump())

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/", response_model=list[TaskResponse])
def get_tasks(
    db: Session = Depends(get_db)
):

    tasks = db.query(
        MaintenanceTask
    ).all()

    return tasks



@router.get("/{task_id}")
def get_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(
        MaintenanceTask
    ).filter(
        MaintenanceTask.id == task_id
    ).first()


    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )


    return task



@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = db.query(
        MaintenanceTask
    ).filter(
        MaintenanceTask.id == task_id
    ).first()


    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )


    db.delete(task)
    db.commit()

    return {
        "message": "Task deleted"
    }