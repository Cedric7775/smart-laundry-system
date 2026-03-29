# ===============================
# TEMPORARY ADMIN CREATION ROUTE
# ===============================
# SECURITY NOTE: This route is for one-time admin setup only. DELETE THIS ROUTE IMMEDIATELY after creating the admin account!
@app.route('/create-admin', methods=['GET'])
def create_admin():
    """
    TEMPORARY: Create initial admin user for Smart Laundry System.
    SECURITY: DELETE THIS ROUTE AFTER USE!
    """
    admin_name = "Cedric Kimutai"
    admin_email = "cedrickimutai@gmail.com"
    admin_phone = "0718283361"
    admin_password = "cedric7775"
    admin_role = "admin"

    conn = get_db_connection()
    c = conn.cursor()
    # Check if admin already exists by email
    c.execute('SELECT id FROM users WHERE email = ?', (admin_email,))
    if c.fetchone():
        conn.close()
        return "Admin already exists"

    # Hash the password before storing
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash(admin_password)

    # Insert admin user using parameterized query
    c.execute('''
        INSERT INTO users (name, email, phone, password, role)
        VALUES (?, ?, ?, ?, ?)
    ''', (admin_name, admin_email, admin_phone, hashed_password, admin_role))
    conn.commit()
    conn.close()
    return "Admin account created successfully!"
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt
import sqlite3
import json
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=BASE_DIR, static_url_path='')

