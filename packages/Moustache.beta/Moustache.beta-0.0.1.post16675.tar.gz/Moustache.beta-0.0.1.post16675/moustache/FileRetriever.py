import os
from flask import request


class FileRetriever:

    @staticmethod
    def retrieve(input_file_name,temp_directory):
        if input_file_name not in request.files:
            return False
        f = request.files[input_file_name]
        temp_template_file = os.path.join(temp_directory,f.filename)
        f.save(temp_template_file)
        return temp_template_file

    @staticmethod
    def retrieve_multiple(input_file_name, temp_directory):
        gabarit_filelist = request.files.getlist(input_file_name)
        gabarit_file_mapping = {}
        for gabarit_file in gabarit_filelist:
            temp_gabarit_file = os.path.join(temp_directory, gabarit_file.filename)
            gabarit_file.save(temp_gabarit_file)
            gabarit_file_mapping[gabarit_file.filename] = temp_gabarit_file
        return gabarit_file_mapping
