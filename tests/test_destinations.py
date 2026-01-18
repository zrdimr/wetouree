import pytest

def test_create_destination(client):
    response = client.post(
        "/destinations/",
        json={
            "name": "Test Island",
            "description": "A beautiful test island.",
            "type": "alam",
            "capacity": 100,
            "latitude": -5.0,
            "longitude": 106.0
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Island"
    assert "id" in data

def test_get_destinations(client):
    # Create one first
    client.post(
        "/destinations/",
        json={
            "name": "Island A",
            "description": "Desc A",
            "type": "alam",
            "capacity": 50,
            "latitude": -5.1,
            "longitude": 106.1
        },
    )
    response = client.get("/destinations/")
    assert response.status_code == 200
    assert len(response.json()) >= 1

def test_get_single_destination(client):
    create_res = client.post(
        "/destinations/",
        json={
            "name": "Island B",
            "description": "Desc B",
            "type": "budaya",
            "capacity": 20,
            "latitude": -5.2,
            "longitude": 106.2
        },
    )
    dest_id = create_res.json()["id"]
    
    response = client.get(f"/destinations/{dest_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Island B"

def test_delete_destination(client):
    create_res = client.post(
        "/destinations/",
        json={"name": "To Delete", "description": "X", "type": "alam", "capacity": 10, "latitude": 0, "longitude": 0},
    )
    dest_id = create_res.json()["id"]
    
    response = client.delete(f"/destinations/{dest_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_res = client.get(f"/destinations/{dest_id}")
    assert get_res.status_code == 404
