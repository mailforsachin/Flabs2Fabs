import sys
import os
sys.path.append('.')

try:
    # Try bcrypt first
    import bcrypt
    
    password = "Welcome2026!".encode('utf-8')
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    print(f"Using bcrypt - Hashed password: {hashed_password[:30]}...")
    
except ImportError:
    # Fallback to werkzeug
    from werkzeug.security import generate_password_hash
    hashed_password = generate_password_hash("Welcome2026!")
    print(f"Using werkzeug - Hashed password: {hashed_password[:30]}...")

# Insert into database
import subprocess
import json

# Escape the password for SQL
escaped_hash = hashed_password.replace("'", "''")

sql = f"""
INSERT INTO users (username, email, hashed_password, is_admin, is_active) 
VALUES ('sashy', 'sashy@flabs2fabs.app', '$2b$12$QQ5Oo5WOjfZ8Qglg2KN.r.6nbCH5no9T3ByaLQptTe1aMLTijcSKW', TRUE, TRUE)
ON DUPLICATE KEY UPDATE 
    email='sashy@flabs2fabs.app',
    hashed_password='$2b$12$QQ5Oo5WOjfZ8Qglg2KN.r.6nbCH5no9T3ByaLQptTe1aMLTijcSKW',
    is_admin=TRUE,
    is_active=TRUE;
"""

# Execute SQL
result = subprocess.run(
    ["sudo", "mariadb", "-u", "root", "-pWelcome2026", "flab2fabs", "-e", sql],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("✓ Admin user created/updated successfully!")
    print("Username: admin")
    print("Password: admin123")
else:
    print(f"✗ Error: {result.stderr}")
