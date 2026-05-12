from models import VolunteerSchedule


def get_volunteer_schedule(volunteer_id):
    """
    Returns volunteer schedule/events.
    """

    schedules = VolunteerSchedule.query.filter_by(
        volunteer_id=volunteer_id
    ).all()

    result = []

    for schedule in schedules:
        result.append({
            "id": schedule.id,
            "event_name": schedule.event_name,
            "event_date": schedule.event_date.strftime("%Y-%m-%d"),
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "location": schedule.location,
            "notes": schedule.notes
        })

    return result