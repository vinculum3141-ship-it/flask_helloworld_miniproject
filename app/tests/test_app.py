from app import app

def test_home():
    client = app.test_client()
    response = client.get('/')
    assert response.status_code == 200
    # The Flask view now returns JSON. Check the content type and JSON payload.
    assert response.content_type == "application/json"
    assert response.get_json() == {"message": "Hello from Flask on Kubernetes (Minikube)!"}
