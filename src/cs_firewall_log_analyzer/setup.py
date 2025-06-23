from setuptools import setup, find_packages

setup(
    name='cs_firewall_log_analyzer',
    author='CraftSynth',
    version='1.0.0',
    description='A tool to query firewall logs and displays and returns results.',
    packages=find_packages(),
    install_requires=[
        'geoip2>=4.0.0',
        'requests>=2.25.1',
        'pandas>=1.1.5',
        'sqlite3>=3.42.0',
    ],
)
