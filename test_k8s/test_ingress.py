import subprocess
import json
import time

def test_ingress_exists():
    """Check that Ingress resource exists."""
    result = subprocess.run(
        ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
        capture_output=True, text=True
    )
    
    # If ingress doesn't exist, skip this test
    if result.returncode != 0:
        import pytest
        pytest.skip("Ingress not deployed. This test only runs when using Ingress setup.")
    
    ingress_data = json.loads(result.stdout)
    assert ingress_data.get("metadata", {}).get("name") == "hello-flask-ingress"
    print("✓ Ingress resource 'hello-flask-ingress' exists")

def test_ingress_has_rules():
    """Check that Ingress has proper routing rules."""
    result = subprocess.run(
        ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        import pytest
        pytest.skip("Ingress not deployed.")
    
    ingress_data = json.loads(result.stdout)
    rules = ingress_data.get("spec", {}).get("rules", [])
    
    assert len(rules) > 0, "Ingress has no rules defined"
    
    # Check first rule has a host
    first_rule = rules[0]
    assert "host" in first_rule, "Ingress rule missing host"
    
    # Check rule has http paths
    paths = first_rule.get("http", {}).get("paths", [])
    assert len(paths) > 0, "Ingress rule has no paths"
    
    # Check path points to hello-flask service
    backend = paths[0].get("backend", {})
    service_name = backend.get("service", {}).get("name")
    assert service_name == "hello-flask", f"Expected service 'hello-flask', got '{service_name}'"
    
    print(f"✓ Ingress routes {first_rule.get('host')} → hello-flask service")

def test_ingress_has_address():
    """Check that Ingress has been assigned an address.
    
    This indicates the Ingress controller is working and has processed the resource.
    """
    result = subprocess.run(
        ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        import pytest
        pytest.skip("Ingress not deployed.")
    
    ingress_data = json.loads(result.stdout)
    
    # Wait up to 30 seconds for address to be assigned
    max_wait = 30
    for i in range(max_wait):
        result = subprocess.run(
            ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
            capture_output=True, text=True
        )
        ingress_data = json.loads(result.stdout)
        
        # Check for address in status
        load_balancer = ingress_data.get("status", {}).get("loadBalancer", {})
        ingress_list = load_balancer.get("ingress", [])
        
        if ingress_list and len(ingress_list) > 0:
            address = ingress_list[0].get("ip") or ingress_list[0].get("hostname")
            if address:
                print(f"✓ Ingress has address: {address}")
                return
        
        if i < max_wait - 1:
            time.sleep(1)
    
    # If we get here, no address was assigned
    raise AssertionError(
        "Ingress has no address assigned after 30 seconds. "
        "This may indicate the Ingress controller is not running. "
        "For Minikube, run: minikube addons enable ingress"
    )

def test_ingress_class():
    """Verify Ingress has the correct ingress class annotation."""
    result = subprocess.run(
        ["kubectl", "get", "ingress", "hello-flask-ingress", "-o", "json"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        import pytest
        pytest.skip("Ingress not deployed.")
    
    ingress_data = json.loads(result.stdout)
    annotations = ingress_data.get("metadata", {}).get("annotations", {})
    
    ingress_class = (
        annotations.get("kubernetes.io/ingress.class") or
        ingress_data.get("spec", {}).get("ingressClassName")
    )
    
    assert ingress_class in ["nginx", "alb"], (
        f"Unexpected ingress class: {ingress_class}. "
        f"Expected 'nginx' (Minikube) or 'alb' (EKS)"
    )
    
    print(f"✓ Ingress class: {ingress_class}")
