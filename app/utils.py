from app.models import Room, RoomType, RoomRegulation, Customer, CustomerType, CustomerRegulation
from app import dao, db

def total_price(price, day, length, list_customer_type, room_id):
    total = price * day
    print(total)
    if length > 1:# Nếu tồn tại 3 khách
        room_regulation = db.session.query(Room.id, RoomRegulation.rate).\
            join(RoomType, Room.room_type_id == RoomType.id).\
            join(RoomRegulation, RoomType.id == RoomRegulation.room_type_id).\
            filter(Room.id == room_id).first()


        total = total + (total * room_regulation.rate)

    customer = db.session.query(Customer.id, CustomerType.type, CustomerRegulation.Coefficient).\
        join(CustomerType, Customer.customer_type_id == CustomerType.id).\
        join(CustomerRegulation, CustomerType.id == CustomerRegulation.customer_type_id).\
        filter(CustomerType.type == 'Foreign').first()

    for item in list_customer_type:
        if item == customer.type:
            total = total * customer.Coefficient
            return total
    return total