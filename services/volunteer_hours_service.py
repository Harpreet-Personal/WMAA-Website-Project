from sqlalchemy import func
from models import db
from models import VolunteerHours, VolunteerAvailability


def get_volunteer_hours(volunteer_id):

    records = VolunteerHours.query.filter_by(
        volunteer_id=volunteer_id
    ).order_by(
        VolunteerHours.submitted_at.desc()
    ).all()

    hours_data = []

    for record in records:

        availability = VolunteerAvailability.query.get(
            record.schedule_id
        )

        hours_data.append({
            "id": record.id,

            "date": (
                availability.available_date.strftime("%d %b %Y")
                if availability and availability.available_date
                else "-"
            ),

            "activity": (
                availability.shift_type
                if availability and availability.shift_type
                else "Availability Submission"
            ),

            "location": "Volunteer Availability",

            "start": (
                availability.start_time.strftime("%I:%M %p")
                if availability and availability.start_time
                else "-"
            ),

            "end": (
                availability.end_time.strftime("%I:%M %p")
                if availability and availability.end_time
                else "-"
            ),

            "hours": record.hours_completed,

            "status": record.approval_status
        })

    return hours_data