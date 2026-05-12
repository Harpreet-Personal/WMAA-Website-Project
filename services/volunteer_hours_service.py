from models import VolunteerHours
from sqlalchemy import func
from models import db


def get_volunteer_hours(volunteer_id):
    """
    Returns volunteer hours records and summary statistics.
    """

    records = VolunteerHours.query.filter_by(
        volunteer_id=volunteer_id
    ).order_by(
        VolunteerHours.submitted_at.desc()
    ).all()

    approved_hours = db.session.query(
        func.coalesce(func.sum(VolunteerHours.hours_completed), 0)
    ).filter(
        VolunteerHours.volunteer_id == volunteer_id,
        VolunteerHours.approval_status == "Approved"
    ).scalar()

    pending_hours = db.session.query(
        func.coalesce(func.sum(VolunteerHours.hours_completed), 0)
    ).filter(
        VolunteerHours.volunteer_id == volunteer_id,
        VolunteerHours.approval_status == "Pending"
    ).scalar()

    activities_logged = len(records)

    formatted_records = []

    for record in records:
        formatted_records.append({
            "id": record.id,
            "activity": record.activity_description,
            "hours": record.hours_completed,
            "status": record.approval_status,
            "submitted_at": record.submitted_at.strftime("%d %b %Y")
        })

    return {
        "approved_hours": approved_hours,
        "pending_hours": pending_hours,
        "activities_logged": activities_logged,
        "records": formatted_records
    }