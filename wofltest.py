from datetime import datetime
import pytz

bookings = [{'usage_start_date': '2020-04-21', 'usage_end_date': '2020-04-22'},
            {'usage_start_date': '2020-06-24', 'usage_end_date': '2020-06-26'},
            {'usage_start_date': '2020-06-24', 'usage_end_date': '2020-06-26'},
            {'usage_start_date': '2020-07-01', 'usage_end_date': '2020-07-03'},
            {'usage_start_date': '2020-07-03', 'usage_end_date': '2020-07-07'},
            {'usage_start_date': '2020-06-24', 'usage_end_date': '2020-06-24'},
            {'usage_start_date': '2020-06-29', 'usage_end_date': '2020-06-30'},
            {'usage_start_date': '2020-07-01', 'usage_end_date': '2020-07-03'}]

# for books in bookings:
#     print({"usage_start_date": books["usage_start_date"].strftime(
#         "%Y-%m-%d"), "usage_end_date": books["usage_end_date"].strftime("%Y-%m-%d")})

daily_bookings = [{
    "start_date": "2020-04-23T12:00:00Z",
    "end_date": "2020-04-26T12:00:00Z"
},
    {
    "start_date": "2020-07-21T12:00:00Z",
    "end_date": "2020-07-24T12:00:00Z"

}
]

def already_booked(book,existing_bookings):
    start_date = datetime.fromisoformat(
        book["start_date"].replace('Z', '+00:00')).date()
    exists = [existing for existing in existing_bookings if pytz.utc.localize(
        datetime.strptime(existing["usage_end_date"], "%Y-%m-%d")).date() >=start_date]

    return exists 


intersection = []

[intersection.extend(already_booked(exists, bookings)) for exists in daily_bookings if (
    datetime.fromisoformat(
        exists["start_date"].replace('Z', '+00:00')).date() >= datetime.now().date())]

print(intersection)
