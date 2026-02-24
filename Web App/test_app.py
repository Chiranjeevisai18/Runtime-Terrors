"""Quick integration test for Gruha Alankara.
Uses an isolated in-memory SQLite database so tests are
self-contained and never conflict with production data.
"""
from app import create_app

# Create app with an isolated in-memory database
app = create_app(test_config={
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    'WTF_CSRF_ENABLED': False,
    'TESTING': True,
})

client = app.test_client()

print("=" * 50)
print("  Gruha Alankara - Integration Test")
print("=" * 50)

# Test landing page
r = client.get('/')
assert r.status_code == 200, f"Landing page returned {r.status_code}"
data = r.data.decode('utf-8')
assert 'gradient-text' in data, "Landing page missing gradient-text"
assert 'navbar' in data, "Landing page missing navbar"
assert 'features-grid' in data, "Landing page missing features-grid"
print("[OK] Landing page loads correctly")

# Test login page
r = client.get('/login')
assert r.status_code == 200, f"Login page returned {r.status_code}"
assert 'Sign In' in r.data.decode('utf-8'), "Login page missing Sign In"
print("[OK] Login page loads correctly")

# Test register page
r = client.get('/register')
assert r.status_code == 200, f"Register page returned {r.status_code}"
assert 'Create Account' in r.data.decode('utf-8'), "Register page missing Create Account"
print("[OK] Register page loads correctly")

# Test registration
r = client.post('/register', data={
    'username': 'testuser',
    'email': 'test@test.com',
    'password': 'test123',
    'confirm_password': 'test123'
})
assert r.status_code == 302, f"Registration returned {r.status_code} (expected 302 redirect to login)"
print("[OK] Registration works correctly")

# Test login
r = client.post('/login', data={
    'email': 'test@test.com',
    'password': 'test123'
}, follow_redirects=True)
assert r.status_code == 200, f"Login returned {r.status_code}"
assert 'My Designs' in r.data.decode('utf-8'), "Dashboard missing My Designs after login"
print("[OK] Login works correctly")

# Test dashboard
r = client.get('/dashboard')
assert r.status_code == 200, f"Dashboard returned {r.status_code}"
assert 'designs-grid' in r.data.decode('utf-8'), "Dashboard missing designs-grid"
print("[OK] Dashboard loads correctly")

# Test upload page
r = client.get('/upload')
assert r.status_code == 200, f"Upload page returned {r.status_code}"
assert 'faces-grid' in r.data.decode('utf-8'), "Upload page missing faces-grid"
print("[OK] Upload page loads correctly")

# Test API: models list
r = client.get('/api/models')
assert r.status_code == 200, f"API /models returned {r.status_code}"
data = r.get_json()
assert data is not None, "API /models returned no JSON"
assert 'sofa' in data, "API /models missing sofa"
assert 'table' in data, "API /models missing table"
assert 'bed' in data, "API /models missing bed"
assert len(data) >= 10, f"API /models only has {len(data)} types"
print(f"[OK] API /models returns {len(data)} furniture types")

# Test logout
r = client.get('/logout')
assert r.status_code == 302, f"Logout returned {r.status_code} (expected 302)"
print("[OK] Logout works correctly")

# Protected route redirect
r = client.get('/dashboard')
assert r.status_code == 302, f"Protected dashboard returned {r.status_code} (expected 302)"
print("[OK] Protected routes redirect unauthenticated users")

print()
print("=" * 50)
print("  ALL TESTS PASSED")
print("=" * 50)
