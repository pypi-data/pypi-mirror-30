import tempfile

import magic
from jinja2 import TemplateSyntaxError

from moustache.APIDefinition import APIDefinition
from moustache.FusionHelper import FusionHelper
from moustache.InvalidUsage import InvalidUsage
from moustache.MoustacheRender import MoustacheRender


class MoustacheCore:

    _uno_port = 2002

    def __init__(self, uno_port=2002):
        self._uno_port = uno_port

    @staticmethod
    def validate_template(template_file_path, the_json):
        render = MoustacheRender()
        return render.render(
            template_file_path,
            **the_json
        )

    def fusion(self, template_file_path, the_json, gabarit_file_mapping, annexe_file_mapping):
        try:
            result = self.validate_template(template_file_path, the_json)
        except TemplateSyntaxError as e:
            raise InvalidUsage("Syntax error on line %d : %s" % (e.lineno, e.message))

        temp_result = tempfile.NamedTemporaryFile(suffix='.odt').name
        with open(temp_result, 'wb') as f_out:
            f_out.write(result)

        out_result = tempfile.NamedTemporaryFile(suffix='.odt').name

        self.helper = FusionHelper(self._uno_port, temp_result)

        if the_json.get(APIDefinition.GABARIT_MAPING_JSON_KEY):
            for gabarit_key, gabarit_value in the_json[APIDefinition.GABARIT_MAPING_JSON_KEY].items():
                if gabarit_value not in gabarit_file_mapping:
                    raise InvalidUsage(
                        "The file %s defined in %s is not present" % (
                            gabarit_value, APIDefinition.GABARIT_MAPING_JSON_KEY))
                if self.helper.search_and_select(gabarit_key):
                    self.helper.insert_odt(gabarit_file_mapping[gabarit_value])

        if the_json.get(APIDefinition.ANNEXE_MAPING_JSON_KEY):
            quality = int(the_json.get(APIDefinition.OUTPUT_QUALITY_JSON_KEY)) if the_json.get(
                APIDefinition.OUTPUT_QUALITY_JSON_KEY) else 150
            for annexe_key, annexe_value in the_json[APIDefinition.ANNEXE_MAPING_JSON_KEY].items():
                if annexe_value not in annexe_file_mapping:
                    raise InvalidUsage(
                        "The file %s defined in %s is not present" % (
                            annexe_value, APIDefinition.ANNEXE_MAPING_JSON_KEY))
                if self.helper.search_and_select(annexe_key):
                    annexe_filepath = self.transform_annexe_in_pdf(annexe_file_mapping[annexe_value])
                    self.helper.insert_pdf(annexe_filepath, quality=quality)

        self.helper.execute("UpdateAllIndexes")

        if the_json.get(APIDefinition.OUTPUT_FORMAT_JSON_KEY) == 'pdf':
            render_in_pdf = True
        else:
            render_in_pdf = False

        self.helper.save_and_close(out_result, pdf=render_in_pdf)
        return out_result

    @staticmethod
    def transform_annexe_in_pdf(annexe_filepath):
        mime_type = magic.from_file(annexe_filepath, mime=True)
        if 'application/pdf' in mime_type:
            return annexe_filepath
        elif 'application/vnd.oasis.opendocument.text' in mime_type:
            return self.helper.convert_odt_to_pdf(annexe_filepath)
            # TODO transformer l'odt en pdf
            raise Exception("Not implemented yet")
        else:
            raise InvalidUsage(
                "annexe %s is in bad format (%s) : only PDF and ODT are valid" % (annexe_filepath, mime_type))
