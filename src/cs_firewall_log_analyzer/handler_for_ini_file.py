import os

def get_setting_from_ini_file(setting_name, 
                              file_path=None, 
                              throw_error_if_not_found=True, 
                              result_in_not_found_case=None, 
                              throw_error_if_empty_string=True, 
                              result_in_empty_string_case=None, 
                              hide_errors=False, 
                              result_in_error_case=None, 
                              separator_between_key_and_value='='):
    r = None
    setting_name = setting_name.strip().lower()

    try:
        if file_path is None:
            file_path = os.path.splitext(os.path.basename(__file__))[0] + '.ini'

        found = False

        with open(file_path, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if line.lower().startswith(setting_name):
                key = line.split(separator_between_key_and_value)[0].strip().lower()
                if key == setting_name:
                    found = True
                    value = line[len(key) + 1:].strip() if len(line) > len(key) + 1 else ''

                    if value == '':
                        if not throw_error_if_empty_string:
                            r = result_in_empty_string_case
                        else:
                            error_message = f"Empty value for setting '{setting_name}' in file '{file_path}' is not allowed."
                            if result_in_empty_string_case is not None:
                                error_message = str(result_in_error_case)
                            raise Exception(error_message)
                    else:
                        r = value
                    break

        if not found:
            if not throw_error_if_not_found:
                r = result_in_not_found_case
            else:
                error_message = f"Missing setting '{setting_name}' from file '{file_path}'."
                if result_in_not_found_case is not None:
                    error_message = str(result_in_not_found_case)
                raise Exception(error_message)

    except Exception as exception:
        if hide_errors:
            r = result_in_error_case
        else:
            outer_exception = Exception(f"Cannot read setting '{setting_name}' from file '{file_path}'.") 
            raise outer_exception from exception

    return r
