import bcrypt

# Hash a password
password = "Welcome2026!".encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(f"Hashed password: {hashed.decode('utf-8')}")

# Test verification
test_password = "password123".encode('utf-8')
if bcrypt.checkpw(test_password, hashed):
    print("✓ Password verification works!")
else:
    print("✗ Password verification failed")
