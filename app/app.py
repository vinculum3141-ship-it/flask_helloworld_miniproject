"""
This code defines a simple web application using Flask.
It creates a single route at the root URL ("/") that returns the message "Hello from Flask on Kubernetes (Minikube)!".
When run directly, it starts a web server listening on all network interfaces at port 5000.
This is typically used as a minimal example for deploying Flask apps, such as in a Kubernetes environment.
"""

import werkzeug
from flask import Flask, jsonify

# Compatibility shim: Werkzeug 3.x removed the `__version__` attribute that
# older Flask test utilities reference. Provide a fallback so tests and
# the Flask test client keep working when Werkzeug 3.x is installed.
if not hasattr(werkzeug, "__version__"):
    # set a reasonable default version string used only for compatibility checks
    werkzeug.__version__ = "3.0.0"


app = Flask(__name__)

@app.route("/")
def hello():
    return jsonify(message="Hello from Flask on Kubernetes (Minikube)!")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
