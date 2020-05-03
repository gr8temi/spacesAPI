from datetime import datetime,timedelta

def order_data():
    return {
            'usage_start_date': datetime.now(),
            'usage_end_date': datetime.now()+timedelta(days=4),
            'transaction_code': "234567",
            'status': 'booked',

        }

def order_type_booking():
    return {
        'order_type':"booking",
    }

def order_type_reservation():
    return {
        "order_type":"reservation",
    }

