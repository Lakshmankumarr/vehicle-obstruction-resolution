"""
Tests for ALPR pipeline, image preprocessing, and fallback behavior.
"""
from fastapi import status


def test_alpr_scan_fallback_mode(client):
    """Tests ALPR scan endpoint with a dummy base64 image."""
    tiny_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    payload = {"image": tiny_base64}
    response = client.post("/api/v1/alpr/scan", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["primaryPlate"] is not None
    assert data["maskedPlate"] is not None
    assert data["confidence"] > 0


def test_alpr_image_size_limit_rejection(client):
    """
    Tests that images exceeding MAX_IMAGE_SIZE_MB (10MB) are rejected.
    Fixes Section 99 Issue 31.
    """
    # 15MB of base64 data decodes to ~11.25MB (strictly > 10MB)
    large_payload = {"image": "A" * (15 * 1024 * 1024)}
    response = client.post("/api/v1/alpr/scan", json=large_payload)
    data = response.json()
    assert data["success"] is False
    assert "exceeds maximum size limit" in data["message"]
