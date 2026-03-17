import secrets
import string

def generate_secret_key(length=64):
    """Generate a secure random secret key"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_jwt_secret(length=32):
    """Generate a secure random JWT secret"""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    jwt_secret = generate_jwt_secret()
    
    print("=" * 50)
    print("GENERATED SECRET KEYS - COPY THESE TO YOUR .env FILE")
    print("=" * 50)
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SECRET_KEY={jwt_secret}")
    print("=" * 50)
    print("\n⚠️  IMPORTANT: Save these keys securely and never share them!")