# CORS Configuration - Allow frontend access in production
CORS(app, resources={
    r"/api/*": {
        "origins": ["*"],  # In production, replace with specific domain
        "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)
jwt = JWTManager(app)

# Database setup
DATABASE = os.path.join(os.path.dirname(__file__), "laundry.db")

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # --- MIGRATION: Ensure 'role' column exists in users table ---
    # This block checks for the 'role' column and if missing, safely rebuilds the table with the correct schema.
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            password TEXT,
            role TEXT DEFAULT 'user'
        )
    ''')
    c.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in c.fetchall()]
    if 'role' not in columns:
        print("[MIGRATION] Migrating users table to include role column...")
        # 1. Create new table with correct schema
        c.execute('''
            CREATE TABLE IF NOT EXISTS users_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT UNIQUE,
                phone TEXT,
                password TEXT,
                role TEXT DEFAULT 'user'
            )
        ''')
        # 2. Copy data from old table, set role to 'user' for all
        c.execute('''
            INSERT INTO users_new (id, name, email, phone, password, role)
            SELECT id, name, email, phone, password, 'user' FROM users
        ''')
        # 3. Drop old users table
        c.execute('DROP TABLE users')
        # 4. Rename new table to users
        c.execute('ALTER TABLE users_new RENAME TO users')
        print("[MIGRATION] Users table rebuilt with role column.")
    
    # Services table
    c.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            price_per_item REAL NOT NULL,
            turnaround_days INTEGER DEFAULT 1,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Addresses table
    c.execute('''
        CREATE TABLE IF NOT EXISTS addresses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            label TEXT,
            address TEXT NOT NULL,
            phone TEXT,
            is_default INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Bookings table
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            service TEXT NOT NULL,
            quantity INTEGER,
            price REAL,
            delivery_date TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Order Status Logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_status_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (booking_id) REFERENCES bookings(id)
        )
    ''')
    
    # Contact submissions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'new',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

# Initialize database on startup - always run init_db to ensure tables exist
init_db()

# ============================================
# ROLE-BASED ACCESS CONTROL (RBAC)
# ============================================

def require_admin():
    """Decorator to require admin role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                identity = get_jwt_identity()
                claims = get_jwt()
                role = claims.get('role', 'customer')
                
                if role != 'admin':
                    return jsonify({'error': 'Admin access required'}), 403
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        return wrapper
    return decorator

def require_customer():
    """Decorator to require customer role (or higher)"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                identity = get_jwt_identity()
                claims = get_jwt()
                role = claims.get('role', 'customer')
                
                if role not in ['customer', 'admin']:
                    return jsonify({'error': 'Authentication required'}), 401
                
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
        return wrapper
    return decorator

def get_user_role():
    """Get current user's role from JWT"""
    try:
        claims = get_jwt()
        return claims.get('role', 'customer')
    except:
        return None

def get_user_id():
    """Get current user's ID from JWT"""
    try:
        return int(get_jwt_identity())
    except:
        return None

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new customer"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['email', 'password', 'name', 'phone']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        name = data['name'].strip()
        phone = data['phone'].strip()
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if user already exists
        c.execute('SELECT id FROM users WHERE email = ?', (email,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = generate_password_hash(password)
        
        # Create user with default 'customer' role
        c.execute('''
            INSERT INTO users (email, password, name, phone, role)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, hashed_password, name, phone, 'customer'))
        
        conn.commit()
        user_id = c.lastrowid
        conn.close()
        
        # Create JWT token with role
        access_token = create_access_token(identity=str(user_id), additional_claims={'role': 'customer'})
        
        return jsonify({
            'message': 'Registration successful',
            'user_id': user_id,
            'access_token': access_token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'phone': phone,
                'role': 'customer'
            }
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login customer"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].strip().lower()
        password = data['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Find user by email
        c.execute('SELECT id, email, name, phone, password, role FROM users WHERE email = ?', (email,))
        user = c.fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create JWT token with role
        user_role = user['role'] or 'customer'  # Default to customer if NULL
        access_token = create_access_token(identity=str(user['id']), additional_claims={'role': user_role})
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'phone': user['phone'],
                'role': user_role
            }
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT id, email, name, phone, address, role, created_at FROM users WHERE id = ?', (user_id,))
        user = c.fetchone()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'message': 'Profile retrieved successfully',
            'user': dict(user)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        
        # Validate data
        allowed_fields = ['name', 'phone', 'address']
        for field in data:
            if field not in allowed_fields:
                return jsonify({'error': f'Cannot update field: {field}'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check user exists
        c.execute('SELECT id FROM users WHERE id = ?', (user_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        if 'name' in data:
            c.execute('UPDATE users SET name = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                     (data['name'], user_id))
        if 'phone' in data:
            c.execute('UPDATE users SET phone = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                     (data['phone'], user_id))
        if 'address' in data:
            c.execute('UPDATE users SET address = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', 
                     (data['address'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Profile updated successfully'
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# BOOKING ENDPOINTS
# ============================================

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'phone', 'location', 'service']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get user_id if authenticated
        user_id = None
        try:
            user_id = int(get_jwt_identity())
        except:
            pass  # Allow anonymous bookings
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO bookings (user_id, name, phone, location, service, quantity, price, delivery_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data['name'],
            data['phone'],
            data['location'],
            data['service'],
            data.get('quantity', 0),
            data.get('price', 0),
            data.get('delivery_date', ''),
            'booked'
        ))
        
        conn.commit()
        booking_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Booking created successfully',
            'booking_id': booking_id,
            'status': 'booked'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings', methods=['GET'])
@jwt_required()
@require_admin()
def get_bookings():
    """Get all bookings (Admin only)"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM bookings ORDER BY created_at DESC')
        bookings = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'Bookings retrieved successfully',
            'bookings': bookings,
            'count': len(bookings)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/my-bookings', methods=['GET'])
@jwt_required()
def get_user_bookings():
    """Get current user's bookings"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM bookings WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        bookings = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'User bookings retrieved successfully',
            'bookings': bookings,
            'count': len(bookings)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['GET'])
def get_booking(booking_id):
    """Get specific booking"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        booking = c.fetchone()
        conn.close()
        
        if not booking:
            return jsonify({'error': 'Booking not found'}), 404
        
        return jsonify({
            'message': 'Booking retrieved successfully',
            'booking': dict(booking)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/<int:booking_id>', methods=['PATCH'])
@jwt_required()
@require_admin()
def update_booking(booking_id):
    """Update booking status (Admin only)"""
    try:
        data = request.json
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if booking exists
        c.execute('SELECT * FROM bookings WHERE id = ?', (booking_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Booking not found'}), 404
        
        # Update status
        c.execute('''
            UPDATE bookings 
            SET status = ?
            WHERE id = ?
        ''', (data.get('status', 'pending'), booking_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Booking updated successfully',
            'booking_id': booking_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================# SERVICES ENDPOINTS
# ============================================

@app.route('/api/services', methods=['GET'])
def get_services():
    """Get all available services"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM services WHERE is_active = 1 ORDER BY name ASC')
        services = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'Services retrieved successfully',
            'services': services,
            'count': len(services)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/<int:service_id>', methods=['GET'])
def get_service(service_id):
    """Get specific service"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        service = c.fetchone()
        conn.close()
        
        if not service:
            return jsonify({'error': 'Service not found'}), 404
        
        return jsonify({
            'message': 'Service retrieved successfully',
            'service': dict(service)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services', methods=['POST'])
@jwt_required()
@require_admin()
def create_service():
    """Create a new service (Admin only)"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'price_per_item']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO services (name, description, price_per_item, turnaround_days, is_active)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data.get('description', ''),
            data['price_per_item'],
            data.get('turnaround_days', 1),
            data.get('is_active', 1)
        ))
        
        conn.commit()
        service_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Service created successfully',
            'service_id': service_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/<int:service_id>', methods=['PATCH'])
@jwt_required()
@require_admin()
def update_service(service_id):
    """Update service details (Admin only)"""
    try:
        data = request.json
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if service exists
        c.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Service not found'}), 404
        
        # Update allowed fields - using parameterized queries to prevent SQL injection
        allowed_fields = ['name', 'description', 'price_per_item', 'turnaround_days', 'is_active']
        for field in allowed_fields:
            if field in data:
                if field == 'name':
                    c.execute('UPDATE services SET name = ? WHERE id = ?', (data[field], service_id))
                elif field == 'description':
                    c.execute('UPDATE services SET description = ? WHERE id = ?', (data[field], service_id))
                elif field == 'price_per_item':
                    c.execute('UPDATE services SET price_per_item = ? WHERE id = ?', (data[field], service_id))
                elif field == 'turnaround_days':
                    c.execute('UPDATE services SET turnaround_days = ? WHERE id = ?', (data[field], service_id))
                elif field == 'is_active':
                    c.execute('UPDATE services SET is_active = ? WHERE id = ?', (data[field], service_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Service updated successfully',
            'service_id': service_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/services/<int:service_id>', methods=['DELETE'])
@jwt_required()
@require_admin()
def delete_service(service_id):
    """Delete service (Admin only)"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if service exists
        c.execute('SELECT * FROM services WHERE id = ?', (service_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Service not found'}), 404
        
        # Soft delete by setting is_active to 0
        c.execute('UPDATE services SET is_active = 0 WHERE id = ?', (service_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Service deleted successfully',
            'service_id': service_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ADDRESSES ENDPOINTS
# ============================================

@app.route('/api/addresses', methods=['GET'])
@jwt_required()
def get_user_addresses():
    """Get current user's saved addresses"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT id, user_id, label, address, phone, is_default FROM addresses WHERE user_id = ? ORDER BY is_default DESC, created_at DESC', (user_id,))
        addresses = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'Addresses retrieved successfully',
            'addresses': addresses,
            'count': len(addresses)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/addresses', methods=['POST'])
@jwt_required()
def create_address():
    """Create a new saved address"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        
        # Validate required fields
        required = ['address']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # If this is the first address or marked as default, set as default
        is_default = data.get('is_default', 0)
        if is_default:
            # Remove default from other addresses
            c.execute('UPDATE addresses SET is_default = 0 WHERE user_id = ?', (user_id,))
        
        c.execute('''
            INSERT INTO addresses (user_id, label, address, phone, is_default)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('label', ''),
            data['address'],
            data.get('phone', ''),
            is_default
        ))
        
        conn.commit()
        address_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Address saved successfully',
            'address_id': address_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/addresses/<int:address_id>', methods=['GET'])
@jwt_required()
def get_address(address_id):
    """Get specific address"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM addresses WHERE id = ? AND user_id = ?', (address_id, user_id))
        address = c.fetchone()
        conn.close()
        
        if not address:
            return jsonify({'error': 'Address not found'}), 404
        
        return jsonify({
            'message': 'Address retrieved successfully',
            'address': dict(address)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/addresses/<int:address_id>', methods=['PATCH'])
@jwt_required()
def update_address(address_id):
    """Update address"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if address belongs to user
        c.execute('SELECT user_id FROM addresses WHERE id = ?', (address_id,))
        address = c.fetchone()
        if not address or address['user_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Address not found'}), 404
        
        # Update fields
        allowed_fields = ['label', 'address', 'phone', 'is_default']
        for field in allowed_fields:
            if field in data:
                if field == 'is_default' and data[field]:
                    # Remove default from other addresses
                    c.execute('UPDATE addresses SET is_default = 0 WHERE user_id = ?', (user_id,))
                c.execute(f'UPDATE addresses SET {field} = ? WHERE id = ?', 
                         (data[field], address_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Address updated successfully',
            'address_id': address_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/addresses/<int:address_id>', methods=['DELETE'])
@jwt_required()
def delete_address(address_id):
    """Delete address"""
    try:
        user_id = int(get_jwt_identity())
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if address belongs to user
        c.execute('SELECT user_id FROM addresses WHERE id = ?', (address_id,))
        address = c.fetchone()
        if not address or address['user_id'] != user_id:
            conn.close()
            return jsonify({'error': 'Address not found'}), 404
        
        c.execute('DELETE FROM addresses WHERE id = ?', (address_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Address deleted successfully',
            'address_id': address_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# ORDER STATUS LOGS ENDPOINTS
# ============================================

@app.route('/api/bookings/<int:booking_id>/status-logs', methods=['GET'])
def get_booking_status_logs(booking_id):
    """Get status history for a booking"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if booking exists
        c.execute('SELECT id FROM bookings WHERE id = ?', (booking_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Booking not found'}), 404
        
        c.execute('SELECT * FROM order_status_logs WHERE booking_id = ? ORDER BY updated_at DESC', (booking_id,))
        logs = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'Status logs retrieved successfully',
            'booking_id': booking_id,
            'logs': logs,
            'count': len(logs)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bookings/<int:booking_id>/status-logs', methods=['POST'])
def log_booking_status(booking_id):
    """Log a status update for a booking"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['status']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if booking exists
        c.execute('SELECT id FROM bookings WHERE id = ?', (booking_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Booking not found'}), 404
        
        # Log status
        c.execute('''
            INSERT INTO order_status_logs (booking_id, status, notes)
            VALUES (?, ?, ?)
        ''', (
            booking_id,
            data['status'],
            data.get('notes', '')
        ))
        
        # Update booking status
        c.execute('UPDATE bookings SET status = ? WHERE id = ?', (data['status'], booking_id))
        
        conn.commit()
        log_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Status logged successfully',
            'log_id': log_id,
            'booking_id': booking_id,
            'status': data['status']
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================# CONTACT ENDPOINTS
# ============================================

@app.route('/api/contacts', methods=['POST'])
def create_contact():
    """Create a new contact submission"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'phone', 'email', 'service', 'message']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO contacts (name, phone, email, service, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data['name'],
            data['phone'],
            data['email'],
            data['service'],
            data['message']
        ))
        
        conn.commit()
        contact_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Contact submission received successfully',
            'contact_id': contact_id,
            'status': 'new'
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts', methods=['GET'])
@jwt_required()
@require_admin()
def get_contacts():
    """Get all contact submissions (Admin only)"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        contacts = [dict(row) for row in c.fetchall()]
        conn.close()
        
        return jsonify({
            'message': 'Contacts retrieved successfully',
            'contacts': contacts,
            'count': len(contacts)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['GET'])
def get_contact(contact_id):
    """Get specific contact"""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        contact = c.fetchone()
        conn.close()
        
        if not contact:
            return jsonify({'error': 'Contact not found'}), 404
        
        return jsonify({
            'message': 'Contact retrieved successfully',
            'contact': dict(contact)
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/contacts/<int:contact_id>', methods=['PATCH'])
@jwt_required()
@require_admin()
def update_contact(contact_id):
    """Update contact status (Admin only)"""
    try:
        data = request.json
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if contact exists
        c.execute('SELECT * FROM contacts WHERE id = ?', (contact_id,))
        if not c.fetchone():
            conn.close()
            return jsonify({'error': 'Contact not found'}), 404
        
        # Update status
        c.execute('''
            UPDATE contacts 
            SET status = ?
            WHERE id = ?
        ''', (data.get('status', 'new'), contact_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Contact updated successfully',
            'contact_id': contact_id
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# EMAIL SENDING
# ============================================

@app.route('/api/contacts/send-email', methods=['POST'])
def send_email():
    """Send email from contact form"""
    try:
        data = request.json
        
        # Validate required fields
        required = ['name', 'phone', 'email', 'service', 'message']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Email credentials (use environment variables for security)
        EMAIL_ADDRESS = os.getenv('SENDER_EMAIL', 'smartlaundry98@gmail.com')
        EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', '')  # You need to set this
        RECEIVER_EMAIL = 'smartlaundry98@gmail.com'
        
        # If no password set, save to database instead of sending
        if not EMAIL_PASSWORD:
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''
                INSERT INTO contacts (name, phone, email, service, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (data['name'], data['phone'], data['email'], data['service'], data['message']))
            conn.commit()
            contact_id = c.lastrowid
            conn.close()
            
            return jsonify({
                'message': 'Message saved successfully (email not sent - configure SMTP)',
                'contact_id': contact_id
            }), 201
        
        # Create email message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f"New Contact Form Submission from {data['name']}"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = RECEIVER_EMAIL
        
        # Plain text version
        text = f"""
        New Contact Form Submission
        
        Name: {data['name']}
        Phone: {data['phone']}
        Email: {data['email']}
        Service: {data['service']}
        Message: {data['message']}
        
        Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        # HTML version
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #333;">New Contact Form Submission</h2>
            <p><strong>Name:</strong> {data['name']}</p>
            <p><strong>Phone:</strong> {data['phone']}</p>
            <p><strong>Email:</strong> {data['email']}</p>
            <p><strong>Service:</strong> {data['service']}</p>
            <p><strong>Message:</strong></p>
            <p style="background-color: #f5f5f5; padding: 10px; border-left: 4px solid #3b82f6;">
              {data['message'].replace(chr(10), '<br>')}
            </p>
            <p style="color: #666; font-size: 12px;">
              Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
          </body>
        </html>
        """
        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        # Send email via Gmail SMTP
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
        except smtplib.SMTPAuthenticationError:
            return jsonify({'error': 'Email authentication failed. Check credentials.'}), 500
        except smtplib.SMTPException as e:
            return jsonify({'error': f'SMTP error: {str(e)}'}), 500
        
        # Save to database
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO contacts (name, phone, email, service, message)
            VALUES (?, ?, ?, ?, ?)
        ''', (data['name'], data['phone'], data['email'], data['service'], data['message']))
        conn.commit()
        contact_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Email sent and message saved successfully',
            'contact_id': contact_id
        }), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'message': 'Smart Laundry Backend (Python Flask)'
    }), 200

# ============================================
# HOME
# ============================================

@app.route('/', methods=['GET'])
def index():
    """Serve the main index.html file"""
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/api', methods=['GET'])
def home():
    """API home endpoint"""
    return jsonify({
        'message': 'Smart Laundry Python Backend',
        'version': '1.0.0',
        'endpoints': {
            'services': {
                'GET': '/api/services - Get all services',
                'GET': '/api/services/<id> - Get service details',
                'POST': '/api/services - Create service (Admin)',
                'PATCH': '/api/services/<id> - Update service (Admin)',
                'DELETE': '/api/services/<id> - Delete service (Admin)'
            },
            'addresses': {
                'GET': '/api/addresses - Get user addresses (Auth required)',
                'GET': '/api/addresses/<id> - Get address (Auth required)',
                'POST': '/api/addresses - Save address (Auth required)',
                'PATCH': '/api/addresses/<id> - Update address (Auth required)',
                'DELETE': '/api/addresses/<id> - Delete address (Auth required)'
            },
            'bookings': {
                'POST': '/api/bookings - Create booking',
                'GET': '/api/bookings - Get all bookings',
                'GET': '/api/bookings/my-bookings - Get user bookings (Auth required)',
                'GET': '/api/bookings/<id> - Get booking details',
                'PATCH': '/api/bookings/<id> - Update booking status',
                'GET': '/api/bookings/<id>/status-logs - Get order status history',
                'POST': '/api/bookings/<id>/status-logs - Log status update'
            },
            'contacts': {
                'POST': '/api/contacts - Submit contact form',
                'GET': '/api/contacts - Get all contacts',
                'GET': '/api/contacts/<id> - Get contact details',
                'PATCH': '/api/contacts/<id> - Update contact status'
            },
            'auth': {
                'POST': '/api/auth/register - Register new user',
                'POST': '/api/auth/login - Login user',
                'GET': '/api/auth/profile - Get user profile (Auth required)',
                'PATCH': '/api/auth/profile - Update profile (Auth required)'
            }
        }
    }), 200

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Production configuration from environment variables
    PORT = int(os.getenv('PORT', 5000))  # Render assigns PORT automatically
    HOST = os.getenv('HOST', '0.0.0.0')  # Listen on all interfaces (required for production)
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # Disable debug in production
    
    print("\n" + "="*60)
    print("🚀 Smart Laundry Python Backend Starting...")
    print("="*60)
    print(f"✅ Server running on http://0.0.0.0:{PORT}")
    print(f"📡 Environment: {'DEVELOPMENT (DEBUG ON)' if DEBUG else 'PRODUCTION (DEBUG OFF)'}")
    print("📝 API Documentation:")
    print("   AUTH:")
    print("      POST   /api/auth/register - Register new user")
    print("      POST   /api/auth/login - Login user")
    print("      GET    /api/auth/profile - Get user profile")
    print("   SERVICES:")
    print("      GET    /api/services - Get all services")
    print("      GET    /api/services/<id> - Get service")
    print("      POST   /api/services - Create service")
    print("      PATCH  /api/services/<id> - Update service")
    print("      DELETE /api/services/<id> - Delete service")
    print("   ADDRESSES:")
    print("      GET    /api/addresses - Get user addresses")
    print("      POST   /api/addresses - Save address")
    print("      PATCH  /api/addresses/<id> - Update address")
    print("      DELETE /api/addresses/<id> - Delete address")
    print("   BOOKINGS:")
    print("      POST   /api/bookings - Create booking")
    print("      GET    /api/bookings - Get all bookings")
    print("      GET    /api/bookings/my-bookings - Get my bookings")
    print("      PATCH  /api/bookings/<id> - Update booking")
    print("      GET    /api/bookings/<id>/status-logs - Get status history")
    print("      POST   /api/bookings/<id>/status-logs - Log status")
    print("   CONTACTS:")
    print("      POST   /api/contacts - Submit contact form")
    print("      GET    /api/contacts - Get all contacts")
    print("      PATCH  /api/contacts/<id> - Update contact")
    print("="*60 + "\n")
    
    # Run server with environment configuration
    app.run(debug=DEBUG, host=HOST, port=PORT)
