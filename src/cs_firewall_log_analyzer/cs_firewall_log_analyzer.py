import sqlite3
from datetime import datetime
from ast import literal_eval
from sys import exception
import os
import sys
import re
import msvcrt

# Add the script directory to sys.path for PyInstaller exe compatibility
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __package__:
    from .handler_for_CsLog import CsLog
    from . import handler_for_db
    from .handler_for_geoip import HandlerForGeoIp
    from . import handler_for_ini_file
    from . import handler_for_file_system
else:
    from handler_for_CsLog import CsLog
    import handler_for_db
    from handler_for_geoip import HandlerForGeoIp
    import handler_for_ini_file
    import handler_for_file_system

def main(log=None):  
    if log is None:
            log = CsLog('')
    log.add_line('--------------------Starting cs_firewall_log_analyzer...')
    
    ini_file_path = handler_for_file_system.build_sattelite_file_path('.ini')
    pfirewall_log_folder_path = handler_for_ini_file.get_setting_from_ini_file('PFirewallLogFolderPath', ini_file_path, True, None, True, None, False, None, '=')
    log.add_line(f'PFirewallLogFolderPath:{pfirewall_log_folder_path}')
    query = handler_for_ini_file.get_setting_from_ini_file('Query', ini_file_path, True, None, True, None, False, None, '=')
    log.add_line(f'Query:{query}')
    query_only_last_x_minutes = int(handler_for_ini_file.get_setting_from_ini_file('QueryOnlyLastXMinutes', ini_file_path, True, 0, False, 0, False, 0, '='))
    log.add_line(f'QueryOnlyLastXMinutes:{query_only_last_x_minutes}')
    wait_for_any_key_to_exit = 'true'==handler_for_ini_file.get_setting_from_ini_file('WaitForAnyKeyToExit', ini_file_path, False, False, False, False, False, False, '=').lower()
    log.add_line(f'WaitForAnyKeyToExit:{wait_for_any_key_to_exit}') 
    
    #parse the query to find the column index for the src_ip
    src_ip_column_index = -1
    query_parts = query.lower().split('select')[1].split('from')[0].strip().split(',')
    for index, part in enumerate(query_parts):
        if 'src_ip' in part:
            src_ip_column_index = index
            break

    if src_ip_column_index < 0:
            log.add_line('WARNING: No src_ip column found in the query''s SELECT part so we can not find IPs from query result and show GeoIP data for them.')

    handler_for_db.pfirewall_logs_to_db(log, pfirewall_log_folder_path)

    if query_only_last_x_minutes > 0:
        current_time = datetime.now()
        time_limit = current_time.timestamp() - (query_only_last_x_minutes * 60)
        query = re.sub(r"\swhere\s", f" WHERE date_ms > {int(time_limit * 1000)} AND ", query, flags=re.IGNORECASE)
        log.add_line(f'Updated Query to only include last {query_only_last_x_minutes} minutes:')
        log.add_line(f'Query:{query}')

    results = handler_for_db.execute_query(query)
    results_with_geoip = []
    for row in results:
        if(src_ip_column_index <0):
            results_with_geoip.append(row)
            log.add_line(f"{str(row)}\n")
        else:
            geo_city_data = HandlerForGeoIp.get_city_info(row[src_ip_column_index])
            if isinstance(geo_city_data, dict):
                row_with_geo_city_data = row + tuple(geo_city_data.values())
            else:
                row_with_geo_city_data = row + (geo_city_data,)

            geo_asn_data = HandlerForGeoIp.get_asn_info(row[src_ip_column_index])
            if isinstance(geo_asn_data, dict):
                row_with_geo_city_and_asn_data = row_with_geo_city_data + tuple(geo_asn_data.values())
            else:
                row_with_geo_city_and_asn_data = row_with_geo_city_data + (geo_asn_data,)

            results_with_geoip.append(row_with_geo_city_and_asn_data)
            log.add_line(f"{str(row_with_geo_city_and_asn_data)}\n")

    log.add_line('--------------------Finished cs_firewall_log_analyzer.')
    log.add_line(f"Results: {len(results_with_geoip)} rows.")
    if not __package__ and wait_for_any_key_to_exit:
        log.add_line('Press any key to exit...')
        msvcrt.getch()
    return results_with_geoip

if __name__ == "__main__":
    main() 