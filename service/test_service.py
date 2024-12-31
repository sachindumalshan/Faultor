import subprocess

def check_service_status(service_name):
    try:
        result = subprocess.run(["systemctl","is-active",service_name],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
        )
        status = result.stdout.strip()
        if status == "active":
            print(f"{service_name} is running")
        else:
            print(f"{service_name} is NOT running")
    except Exception as e:
        print(f"Error checking status for {service_name}: {e}")

services = ["dummy_service1","dummy_service2"]
for service in services:
    check_service_status(service)
