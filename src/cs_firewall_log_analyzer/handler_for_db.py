import sqlite3
import os
import sys

if __package__:
    # Try relative import (for package usage)
    from .handler_for_CsLog import CsLog
    from . import handler_for_file_system
else:
    # Fallback to absolute import (for script/exe usage)
    from handler_for_CsLog import CsLog
    import handler_for_file_system

def pfirewall_logs_to_db(log, folder_path):

    db_file_path = handler_for_file_system.build_sattelite_file_path('.db')
    # Create a SQLite database and ensure connection is closed even if exception occurs
    with sqlite3.connect(db_file_path) as conn:
        c = conn.cursor()
        # Drop the table if it already exists
        c.execute("DROP TABLE IF EXISTS firewall_log")
        # Create a table to store the firewall log data
        c.execute('''CREATE TABLE IF NOT EXISTS firewall_log
                         (date_ms INTEGER, date TEXT, time TEXT, action TEXT, protocol TEXT, src_ip TEXT, dst_ip TEXT, src_port TEXT, dst_port TEXT, size TEXT, tcpflags TEXT, tcpsyn TEXT, tcpack TEXT, tcpwin TEXT, icmptype TEXT, icmpcode TEXT, info TEXT, path TEXT)''')
        # Commit the changes
        conn.commit()

    #find all files in folder_path starting with pfirewall.log
    if not folder_path:
        folder_path = '.'
    file_paths = [f for f in os.listdir(folder_path) if f.startswith('pfirewall.log')]

    if not file_paths:
        log.add_line(f"No pfirewall.log files found in folder {folder_path}.")
        return

    for file_path in file_paths:  
        file_path = os.path.join(folder_path, file_path)
        pfirewall_log_to_db(log, file_path)

def parse_date_to_ms(date: str, time: str):
    """Combine date and time, parse to datetime, and convert to milliseconds since epoch."""
    from datetime import datetime
    dt_str = f"{date} {time}"
    try:
        dt_obj = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return int(dt_obj.timestamp() * 1000)
    except Exception:
        return None

def pfirewall_log_to_db(log, file_path):
    log.add_line(f"Loading file: {file_path} into the database...")

    db_file_path = handler_for_file_system.build_sattelite_file_path('.db')
    with sqlite3.connect(db_file_path) as conn:
        c = conn.cursor()
        # Load the firewall log data into the database   
        with open(file_path, 'r') as f:
            lines = f.readlines()
        # Skip the header lines
        for i in range(4):
            lines.pop(0)
        for line in lines:
            fields = line.strip().split()
            if len(fields) > 0:
                date, time, action, protocol, src_ip, dst_ip, src_port, dst_port, size, tcpflags, tcpsyn, tcpack, tcpwin, icmptype, icmpcode, info, path = fields
                date_ms = parse_date_to_ms(date, time)
                c.execute("INSERT INTO firewall_log VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (date_ms, date, time, action, protocol, src_ip, dst_ip, src_port, dst_port, size, tcpflags, tcpsyn, tcpack,
                           tcpwin, icmptype, icmpcode, info, path))
        conn.commit()
    
def execute_query(query):
    db_file_path = handler_for_file_system.build_sattelite_file_path('.db')
    with sqlite3.connect(db_file_path) as conn:
        c = conn.cursor()
        c.execute(query)
        results = c.fetchall()
    return results