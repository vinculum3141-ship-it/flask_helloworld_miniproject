import subprocess
import requests
import time

def test_service_reachable():
    """Ensure the exposed service URL is responding."""
    # Try a few times to get a non-empty URL from minikube (sometimes it takes a moment to be ready)
    url = ""
    for i in range(5):
        proc = subprocess.run(
            ["minikube", "service", "hello-flask", "--url"],
            capture_output=True, text=True
        )
        url = proc.stdout.strip()
        if url:
            break
        time.sleep(1)

    assert url, (
        "minikube returned an empty URL for service 'hello-flask'. "
        f"stdout={{proc.stdout!r}} stderr={{proc.stderr!r}} returncode={{proc.returncode}}"
    )

    # Ensure the URL includes a scheme
    assert url.startswith(("http://", "https://")), f"Service URL does not include scheme: {{url!r}}"

    resp = requests.get(url, timeout=5)
    assert resp.status_code == 200, f"Unexpected status {{resp.status_code}} from {{url}}"
    assert "Hello" in resp.text
