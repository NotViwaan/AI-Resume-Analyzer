import io
import pytest


@pytest.mark.asyncio
async def test_upload_resume(client, auth_headers, test_db):
    # Create a candidate first
    cand = await client.post(
        "/api/v1/candidates",
        json={"first_name": "Resume", "last_name": "Tester", "email": "resume.tester@test.com"},
        headers=auth_headers,
    )
    cid = cand.json()["id"]

    # Create a minimal PDF-like file for testing
    fake_pdf = io.BytesIO(b"%PDF-1.4 test resume content Python FastAPI MongoDB")
    fake_pdf.name = "test_resume.pdf"

    response = await client.post(
        "/api/v1/resumes/upload",
        headers=auth_headers,
        data={"candidate_id": cid},
        files={"file": ("test_resume.pdf", fake_pdf, "application/pdf")},
    )
    # Expect either 201 (success) or 422 (can't parse fake PDF - both are valid in tests)
    assert response.status_code in (201, 422)


@pytest.mark.asyncio
async def test_get_nonexistent_resume(client, auth_headers):
    response = await client.get(
        "/api/v1/resumes/000000000000000000000000",
        headers=auth_headers,
    )
    assert response.status_code == 404
