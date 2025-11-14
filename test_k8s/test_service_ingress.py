"""
Test service accessibility via Ingress.

This test verifies that the Flask application can be reached through
an Ingress resource (for ClusterIP service type).
"""
import requests
import pytest

from .utils import get_service, get_ingress, get_minikube_ip, is_ci_environment


def get_ingress_url_and_host(ingress):
    """
    Get URL and host header from Ingress resource.
    
    In CI/CD environments, uses Minikube IP directly.
    In local development, uses the ingress hostname.
    
    Returns:
        tuple: (url, host_header) where host_header is the Host header to use
    """
    rules = ingress.get("spec", {}).get("rules", [])
    if not rules:
        return None, None
    
    # Get the configured hostname from ingress rules
    ingress_host = rules[0].get("host", "hello-flask.local")
    
    # In CI/CD: Use Minikube IP instead of hostname (DNS won't resolve)
    if is_ci_environment():
        print("Detected CI environment - using Minikube IP instead of hostname")
        minikube_ip = get_minikube_ip()
        
        if minikube_ip:
            print(f"Using Minikube IP: {minikube_ip} with Host header: {ingress_host}")
            # Return IP-based URL but also return the host header to use
            return f"http://{minikube_ip}", ingress_host
        else:
            print("Warning: Could not get Minikube IP, falling back to hostname")
    
    # Local development: Use the ingress hostname
    print(f"Using Ingress hostname: {ingress_host}")
    return f"http://{ingress_host}", ingress_host


@pytest.mark.ingress
def test_service_is_clusterip(service):
    """Verify that the service is configured as ClusterIP when using Ingress."""
    service_type = service["spec"]["type"]
    
    if service_type != "ClusterIP":
        pytest.skip(
            f"Service type is '{service_type}', not 'ClusterIP'. "
            f"This test assumes ClusterIP with Ingress."
        )
    
    print(f"✓ Service type: {service_type} (using Ingress for external access)")


@pytest.mark.ingress
def test_ingress_service_reachable(service, ingress, k8s_timeouts):
    """
    Test that the service is reachable via Ingress.
    
    This test supports both CI/CD (using Minikube IP) and local environments
    (using /etc/hosts entries).
    """
    service_type = service["spec"]["type"]
    
    if service_type != "ClusterIP":
        pytest.skip(f"Service type is '{service_type}', expected 'ClusterIP' for Ingress test")
    
    print(f"Testing Ingress service accessibility...")
    
    # Get URL and Host header from Ingress
    url, host_header = get_ingress_url_and_host(ingress)
    
    assert url, (
        "No valid Ingress URL could be determined. "
        "Ensure Ingress resource is deployed and configured correctly."
    )
    
    print(f"Ingress URL: {url}")
    
    # Prepare headers
    headers = {}
    if host_header and not url.endswith(host_header):
        headers['Host'] = host_header
        print(f"Setting Host header: {host_header}")
    
    # Test the URL
    timeout = k8s_timeouts.get('http_request', 5)
    
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        assert resp.status_code == 200, \
            f"Unexpected status {resp.status_code} from {url}"
        assert "Hello" in resp.text, \
            f"Expected 'Hello' in response from {url}"
        
        print(f"✓ Service is reachable via Ingress at {url}")
        print(f"✓ Response: {resp.text[:100]}...")
        
    except requests.exceptions.RequestException as e:
        pytest.fail(
            f"Failed to reach service at {url}. "
            f"Error: {e}. "
            f"If using Ingress, ensure: 1) Ingress controller is running, "
            f"2) /etc/hosts is configured (local) or Minikube IP is accessible (CI), "
            f"3) Ingress resource is deployed."
        )


@pytest.mark.ingress
def test_ingress_points_to_correct_service(ingress, service_name):
    """Verify that the Ingress routes to the correct service."""
    rules = ingress.get("spec", {}).get("rules", [])
    assert len(rules) > 0, "Ingress has no rules defined"
    
    # Check the backend service name
    paths = rules[0].get("http", {}).get("paths", [])
    assert len(paths) > 0, "Ingress rule has no paths"
    
    backend = paths[0].get("backend", {})
    backend_service_name = backend.get("service", {}).get("name")
    
    assert backend_service_name == service_name, \
        f"Ingress backend points to '{backend_service_name}', expected '{service_name}'"
    
    print(f"✓ Ingress correctly routes to service '{service_name}'")
