import msvcrt
import os
import time

import handler_for_email
import handler_for_firewall
import cs_firewall_log_analyzer

def state_machine():
    #If you run this app frequently (like every few seconds) we use state file to avoid running the app multiple times in parallel.
    #If you run this app while it is already running, it will just schedule one more run and exit.

    state_file_path = cs_firewall_log_analyzer.handler_for_file_system.build_sattelite_file_path('.state')
    if not os.path.exists(state_file_path):
        print('State file not found. Creating it...')
        with open(state_file_path, 'w') as state_file:
            state_file.write('not running')
    else:
        # If state file is invalid or its too long in mid-state reset it
        with open(state_file_path, 'r') as state_file:
            state = state_file.read().strip()
            if( state not in ['not running', 'running', 'scheduled']):
                print(f'Invalid state found in state file: {state}. Resetting to "not running"...')
                with open(state_file_path, 'w') as state_file:
                    state_file.write('not running')
            elif state == 'scheduled' and (time.time() - os.path.getmtime(state_file_path) > 300):
                print('State file is scheduled for another run but it is more than 5 minutes old. Resetting to "not running"...')
                with open(state_file_path, 'w') as state_file:
                    state_file.write('not running')

    with open(state_file_path, 'r') as state_file:
        state = state_file.read().strip()
    if state == 'not running':
        print('The script is not running. Running it...')
        with open(state_file_path, 'w') as state_file:
            state_file.write('running')
        Execute()
        with open(state_file_path, 'r') as state_file:
            state = state_file.read().strip()
        while state == 'scheduled':
            print('The script was scheduled for another run. Running it one more time...')
            with open(state_file_path, 'w') as state_file:
                state_file.write('running')
            Execute()
            with open(state_file_path, 'r') as state_file:
                state = state_file.read().strip()
        if(state == 'running'):
            print('The script finished running. Setting state to "not running"...')
            with open(state_file_path, 'w') as state_file:
                state_file.write('not running')
            
    elif state == 'running':
        print('The script is already running. Scheduling one more run...')
        with open(state_file_path, 'w') as state_file:
            state_file.write('scheduled')
        return            
            
    elif state == 'scheduled':
        print('The script is already scheduled for another run. Nothing else to do...')
        with open(state_file_path, 'w') as state_file:#we still want to rewrite file so timestamp is updated
            state_file.write('scheduled')
        return         

