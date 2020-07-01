from datetime import datetime, timedelta
import json
import pytz

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
