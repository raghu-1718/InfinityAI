import subprocess

def run_trivy_scan(image_name):
    result = subprocess.run(["trivy", "image", image_name], capture_output=True, text=True)
    print(result.stdout)

def run_snyk_scan(path):
    result = subprocess.run(["snyk", "test", path], capture_output=True, text=True)
    print(result.stdout)
