import re
import sys


def read_config_file(config_file):
    with open(config_file, "r") as file:
        lines = file.readlines()

    variables = []
    current_variable = ""

    for line in lines:
        if re.match(r"\[.*\]", line):
            variables.append(current_variable)

            current_variable = ""
        elif line.strip() == "":
            continue
        else:
            current_variable += "\n" + line

    variables.append(current_variable)

    return variables


def get_hosts(public_ip_variables, private_ip_variables):
    git_hosts = [
        f"--add-host git-server-{get_uuid(re.search(r'hostname = (.*)', variable).group(1), private_ip_variables)}:"
        f"{re.search(r'ipv4 = (.*)', variable).group(1).replace(' ', '')}"
        for variable in public_ip_variables
        if "git-server = true" in variable
    ]

    storage_hosts = [
        f"--add-host storage-server-{get_uuid(re.search(r'hostname = (.*)', variable).group(1), private_ip_variables)}:"
        f"{re.search(r'ipv4 = (.*)', variable).group(1).replace(' ', '')}"
        for variable in public_ip_variables
        if "storage-server = true" in variable
    ]

    hosts = git_hosts + storage_hosts

    return " ".join(hosts)


def get_uuid(hostname, private_ip_variables):
    for variable in private_ip_variables:
        hostname_match = re.search(r"hostname = (.*)", variable)
        uuid_match = re.search(r"uuid = (.*)", variable)

        if hostname_match and uuid_match:
            if hostname_match.group(1) == hostname:
                return uuid_match.group(1)

    return None


def main():
    if len(sys.argv) != 3:
        print(
            "Usage: python load-test-get-cluster-hosts.py <public_ip_config_file> <private_ip_config_file>"
        )
        sys.exit(1)

    public_ip_config_file = sys.argv[1]
    private_ip_config_file = sys.argv[2]

    public_ip_config_variables = read_config_file(public_ip_config_file)
    private_ip_config_variables = read_config_file(private_ip_config_file)
    hosts = get_hosts(public_ip_config_variables, private_ip_config_variables)

    print(hosts)


if __name__ == "__main__":
    main()
