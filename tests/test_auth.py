def test_signup_and_login(client):
    r = client.post("/auth/signup", json={"email": "a@b.com", "password": "pass1234"})
    assert r.status_code == 201

    r = client.post("/auth/login", json={"email": "a@b.com", "password": "pass1234"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_login_wrong_password(client):
    client.post("/auth/signup", json={"email": "c@d.com", "password": "pass1234"})
    r = client.post("/auth/login", json={"email": "c@d.com", "password": "wrong"})
    assert r.status_code == 401

def test_me_requires_token(client):
    r = client.get("/me")
    assert r.status_code == 401