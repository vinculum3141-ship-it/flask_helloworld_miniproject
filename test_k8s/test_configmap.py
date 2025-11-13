import subprocess

def test_configmap_applied():
    pod = subprocess.getoutput("minikube kubectl -- get pods -l app=hello-flask -o jsonpath='{.items[0].metadata.name}'")
    env = subprocess.getoutput(f"minikube kubectl -- exec {pod} -- printenv APP_ENV")
    assert env.strip() == "local"
