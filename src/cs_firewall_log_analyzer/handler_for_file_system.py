
import os
import sys
def build_sattelite_file_path(extension_or_file_name_or_file_path=None):
    main_file_path = os.path.abspath(sys.argv[0])
    main_file_name_without_extension = os.path.splitext(os.path.basename(main_file_path))[0]
    main_folder_path = os.path.dirname(main_file_path)
    if(not extension_or_file_name_or_file_path):#user passed no parameter or falsy value
        r = os.path.join(main_folder_path, main_file_name_without_extension+'.'+ ('log' if not extension_or_file_name_or_file_path else extension_or_file_name_or_file_path))
    else:
        if os.path.isabs(extension_or_file_name_or_file_path):#user passed absolute path
            r = extension_or_file_name_or_file_path
        else:
            if(extension_or_file_name_or_file_path.startswith('.')):#user passed extension
                r = os.path.join(main_folder_path, main_file_name_without_extension + extension_or_file_name_or_file_path)
            else:
                if(extension_or_file_name_or_file_path.startswith('\\') or extension_or_file_name_or_file_path.startswith('/')):#user passed relative path
                    r = os.path.join(main_folder_path, extension_or_file_name_or_file_path)
                else:
                    if('\\' in extension_or_file_name_or_file_path or '/' in extension_or_file_name_or_file_path):#user passed relative path with file name
                        r = os.path.join(main_folder_path, extension_or_file_name_or_file_path)
                    else:
                        if('.' in extension_or_file_name_or_file_path):#user passed file name
                            r = os.path.join(main_folder_path, extension_or_file_name_or_file_path)
                        else:
                            if(len(extension_or_file_name_or_file_path) <=3):#user passed extension
                                r = os.path.join(main_folder_path, main_file_name_without_extension + '.' + extension_or_file_name_or_file_path)
                            else:#user passed file name without extension
                                r = os.path.join(main_folder_path, extension_or_file_name_or_file_path)
    return r