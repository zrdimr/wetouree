import pytest

def test_user_registration(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123",
            "name": "Test User",
            "phone": "0899"
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_user_login(client):
    # 1. Register
    client.post(
        "/users/register",
        json={"username": "loginuser", "email": "l@ex.com", "password": "pass", "name": "N", "phone": "P"},
    )
    
    # 2. Login
    response = client.post(
        "/users/login",
        json={"username": "loginuser", "password": "pass"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "user" in response.json()

def test_login_invalid_password(client):
    client.post(
        "/users/register",
        json={"username": "wrongpass", "email": "w@ex.com", "password": "correct", "name": "N", "phone": "P"},
    )
    response = client.post(
        "/users/login",
        json={"username": "wrongpass", "password": "wrong"},
    )
    assert response.status_code == 401
    assert "Username atau password salah" in response.json()["detail"]

def test_update_user(client):
    # 1. Register
    reg_res = client.post(
        "/users/register",
        json={"username": "updateuser", "email": "u@ex.com", "password": "pass", "name": "Old Name", "phone": "P"},
    )
    user_id = reg_res.json()["id"]
    
    # 2. Update
    response = client.put(
        f"/users/{user_id}",
        json={"name": "New Name", "phone": "0000"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"

def test_update_user_role(client):
    # 1. Register
    reg_res = client.post(
        "/users/register",
        json={"username": "roleuser", "email": "r@ex.com", "password": "pass", "name": "N", "phone": "P"}
    )
    user_id = reg_res.json()["id"]
    
    # 2. Update Role
    response = client.put(
        f"/users/{user_id}/role",
        json={"role": "area_manager", "assigned_area": "Test Area"}
    )
    assert response.status_code == 200
    assert response.json()["role"] == "area_manager"
    assert response.json()["assigned_area"] == "Test Area"
