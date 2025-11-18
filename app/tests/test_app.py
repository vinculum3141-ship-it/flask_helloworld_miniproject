"""
Unit tests for the Flask application.

This module contains unit tests that validate the core functionality of the Flask
application, including:

- HTTP response validation: Ensures the root endpoint returns 200 OK status
- Content validation: Verifies the response body contains the expected JSON message
- Performance testing: Validates that the application responds within acceptable latency (<1s)
- Error handling: Tests that invalid routes properly return 404 Not Found status

Test Scenarios:
    1. test_home_returns_200_ok(): Validates that GET request to '/' returns 200 OK status
    2. test_home_response_content(): Verifies the response contains the expected JSON message
    3. test_response_latency(): Ensures app responds within 1 second
    4. test_invalid_route_returns_404(): Verifies 404 status for non-existent routes

Fixtures:
    - client: Flask test client for making requests
    - home_response: Response object from GET request to '/'

Usage:
    Run tests using pytest:
        $ pytest app/tests/test_app.py -v
    
    Or using the Makefile:
        $ make unit-tests
"""

import time
import pytest
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture
def home_response(client):
    """Get the response from the home route."""
    return client.get('/')


def test_home_returns_200_ok(home_response):
    """Test that HTTP GET to / returns 200 OK status."""
    assert home_response.status_code == 200


def test_home_response_content(home_response):
    """Test that the response body contains the expected JSON message."""
    # The Flask view now returns JSON. Check the content type and JSON payload.
    assert home_response.content_type == "application/json"
    assert home_response.get_json() == {"message": "Hello from Flask on Kubernetes (Minikube)!"}


def test_response_latency(client):
    """Test that the app responds within acceptable latency (< 1 second)."""
    start_time = time.time()
    response = client.get('/')
    end_time = time.time()
    
    latency = end_time - start_time
    assert response.status_code == 200
    assert latency < 1.0, f"Response took {latency:.3f}s, expected < 1.0s"


def test_invalid_route_returns_404(client):
    """Test that invalid routes return 404 Not Found."""
    # Test various invalid routes
    invalid_routes = [
        '/invalid',
        '/nonexistent',
        '/api/unknown',
        '/random/path'
    ]
    
    for route in invalid_routes:
        response = client.get(route)
        assert response.status_code == 404, f"Route {route} should return 404, got {response.status_code}"
