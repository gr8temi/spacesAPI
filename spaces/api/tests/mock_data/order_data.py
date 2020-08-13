from datetime import datetime, timedelta
import json
import pytz
from ...models.spaces import Space
from ...models.spaces_category import SpaceCategory
from ...models.user import User
from ...models.agent import Agent
from ...models.availabilities import Availability
from .space_data import space_creation_data, space_category_data, extras_data, availability_data, hourly_space_data
from .registration_data import user_registration_data, agent_registration_data
from ...models.order_type import OrderType

def date_object(date):
    return f"{datetime.strptime(date, '%Y-%m-%d %H:%M:%S').isoformat()}Z"


def order_data1():
    return {
        'usage_start_date': f"{datetime.strptime('2020-04-20 11:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'usage_end_date': f"{datetime.strptime('2020-04-25 11:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'transaction_code': "234567",
        'amount': 700,
        'no_of_guest': 34,

        'name': "sola",
        'company_email': "ola mail",
    }


def order_extra():
    return {
        'extras': [{"extraName": "Free Wifi", "amount": 6000}, {"extraName": "Free AC", "amount": 6000}]
    }


def hourly_order_data():
    return {
        'hours_booked': json.dumps([{'date': '2020-04-20', 'time_in': '11:00', 'time_out': '13:00'}, {'date': '2020-04-21', 'time_in': '11:00', 'time_out': '13:00'}, {'date': '2020-04-22', 'time_in': '11:00', 'time_out': '13:00'}]),
        'usage_start_date': f"{datetime.strptime('2020-04-20 11:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'usage_end_date': f"{datetime.strptime('2020-04-22 13:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'transaction_code': "234567",
        'amount': 700,
        'no_of_guest': 34,
        'name': "sola",
        'company_email': "ola@gmail.com",
    }


def order_data3():
    return {
        'usage_start_date': f"{datetime.strptime('2020-04-22 13:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'usage_end_date': f"{datetime.strptime('2020-04-23 13:00:00', '%Y-%m-%d %H:%M:%S').isoformat()}Z",
        'transaction_code': "T557190424557585",
        'amount': 700,
        'no_of_guest': 30,
        'name': "sola",
        'company_email': "ola@gmail.com",
    }


def order_data4():
    return {
        'usage_start_date': date_object("2020-04-27 01:00:00"),
        'usage_end_date': date_object("2020-04-29 08:00:00"),
        'transaction_code': "none",
        'amount': 700,
        'no_of_guest': 25,
        'name': "sola",
        'company_email': "ola@gmail.com",
    }


def order_data():
    return {
        'usage_start_date': f"{datetime.now().isoformat()}Z",
        'usage_end_date': f"{(datetime.now()+timedelta(days=4)).isoformat()}Z",
        'transaction_code': "234567",
        'amount': 700,
        'no_of_guest': 20,
        'name': "sola",
        'company_email': "ola@gmail.com"
    }


def order_type_booking():
    return {
        'order_type': "booking",
    }


def order_type_reservation():
    return {
        "order_type": "reservation",
    }


def create_space():
    space_category = SpaceCategory.objects.create(**space_category_data())
    user = User.objects.create(**user_registration_data())
    agent = Agent.objects.create(
        user=user, **agent_registration_data())
    daily_space = Space.objects.create(
        **space_creation_data(), agent=agent, space_category=space_category)
    booking = OrderType.objects.create(order_type="booking")
    hourly_space = Space.objects.create(
        **hourly_space_data(), agent=agent, space_category=space_category)
    for avail in availability_data()["availability"]:
        Availability.objects.create(space=hourly_space.name,day=avail["day"], all_day=avail["all_day"],open_time=avail["open_time"],close_time=avail["close_time"])


    return (daily_space, hourly_space, user)


def booking_confirmed_data():
    daily_space, hourly_space, user = create_space()

    return {
        "hourly_booking":
        {"hours_booked":
            [
                {"start_date": "2020-11-11T10:00:00.000Z",
                    "end_date": "2020-11-11T12:00:00.000Z"},
                {"start_date": "2020-12-15T10:30:00.000Z",
                    "end_date": "2020-12-15T12:30:00.000Z"}
            ],
            "transaction_code": "-7vRrIja=cXbDrD",
            "no_of_guest": 0,
            "order_type": "booking",
            "space": f"{hourly_space.space_id}",
            "name": "Adams Temi",
            "company_email": "gr8temi@gmail.com",
            "extras": [{"name": "gym", "amount": 200}],
            "amount": 8700,
            "user": f"{user.user_id}",
            "duration": "hourly",
         },
        "daily_booking":
        {"daily_bookings":
         [
             {"start_date": "2020-11-11T18:00:00.000Z",
              "end_date": "2020-11-11T18:00:00.000Z"},
             {"start_date": "2020-12-15T18:30:00.000Z",
              "end_date": "2020-12-15T18:30:00.000Z"}
         ],
         "transaction_code": "-7vRrIja=cXbDrD",
         "no_of_guest": 0,
         "order_type": "booking",
         "space": f"{daily_space.space_id}",
         "name": "Adams Temi",
         "company_email": "gr8temi@gmail.com",
         "extras": [{"name": "gym", "amount": 200}],
         "amount": 8700,
         "user": f"{user.user_id}",
         "duration": "daily",
         },
        "old_bookings": {"daily_bookings":
                         [
                             {"start_date": f"{(datetime.now()-timedelta(days=1)).isoformat()}Z",
                              "end_date": f"{(datetime.now()-timedelta(days=1)).isoformat()}Z"},
                         ],
                         "transaction_code": "-7vRrIja=cXbDrD",
                         "no_of_guest": 0,
                         "order_type": "booking",
                         "space": daily_space.space_id,
                         "name": "Adams Temi",
                         "company_email": "gr8temi@gmail.com",
                         "extras": [{"name": "gym", "amount": 200}],
                         "amount": 8700,
                         "user": user.user_id,
                         "duration": "daily",
                         }

    }
