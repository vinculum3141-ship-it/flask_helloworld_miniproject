"""Test Secret integration with pods."""
import base64
import pytest

from .utils import get_pods, exec_in_pod, get_secret, get_deployment


def test_secret_exists():
    """Verify that the Secret resource exists in the cluster."""
    secret = get_secret("hello-secrets")
    
    assert secret is not None, "Secret 'hello-secrets' does not exist in the cluster"
    assert secret["kind"] == "Secret", "Resource is not a Secret"
    assert secret["metadata"]["name"] == "hello-secrets", "Secret has wrong name"
    assert secret["type"] == "Opaque", "Secret should be of type Opaque"
    
    print("✓ Secret 'hello-secrets' exists")


def test_secret_has_correct_keys():
    """Verify that the Secret contains the expected keys."""
    secret = get_secret("hello-secrets")
    
    assert secret is not None, "Secret 'hello-secrets' not found"
    
    data = secret.get("data", {})
    
    # Check expected keys exist
    expected_keys = ["API_KEY", "DB_PASSWORD"]
    for key in expected_keys:
        assert key in data, f"Secret missing expected key: {key}"
    
    print(f"✓ Secret has correct keys: {list(data.keys())}")


def test_secret_values_are_base64_encoded():
    """Verify that Secret values are properly base64-encoded."""
    secret = get_secret("hello-secrets")
    
    assert secret is not None, "Secret 'hello-secrets' not found"
    
    data = secret.get("data", {})
    
    # Test each value can be decoded from base64
    expected_decoded_values = {
        "API_KEY": "somesecretkey",
        "DB_PASSWORD": "password123"
    }
    
    for key, expected_decoded in expected_decoded_values.items():
        assert key in data, f"Secret missing key: {key}"
        
        encoded_value = data[key]
        
        # Verify it's valid base64
        try:
            decoded_value = base64.b64decode(encoded_value).decode('utf-8')
        except Exception as e:
            pytest.fail(f"Failed to decode {key} from base64: {e}")
        
        # Verify decoded value matches expected
        assert decoded_value == expected_decoded, \
            f"Expected {key} to decode to '{expected_decoded}', got '{decoded_value}'"
    
    print(f"✓ All Secret values are correctly base64-encoded")


def test_deployment_references_secret():
    """Verify that the deployment references the Secret correctly."""
    deployment = get_deployment("hello-flask")
    
    assert deployment is not None, "Deployment 'hello-flask' not found"
    
    containers = deployment["spec"]["template"]["spec"]["containers"]
    assert len(containers) > 0, "No containers found in deployment"
    
    main_container = containers[0]
    env_from = main_container.get("envFrom", [])
    
    # Check that envFrom includes secretRef to hello-secrets
    secret_refs = [
        ref for ref in env_from 
        if "secretRef" in ref and ref["secretRef"]["name"] == "hello-secrets"
    ]
    
    assert len(secret_refs) > 0, \
        "Deployment does not reference Secret 'hello-secrets' in envFrom"
    
    print("✓ Deployment correctly references Secret 'hello-secrets'")


def test_secret_applied(pods):
    """Verify that Secret environment variables are applied to pods."""
    assert len(pods) > 0, "No pods found to test Secret"
    
    pod_name = pods[0]["metadata"]["name"]
    
    # Execute printenv in the pod to check API_KEY variable
    result = exec_in_pod(pod_name, ["printenv", "API_KEY"])
    env_value = result.stdout.strip()
    
    # The value in the pod should be decoded (not base64)
    assert env_value == "somesecretkey", \
        f"Expected API_KEY='somesecretkey', got '{env_value}'"
    
    print(f"✓ Secret applied: API_KEY={env_value}")


def test_all_secret_values_in_pods(pods):
    """Verify that all Secret values are correctly injected into pods (decoded)."""
    assert len(pods) > 0, "No pods found to test Secret"
    
    pod_name = pods[0]["metadata"]["name"]
    
    # Test all expected environment variables (should be decoded in pod)
    expected_env_vars = {
        "API_KEY": "somesecretkey",
        "DB_PASSWORD": "password123"
    }
    
    for env_var, expected_value in expected_env_vars.items():
        result = exec_in_pod(pod_name, ["printenv", env_var])
        actual_value = result.stdout.strip()
        
        assert actual_value == expected_value, \
            f"Expected {env_var}='{expected_value}', got '{actual_value}'"
    
    print(f"✓ All Secret values correctly injected into pods (decoded): {list(expected_env_vars.keys())}")
