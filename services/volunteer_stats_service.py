from models import (
    db,
    VolunteerHours,
    VolunteerAttendance
)
from sqlalchemy import func


def get_total_hours(volunteer_id):
    """
    Returns total approved volunteer hours.
    """

    total = db.session.query(
        func.sum(VolunteerHours.hours_completed)
    ).filter(
        VolunteerHours.volunteer_id == volunteer_id,
        VolunteerHours.approval_status == "approved"
    ).scalar()

    return float(total or 0)


def get_events_attended(volunteer_id):
    """
    Returns total attended events/shifts.
    """

    count = VolunteerAttendance.query.filter_by(
        volunteer_id=volunteer_id,
        attendance_status="attended"
    ).count()

    return count


def get_tasks_completed(volunteer_id):
    """
    Returns completed volunteer tasks/events.
    """

    count = VolunteerHours.query.filter_by(
        volunteer_id=volunteer_id,
        approval_status="approved"
    ).count()

    return count


def get_dashboard_statistics(volunteer_id):
    """
    Returns all dashboard statistics in one response.
    """

    return {
        "hours_volunteered": get_total_hours(volunteer_id),
        "events_attended": get_events_attended(volunteer_id),
        "tasks_completed": get_tasks_completed(volunteer_id)
    }