from datetime import datetime,timedelta

def date_object(date):
    return datetime.strptime(date, '%Y-%m-%d %H:%M:%S')

def order_data1():
    return {
            'usage_start_date': datetime.strptime("2020-04-20 11:00:00", '%Y-%m-%d %H:%M:%S'),
            'usage_end_date': datetime.strptime("2020-04-25 11:00:00", '%Y-%m-%d %H:%M:%S'),
            'transaction_code': "234567",
            'amount': "700",
            'no_of_guest': 34,
            'first_name': "sola",
            'last_name': "sola",
            'company_email': "ola mail",        
            }
def order_extra():
    return {
        'extras': [{"extraName": "Free Wifi", "amount": 6000}, {"extraName": "Free AC", "amount": 6000}]
    }

def order_data2():
    return {
            'usage_start_date': date_object("2020-04-26 10:00:00"),
            'usage_end_date': date_object("2020-04-28 15:00:00"),
            'transaction_code': "234967",
            'amount': "700",
            'no_of_guest': 45,
            'first_name': "sola",
            'last_name': "sola",
            'company_email': "soa mail",        
        }

def order_data3():
    return {
            'usage_start_date': date_object("2020-04-23 12:00:00"),
            'usage_end_date': date_object("2020-04-25 00:00:00"),
            'transaction_code': "T557190424557585",
            'amount': "700",
            'no_of_guest': 30,
            'first_name': "sola",
            'last_name': "sola",
            'company_email': "sla mail",
            }

def order_data4():
    return {
            'usage_start_date': date_object("2020-04-27 01:00:00"),
            'usage_end_date': date_object("2020-04-29 08:00:00"),
            'transaction_code': "none",
            'amount': "700",
            'no_of_guest': 25,
            'first_name': "sola",
            'last_name': "sola",
            'company_email': "sol mail",
        }

def order_data():
    return {
            'usage_start_date': datetime.now(),
            'usage_end_date': datetime.now()+timedelta(days=4),
            'transaction_code': "234567",
            'amount': "700",
            'no_of_guest': 20,
            'first_name': "sola",
            'last_name': "sola",
            'company_email': "solar mail"        
        }

def order_type_booking():
    return {
        'order_type':"booking",
    }

def order_type_reservation():
    return {
        "order_type":"reservation",
    }