def Execute():
    log = cs_firewall_log_analyzer.handler_for_CsLog.CsLog('--------------------Starting...')

    try:
        ini_file_path = cs_firewall_log_analyzer.handler_for_file_system.build_sattelite_file_path('.ini')
        query = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('Query', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'Query:{query}')
        firewall_rule_name = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('FirewallRuleName', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'FirewallRuleName:{firewall_rule_name}')
        firewall_rule_creation_command = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('FirewallRuleCreationCommand', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'FirewallRuleCreationCommand:{firewall_rule_creation_command}')

        smtp_enabled = 'true'==cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_enabled', ini_file_path, True, False, True, False, False, False, '=').lower()
        log.add_line(f'smtp_enabled:{smtp_enabled}') 
        smtp_hostname = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_hostname', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'smtp_hostname:{"*" * len(smtp_hostname)}')
        smtp_port = int(cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_port', ini_file_path, True, None, True, None, False, None, '='))
        log.add_line(f'smtp_port:{smtp_port}')
        smtp_username = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_username', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'smtp_username:{smtp_username}')
        smtp_password = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_password', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'smtp_password:{"*" * len(smtp_password)}')
        smtp_from_address = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_from_address', ini_file_path, True, None, True, None, False, None, '=')   
        log.add_line(f'smtp_from_address:{smtp_from_address}')
        smtp_to_address = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_to_address', ini_file_path, True, None, True, None, False, None, '=')   
        log.add_line(f'smtp_to_address:{smtp_to_address}')
        smtp_subject = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_subject', ini_file_path, True, None, True, None, False, None, '=')
        log.add_line(f'smtp_subject:{smtp_subject}')
        smtp_use_ssl = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_use_ssl', ini_file_path, True, None, True, None, False, None, '=') 
        log.add_line(f'smtp_use_ssl:{smtp_use_ssl}')
        smtp_ignore_certificate_errors = cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('smtp_ignore_certificate_errors', ini_file_path, True, None, True, None, False, None, '=') 
        log.add_line(f'smtp_ignore_certificate_errors:{smtp_ignore_certificate_errors}')

        wait_for_any_key_to_exit = 'true'==cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('WaitForAnyKeyToExit', ini_file_path, False, False, False, False, False, False, '=').lower()
        log.add_line(f'WaitForAnyKeyToExit:{wait_for_any_key_to_exit}') 

        if handler_for_firewall.rule_exists(firewall_rule_name):
            log.add_line(f"Firewall rule '{firewall_rule_name}' found.")
        else:
            log.add_line(f"Firewall rule '{firewall_rule_name}' not found. Creating it now…")
            handler_for_firewall.create_rule(firewall_rule_creation_command, log)

        #parse the query to find the column index for the src_ip
        src_ip_column_index = -1
        query_parts = query.lower().split('select')[1].split('from')[0].strip().split(',')
        for index, part in enumerate(query_parts):
            if 'src_ip' in part:
                src_ip_column_index = index
                break

        attackers = cs_firewall_log_analyzer.cs_firewall_log_analyzer.main(log)
        new_attackers = []
        log.add_line(f"Detected attackers count: {len(attackers)}")

        if(len(attackers) == 0):
            log.add_line('No attackers found. Exiting...')
        else:
            blacklisted_ips = handler_for_firewall.get_remote_ips_from_firewall_rule(firewall_rule_name, log)
            log.add_line(f"Initial blacklisted IPs in firewall rule {firewall_rule_name} count: {len(blacklisted_ips)}")        
            log.add_line(f"Initial blacklisted IPs in firewall rule {firewall_rule_name} are:")
            if len(blacklisted_ips) > 50:
                for ip in blacklisted_ips[:50]:
                    log.add_line("   "+ip)
                log.add_line("   ... (only first 50 shown)")
            else:
                for ip in blacklisted_ips:
                    log.add_line("   "+ip)

            if src_ip_column_index < 0:
                log.add_line('WARNING: No src_ip column found in the query''s SELECT part so we can not find IPs from query result and blacklist them. Exiting...')
            else:            
                log.add_line(f'Adding new attackers IPs to that retrieved blacklist...')
                i = 0
                for attacker in attackers:
                    i += 1
                    attacker_ip = attacker[src_ip_column_index]
                    if attacker_ip not in blacklisted_ips:
                        new_attackers.append(attacker)
                        if(i<50):
                            log.add_line(f"    {i:>3}: {attacker_ip}")
                        elif(i==50):
                            log.add_line(f"    ... (only first 50 shown)")
                    blacklisted_ips.append(attacker[src_ip_column_index])
                log.add_line(f'{len(new_attackers)} new attackers IPs added to blacklist.')
                blacklisted_ips = handler_for_firewall.remove_duplicate_ips_and_sort(blacklisted_ips)

                count_of_blacklisted_ips_to_save = len(blacklisted_ips)
                log.add_line(f"Saving {len(blacklisted_ips)} blacklisted IPs back to firewall rule {firewall_rule_name}...")
                handler_for_firewall.set_remote_ips_to_firewall_rule(firewall_rule_name, blacklisted_ips, log)

                log.add_line('Retrieving blacklist from firewall rule...')
                blacklisted_ips = handler_for_firewall.get_remote_ips_from_firewall_rule(firewall_rule_name, log)
                log.add_line(f"Final blacklisted IPs in firewall rule {firewall_rule_name} count: {len(blacklisted_ips)}")
                log.add_line(f"Final blacklisted IPs in firewall rule {firewall_rule_name} are:")
                if len(blacklisted_ips) > 50:
                    for ip in blacklisted_ips[:50]:
                        log.add_line("   "+ip)
                    log.add_line("   ... (only first 50 shown)")
                else:
                    for ip in blacklisted_ips:
                        log.add_line("   "+ip)

                if count_of_blacklisted_ips_to_save == len(blacklisted_ips):
                    log.add_line(f"All {count_of_blacklisted_ips_to_save} blacklisted IPs were saved successfully.")
                else:
                    log.add_line(f"Warning: {count_of_blacklisted_ips_to_save} blacklisted IPs were expected to be saved, but only {len(blacklisted_ips)} were found in the firewall rule after saving.")
    
        if(smtp_enabled and len(new_attackers) > 0 ):
            log.add_line('--------------------Sending email...')
            handler_for_email.send_email(
                smtp_hostname,
                smtp_port,
                smtp_username,
                smtp_password,
                smtp_from_address,
                smtp_to_address,
                smtp_subject.replace('{attackers_count}', str(len(attackers))).replace('{new_attackers_count}', str(len(new_attackers))),
                log.get_body(),
                log=None,
                use_ssl=smtp_use_ssl.lower() == 'true',
                ignore_certificate_errors=smtp_ignore_certificate_errors.lower() == 'true'
            )

        log.add_line('--------------------Finished.')        
    
    except Exception as e:
        log.add_line(f'Error: {e}')
        log.add_line('Exiting due to error.')

        try:
            if(smtp_enabled):
                handler_for_email.send_email(
                    smtp_hostname,
                    smtp_port,
                    smtp_username,
                    smtp_password,
                    smtp_from_address,
                    smtp_to_address,
                    f'Request Flood Guard - error: {e}',
                    log.get_body(),
                    log=None,
                    use_ssl=smtp_use_ssl.lower() == 'true',
                    ignore_certificate_errors=smtp_ignore_certificate_errors.lower() == 'true'
            )
        except Exception as email_error:
            log.add_line(f'Error sending email: {email_error}')
            log.add_line('Exiting due to error in sending email.')
        return
def run_just_firewall_log_analyzer():
    log = cs_firewall_log_analyzer.handler_for_CsLog.CsLog('--------------------Starting...')

    try:
        cs_firewall_log_analyzer.cs_firewall_log_analyzer.main(log)
        log.add_line('--------------------Finished.')
    except Exception as e:
        log.add_line(f'Error: {e}')
        log.add_line('Exiting due to error.')

if __name__ == "__main__":
    if len(os.sys.argv) > 1 and os.sys.argv[1].lower() == '-show':
        run_just_firewall_log_analyzer()
    else:
        state_machine()

    ini_file_path = cs_firewall_log_analyzer.handler_for_file_system.build_sattelite_file_path('.ini')
    wait_for_any_key_to_exit = 'true'==cs_firewall_log_analyzer.handler_for_ini_file.get_setting_from_ini_file('WaitForAnyKeyToExit', ini_file_path, False, False, False, False, False, False, '=').lower()
    if wait_for_any_key_to_exit:
        print('Press any key to exit...')
        msvcrt.getch() 


