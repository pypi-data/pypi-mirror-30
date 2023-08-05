import tempfile
from flask import request

class FileRetriever:

    def retrieve(self,app,input_file_name):
        if (not input_file_name in request.files):
            return False
        f = request.files[input_file_name]
        temp_template_file = tempfile.NamedTemporaryFile(suffix='.odt').name
        f.save(temp_template_file)
        app.logger.info("Saving template file %s to %s" % (f.filename, temp_template_file))
        return temp_template_file

    def retrieveMultiple(self, app, input_file_name):
        gabarit_filelist = request.files.getlist(input_file_name)
        gabarit_file_mapping = {}
        app.logger.info("Gabarit file list %s" % gabarit_filelist)

        for gabarit_file in gabarit_filelist:
            temp_gabarit_file = tempfile.NamedTemporaryFile(suffix='.odt').name
            gabarit_file.save(temp_gabarit_file)
            gabarit_file_mapping[gabarit_file.filename] = temp_gabarit_file
            app.logger.info("Saving gabarit %s to %s" % (gabarit_file, temp_gabarit_file))

        return gabarit_file_mapping


file_retriever = FileRetriever()
