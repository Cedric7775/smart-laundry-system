import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('laundry.db')
c = conn.cursor()

# Create a booking for user 2 (cedric)
user_id = 2
name = "Cedric"
phone = "0718283361"
location = "Nairobi, Kenya"
service = "Regular Wash"
quantity = 15
price = 300
delivery_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')

c.execute('''
    INSERT INTO bookings (user_id, name, phone, location, service, quantity, price, delivery_date, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', (user_id, name, phone, location, service, quantity, price, delivery_date, 'pending'))

booking_id = c.lastrowid
conn.commit()

# Log the status
c.execute('''
    INSERT INTO order_status_logs (booking_id, status, notes)
    VALUES (?, ?, ?)
''', (booking_id, 'pending', 'Booking created'))

conn.commit()
conn.close()

print(f"✅ Created test booking {booking_id} for user {user_id}")
print(f"   Service: {service}")
print(f"   Delivery: {delivery_date}")
print(f"   Status: pending")
