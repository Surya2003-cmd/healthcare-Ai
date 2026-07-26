
def book_appointment(user_id, doctor_id, date):
    return {
        'status':'Booked',
        'user_id':user_id,
        'doctor_id':doctor_id,
        'date':date
    }
