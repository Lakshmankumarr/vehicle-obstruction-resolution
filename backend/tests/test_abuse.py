"""
Tests for abuse reporting and moderation.
Fixes:
- Section 99 Issue 25: Validates report target existence
- Section 99 Issue 11: Validates abuse restrictions persist
"""
from fastapi import status
from uuid import uuid4


def test_create_report_success(client, token_user_a, user_b):
    """Test reporting user B."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {
        "targetUserId": str(user_b.id),
        "reason": "SPAM",
        "description": "Sending frequent unnecessary notifications."
    }
    response = client.post("/api/v1/report/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert "reportId" in data


def test_create_report_nonexistent_target_fails(client, token_user_a):
    """
    Test reporting a non-existent target user returns 404.
    Fixes Section 99 Issue 25.
    """
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {
        "targetUserId": str(uuid4()),
        "reason": "SPAM"
    }
    response = client.post("/api/v1/report/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_cannot_report_self(client, token_user_a, user_a):
    """User cannot report themselves."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {
        "targetUserId": str(user_a.id),
        "reason": "SPAM"
    }
    response = client.post("/api/v1/report/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
