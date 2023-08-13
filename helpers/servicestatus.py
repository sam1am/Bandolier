import subprocess

def get_services():
    output = subprocess.check_output(['systemctl', 'list-unit-files', '--type=service'], universal_newlines=True)
    services = [line.split()[0] for line in output.split('\n') if line.startswith(('bandolier', 'boring'))]
    return services

def show_service_status(service):
    try:
        output = subprocess.check_output(['systemctl', 'is-active', service], universal_newlines=True)
        print(f"Service {service} is {output.strip()}")
        show_service_port(service)
    except subprocess.CalledProcessError as e:
        print(f"Error getting status for {service}: {str(e)}")

def show_service_port(service):
    try:
        output = subprocess.check_output(['sudo', 'netstat', '-tulpn'], universal_newlines=True)
        for line in output.split('\n'):
            if service in line:
                print(f"Service {service} is using: {line.strip().split()[-1]}")
    except subprocess.CalledProcessError as e:
        print(f"Error getting port for {service}: {str(e)}")

def main():
    services = get_services()
    for service in services:
        show_service_status(service)

if __name__ == "__main__":
    main()
