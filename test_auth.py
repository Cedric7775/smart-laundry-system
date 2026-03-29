import sqlite3
from werkzeug.security import check_password_hash
import requests
import json

# Check password
conn = sqlite3.connect('laundry.db')
c = conn.cursor()
c.execute('SELECT id, email, password FROM users WHERE email = ?', ('ck@gmail.com',))
user = c.fetchone()
conn.close()

if user:
    print(f'User found: {user[1]}')
    
    # Test different passwords
    test_passwords = ['password', 'test123', 'cedric', '123456', 'ck@gmail.com']
    
    for test_pw in test_passwords:
        if check_password_hash(user[2], test_pw):
            print(f'✅ Password "{test_pw}" is correct!')
            
            # Test login with correct password
            print('\nTesting login with correct password...')
            response = requests.post('http://localhost:5000/api/auth/login', 
                                   json={'email': 'ck@gmail.com', 'password': test_pw})
            print(f'Login Status: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                token = data.get('access_token')
                print(f'✅ Login successful!')
                print(f'Token: {token[:30]}...')
                
                # Test profile endpoint
                print('\nTesting profile endpoint...')
                headers = {'Authorization': f'Bearer {token}'}
                profile_response = requests.get('http://localhost:5000/api/auth/profile', 
                                              headers=headers)
                print(f'Profile Status: {profile_response.status_code}')
                print(f'Profile Response:')
                print(json.dumps(profile_response.json(), indent=2))
            break
    else:
        print('❌ No matching password found')
        print('Please register a new user with a known password')
