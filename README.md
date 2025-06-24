# RequestFloodGuard 1.0
Detects brute-force RDC attacks in Firewall log and blocks found IP-s<br>
Video presentation: http://www.f4cio.com/RequestFloodGuard

This python app will load all firewall logs from specified folder and detect attackers by running the specified query on those logs. Default query detects frequent requests on RDC port. It will then update or, if not found, create a firewall rule to block those attackers. Finally if attackers were detected it will send an email with the list of attackers IPs (and their rough location) blacklisted/added to firewall rule.

Idea is to run this app either periodically or on every failed login attempt. If you run this app frequently (like every few seconds) app uses .state file to prevent running the app multiple times in parallel. If you run this app while it is already running, it will just schedule one more run and exit.

If you run this app with *-show* argument it will just execute query and show result

Make sure to run it with admin rights. Маke sure to enable firewall logging in Windows Firewall settings.

Above is the default behavior but you can change configuration to identify any desired set of requests from Firewall log
or to modify Firewall rule that is being updated. See *RequestFloodGuard.ini* for configuration options.

The free IP to City Lite database by DB-IP is licensed under a Creative Commons Attribution 4.0 International License:
https://creativecommons.org/licenses/by/4.0/
You can ocasionally re-download .mmdb GeoIP databases but keep same file names:
- https://db-ip.com/db/download/ip-to-city-lite
- https://db-ip.com/db/download/ip-to-asn-lite

## Installation
If your favourite python dev invironment doesn't do this on startup you should manually install virtual environment and packages.

On windows:
<code>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install sqlite3
pip install geoip2
pip install pyinstaller
</code>

On MacOS/Linux:
<code>
python3 -m venv .venv
source .venv/bin/activate
pip install sqlite3
pip install geoip2
pip install pyinstaller
</code>

Run build_exe.bat to publish to \dist.
