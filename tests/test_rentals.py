import pytest

def test_create_equipment(client):
    response = client.post(
        "/rentals/equipment",
        json={
            "name": "Test Tent",
            "description": "Standard 4P Tent",
            "category": "tent",
            "price_per_day": 50000,
            "stock": 5
        },
    )
    assert response.status_code == 200
    assert response.json()["available"] == 5

def test_rental_flow(client):
    # 1. Create equipment
    eq_res = client.post(
        "/rentals/equipment",
        json={
            "name": "Rent Tent",
            "description": "Durable",
            "category": "tent",
            "price_per_day": 100000,
            "stock": 10
        },
    )
    eq_id = eq_res.json()["id"]
    
    # 2. Create rental
    rental_res = client.post(
        "/rentals/",
        json={
            "equipment_id": eq_id,
            "customer_name": "John Doe",
            "customer_phone": "0812",
            "rental_date": "2026-01-20",
            "return_date": "2026-01-22",
            "quantity": 2
        },
    )
    assert rental_res.status_code == 200
    # 2 days (20 to 22) * 100000 * 2 = 400000
    assert rental_res.json()["total_price"] == 400000
    
    # 3. Check inventory reduced
    eq_get = client.get("/rentals/equipment")
    for item in eq_get.json():
        if item["id"] == eq_id:
            assert item["available"] == 8

def test_insufficient_stock(client):
    eq_res = client.post(
        "/rentals/equipment",
        json={"name": "Rare", "description": "X", "category": "tent", "price_per_day": 1, "stock": 1},
    )
    eq_id = eq_res.json()["id"]
    
    rental_res = client.post(
        "/rentals/",
        json={
            "equipment_id": eq_id,
            "customer_name": "Fail",
            "customer_phone": "0",
            "rental_date": "2026-01-01",
            "return_date": "2026-01-02",
            "quantity": 5
        },
    )
    assert rental_res.status_code == 400
    assert "Not enough equipment available" in rental_res.json()["detail"]
