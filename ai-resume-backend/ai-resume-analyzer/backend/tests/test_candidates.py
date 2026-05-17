import pytest


@pytest.mark.asyncio
async def test_create_candidate(client, auth_headers):
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "current_title": "Software Engineer",
        "skills": ["Python", "FastAPI", "MongoDB"],
    }
    response = await client.post("/api/v1/candidates", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "jane.doe@example.com"
    assert "id" in data
    return data["id"]


@pytest.mark.asyncio
async def test_list_candidates(client, auth_headers):
    response = await client.get("/api/v1/candidates", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_duplicate_email_rejected(client, auth_headers):
    payload = {
        "first_name": "Duplicate",
        "last_name": "User",
        "email": "jane.doe@example.com",
    }
    response = await client.post("/api/v1/candidates", json=payload, headers=auth_headers)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_update_candidate_status(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/candidates",
        json={"first_name": "Bob", "last_name": "Smith", "email": "bob.status@test.com"},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    cid = create_resp.json()["id"]

    update_resp = await client.patch(
        f"/api/v1/candidates/{cid}/status",
        json={"status": "shortlisted"},
        headers=auth_headers,
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["status"] == "shortlisted"


@pytest.mark.asyncio
async def test_delete_candidate(client, auth_headers):
    create_resp = await client.post(
        "/api/v1/candidates",
        json={"first_name": "Delete", "last_name": "Me", "email": "delete.me@test.com"},
        headers=auth_headers,
    )
    cid = create_resp.json()["id"]
    del_resp = await client.delete(f"/api/v1/candidates/{cid}", headers=auth_headers)
    assert del_resp.status_code == 204
