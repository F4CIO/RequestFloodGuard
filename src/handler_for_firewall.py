from ipaddress import IPv4Address

import handler_for_cmd
import cs_firewall_log_analyzer



def rule_exists(name: str) -> bool:
    """
    Uses `netsh advfirewall firewall show rule`
    Returns True if the rule is present, False otherwise.
    """
    cmd = [
        "netsh", "advfirewall", "firewall",
        "show", "rule",
        f"name={name}"
    ]
    output = handler_for_cmd.run_command(cmd, True)
    return "No rules match" not in output

def create_rule(firewall_rule_creation_command: str, log: cs_firewall_log_analyzer.handler_for_CsLog.CsLog = None, extra_args: list = None) -> None:
    """
    Uses `netsh advfirewall firewall add rule ...` to create the block rule.
    """
    # cmd = [
    #     "netsh", "advfirewall", "firewall",
    #     "add", "rule",
    #     f"name={name}",
    #     "description=http://www.f4cio.com/RequestFloodGuard",
    #     "dir=in",
    #     "action=block",
    #     "localip=any",
    #     "remoteip=255.255.255.254",
    #     "protocol=any",
    #     "profile=domain,private,public",
    #     "interfacetype=any",
    #     "enable=yes",
    #     "edge=no",            # edge traversal disabled
    #     "security=notrequired"
    # ]
    cmd = firewall_rule_creation_command.split()
    
    output = handler_for_cmd.run_command(cmd, False)

    if output.startswith('Ok.'):
        log.add_line(f"Rule created successfully.")
    else:
        log.add_line(f"ERROR: Failed to create rule. Output: {output}")
  
def get_firewall_rule_details(rule_name: str) -> str:
    """
    Runs the netsh command to show a firewall rule and returns its output as a string.

    :param rule_name: The exact name of the firewall rule, e.g. "CraftSynth.RequestFloodGuard"
    :return: The full command output (stdout + stderr) as one string.
    :raises RuntimeError: If the command fails (non-zero exit code).
    """
    # Build the command; note how we wrap the rule name in quotes
    cmd = [
        "netsh", "advfirewall", "firewall", "show", "rule",
        f'name={rule_name}',  # netsh expects name=<rule_name>
        "verbose"
    ]

    return handler_for_cmd.run_command(cmd)

def get_remote_ips_from_firewall_rule(rule_name: str, log: cs_firewall_log_analyzer.handler_for_CsLog.CsLog) -> None:
    r = [] 
    
    try:
        output = get_firewall_rule_details(rule_name)
        log.add_line("Firewall rule output:")
        log.add_line(output)

        # Here you should parse the output and extract the remote IPs but parse both ip ranges notation, single ip and CIDR notation
        # for example output like "RemoteIP: 192.168.1.1,5.5.5.5/32,6.6.6.6-6.6.6.8" and then extract the IPs or ranges into array of single ips
        for line in output.splitlines():
            if "RemoteIP:" in line:
                # Extract the part after "RemoteIP:"
                ips_part = line.split("RemoteIP:")[1].strip()
                r = csv_to_ips(ips_part, log)

    except RuntimeError as e:
        log.add_line("Error retrieving firewall rule:")
        log.add_line(str(e))

    r = list(set(r))  # Remove duplicates
    # Sort the IPs using IPv4Address for correct order
    r = sorted(r, key=lambda ip: IPv4Address(ip))
    return r

