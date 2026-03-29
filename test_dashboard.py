import sqlite3
from werkzeug.security import check_password_hash
import requests
import json

# Check password and get token
conn = sqlite3.connect('laundry.db')
c = conn.cursor()
c.execute('SELECT id, email, password FROM users WHERE email = ?', ('ck@gmail.com',))
user = c.fetchone()
conn.close()

if user:
    # Login
    response = requests.post('http://localhost:5000/api/auth/login', 
                           json={'email': 'ck@gmail.com', 'password': '123456'})
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('access_token')
        print(f'✅ Login successful!')
        print(f'Token: {token[:30]}...\n')
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test profile endpoint
        print('📋 Testing Profile Endpoint...')
        response = requests.get('http://localhost:5000/api/auth/profile', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Profile loaded successfully')
            profile = response.json()['user']
            print(f'   Name: {profile["name"]}')
            print(f'   Email: {profile["email"]}\n')
        
        # Test bookings endpoint  
        print('📦 Testing Bookings Endpoint...')
        response = requests.get('http://localhost:5000/api/bookings/my-bookings', headers=headers)
        print(f'Status: {response.status_code}')
        if response.status_code == 200:
            print('✅ Bookings loaded successfully')
            bookings = response.json()['bookings']
            print(f'   Count: {len(bookings)}')
            if bookings:
                for booking in bookings:
                    print(f'   - #{booking["id"]}: {booking["service"]} ({booking["status"]})')
            else:
                print('   No bookings found')
