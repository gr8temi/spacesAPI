from datetime import datetime,timedelta

def date_object(date):
            return datetime.strptime(date, '%Y-%m-%d').date()

def order_data1():
    return {
            'usage_start_date': date_object("2020-04-18"),
            'usage_end_date': date_object("2020-04-20"),
            'transaction_code': "234567"
            }
        
def order_data2():
    return {
            'usage_start_date': date_object("2020-04-21"),
            'usage_end_date': date_object("2020-04-23"),
            'transaction_code': "234967"
        }

def order_data3():
    return {
            'usage_start_date': date_object("2020-04-23"),
            'usage_end_date': date_object("2020-04-25"),
            'transaction_code': "234967"
        }

def order_data4():
    return {
            'usage_start_date': date_object("2020-04-27"),
            'usage_end_date': date_object("2020-04-29"),
            'transaction_code': "none"
        }

def order_data():
    return {
            'usage_start_date': datetime.now(),
            'usage_end_date': datetime.now()+timedelta(days=4),
            'transaction_code': "234567",
            'status': 'booked' 
        }

def order_type_booking():
    return {
        'order_type':"booking",
    }

def order_type_reservation():
    return {
        "order_type":"reservation",
    }


