from datetime import datetime
import os
import sys

if __package__:
    from . import handler_for_file_system
else:
    import handler_for_file_system

class CsLog:
    body = ''
    log_file_path = None

    def __init__(self, initial_body='', log_file_path=None):
        self.body = initial_body

        log_file_path = handler_for_file_system.build_sattelite_file_path(log_file_path)
        self.log_file_path = log_file_path

        self.add_line(initial_body)    

    def get_body(self):
        return self.body

    def add_line(self, line: str):
        line = f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {line}'

        self.body += line+'\n'

        print(line)

        if self.log_file_path:
            with open(self.log_file_path, 'a') as log_file:
                log_file.write(line+'\n')