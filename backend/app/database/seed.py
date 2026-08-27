from app.database.connection import SessionLocal
from app.models import MaintenanceTask, Asset, Schedule


db = SessionLocal()


tasks = [
    MaintenanceTask(
        track_id="T101",
        department="Engineering",
        task_type="Rail Inspection",
        description="Check rail cracks and defects",
        risk_level=8,
        priority_score=0,
        duration=4,
        status="Pending"
    ),

    MaintenanceTask(
        track_id="T202",
        department="Electrical",
        task_type="Power Maintenance",
        description="Inspect overhead electrical lines",
        risk_level=7,
        priority_score=0,
        duration=3,
        status="Pending"
    )
]


assets = [
    Asset(
        asset_type="Rail Track",
        location="Zone A",
        condition="Good"
    ),

    Asset(
        asset_type="Signal System",
        location="Zone B",
        condition="Needs Inspection"
    )
]


schedules = [
    Schedule(
        task_id=1,
        start_time="02:00",
        end_time="06:00",
        allocated_track="T101",
        status="Scheduled"
    )
]


db.add_all(tasks)
db.add_all(assets)
db.add_all(schedules)


db.commit()

db.close()


print("Database seeded successfully")