def csv_to_ips(ips_csv: str, log: cs_firewall_log_analyzer.handler_for_CsLog.CsLog) -> list:
    # Split by comma to get individual IPs or ranges
    r = []
    csv_items = ips_csv.split(',')
    for ip in csv_items:
        ip = ip.strip()
        if '/' in ip:  # CIDR notation
            base_ip, cidr = ip.split('/')
            base_parts = list(map(int, base_ip.split('.')))
            cidr = int(cidr)
            if cidr == 24:
                for i in range(1, 255):
                    r.append(f"{base_parts[0]}.{base_parts[1]}.{base_parts[2]}.{i}")
            elif cidr == 32:
                r.append(base_ip)
        elif '-' in ip:  # Range notation
            start_ip, end_ip = ip.split('-')
            start_parts = list(map(int, start_ip.split('.')))
            end_parts = list(map(int, end_ip.split('.')))
            # Expand all IPs in the range, incrementing each octet as needed
            current = start_parts.copy()
            while current <= end_parts:
                ip_addr = f"{current[0]}.{current[1]}.{current[2]}.{current[3]}"                            
                r.append(ip_addr)
                # Increment IP (IPv4 style)
                current[3] += 1
                for i in [3,2,1]:
                    if current[i] > 255:
                        current[i] = 0
                        current[i-1] += 1
            # Remove the original range string from remote_ips if present
            if ip in r:
                r.remove(ip)
        else:  # Single IP
            # Remove /32 if present (for single IPs written as x.x.x.x/32)
            if ip.endswith('/32'):
                r.append(ip.split('/')[0])
            else:
                r.append(ip)
    return r

def ips_to_csv(ip_list):
    """
    Convert a sorted list of IPv4 address strings into a CSV string,
    merging consecutive addresses into StartIP-EndIP ranges.

    Args:
        ip_list (list of str): Sorted list of IPv4 addresses as strings.

    Returns:
        str: A CSV string where consecutive runs are collapsed into StartIP-EndIP.
    """
    if not ip_list:
        return ""

    # Convert all to IPv4Address for easy arithmetic/comparison.
    ips = [IPv4Address(ip) for ip in ip_list]

    ranges = []
    start = prev = ips[0]

    for ip in ips[1:]:
        # Check if current ip is exactly prev + 1
        if int(ip) == int(prev) + 1:
            # extend the current range
            prev = ip
        else:
            # break in continuity; finalize the previous range
            if start == prev:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{prev}")
            # start a new range
            start = prev = ip

    # finalize the last range
    if start == prev:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{prev}")

    # Join all segments with commas
    return ",".join(ranges)

def set_remote_ips_to_firewall_rule(rule_name: str, ips, log: cs_firewall_log_analyzer.handler_for_CsLog.CsLog) -> None:
        
    try:
        ips_csv = ips_to_csv(ips)

        cmd = ["netsh", "advfirewall", "firewall", "set", "rule", f'name={rule_name}', "new", f"remoteip={ips_csv}" ]

        output = handler_for_cmd.run_command(cmd)
        log.add_line("CMD output:")
        log.add_line(output)

    except RuntimeError as e:
        log.add_line("Error setting firewall rule:")
        log.add_line(str(e))

def remove_duplicate_ips_and_sort(ips: list) -> list:
    ips = list(set(ips))  # Remove duplicates
    ips = sorted(ips, key=lambda ip: IPv4Address(ip))
    return ips

if __name__ == "__main__":
    log = cs_firewall_log_analyzer.handler_for_CsLog.CsLog('--------------------Starting...')

    RULE_NAME = "CraftSynth.RequestFloodGuard"
    # Here’s where you could decide on a remote IP or list, e.g.:
    # my_remote_ips = ["99.99.99.99"]
    # extra = [f"remoteip={','.join(my_remote_ips)}"] if my_remote_ips else None
    if rule_exists(RULE_NAME):
        print(f"Firewall rule '{RULE_NAME}' found.")
    else:
        print(f"Firewall rule '{RULE_NAME}' not found. Creating it now…")
        create_rule(f"netsh advfirewall firewall add rule name=CraftSynth.RequestFloodGuard description=http://www.f4cio.com/RequestFloodGuard dir=in action=block localip=any remoteip=255.255.255.254 protocol=any profile=domain,private,public interfacetype=any enable=yes edge=no security=notrequired", log)


    ips = get_remote_ips_from_firewall_rule(RULE_NAME, log)
    log.add_line(f"All found remote IPs: {len(ips)}")    
    ips.append("4.4.4.4")
    ips.append("4.4.4.5")
    ips.append("4.4.4.6")
    ips = list(set(ips))  # Remove duplicates
    ips = sorted(ips, key=lambda ip: IPv4Address(ip))
    set_remote_ips_to_firewall_rule(RULE_NAME, ips, log)
    ips = get_remote_ips_from_firewall_rule(RULE_NAME, log)    
    log.add_line(f"All found remote IPs: {len(ips)}")    
    log.add_line('--------------------Finished.')
