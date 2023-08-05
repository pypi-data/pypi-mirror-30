# -*- coding: utf-8 -*-

import json
import tempfile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from jinja2 import TemplateSyntaxError
from moustache.MoustacheRender import MoustacheRender

from moustache.FusionHelper import FusionHelper
from moustache.InvalidUsage import InvalidUsage
from moustache.APIDefinition import APIDefinition
from moustache.FileRetriever import file_retriever


app = Flask(__name__)
app.secret_key = 'chaeQuaiy1oth1uu'


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/')
def index():
    validation = {}
    if 'validation' in session :
        validation = session.pop('validation')
    parse_url = url_for('parse',_external=True)
    return render_template("test_form.html",validation=validation,parse_url=parse_url)


@app.route('/validate',methods=['POST'])
def validate():

    session['validation'] = {
        'is_valid': False,
        'message': ""
    }
    app.logger.debug("Starting validate API call")

    temp_template_file = file_retriever.retrieve(app,APIDefinition.TEMPLATE_FILE_FORM_NAME)

    if not temp_template_file:
         session['validation']['message'] = "Le fichier template n'est pas présent"
         return redirect(url_for('index'))

    render = MoustacheRender()
    the_json = json.load(StringIO("{}"))
    try:
        render.render(
            temp_template_file,
            **the_json
        )
        session['validation']['is_valid'] = True
        session['validation']['message'] = "Le template est valide"
    except TemplateSyntaxError as e:
        session['validation']['message'] = "Syntax error on line %d : %s" % (e.lineno, e.message)

    return redirect(url_for('index'))


@app.route('/parse', methods=['POST'])
def parse():
    app.logger.debug("Starting parse API call")

    temp_template_file = file_retriever.retrieve(app,APIDefinition.TEMPLATE_FILE_FORM_NAME)

    if not temp_template_file:
        raise InvalidUsage("Le fichier template n'est pas présent")

    if APIDefinition.JSON_FILE_FORM_NAME not in request.files:
        raise InvalidUsage("Le fichier json n'est pas présent")

    j = request.files[APIDefinition.JSON_FILE_FORM_NAME]
    json_content = j.stream.read()
    the_json = json.load(StringIO(json_content.decode('utf-8')))

    app.logger.debug("Retrieving json data %s" % the_json)

    gabarit_file_mapping = file_retriever.retrieveMultiple(app,APIDefinition.GABARIT_FORM_NAME)

    annexe_file_mapping = file_retriever.retrieveMultiple(app, APIDefinition.ANNEXE_FORM_NAME)

    render = MoustacheRender()

    try:
        result = render.render(
            temp_template_file,
            **the_json
        )
    except TemplateSyntaxError as e:
        raise InvalidUsage("Syntax error on line %d : %s" % (e.lineno, e.message))

    temp_result = tempfile.NamedTemporaryFile(suffix='.odt').name
    with open(temp_result, 'wb') as f_out:
        f_out.write(result)

    out_result = tempfile.NamedTemporaryFile(suffix='.odt').name

    helper = FusionHelper(2002, temp_result)

    if the_json.get(APIDefinition.GABARIT_MAPING_JSON_KEY):
        for gabarit_key, gabarit_value in the_json[APIDefinition.GABARIT_MAPING_JSON_KEY].items():
            if helper.search_and_select(gabarit_key):
                helper.insert_odt(gabarit_file_mapping[gabarit_value])

    if the_json.get(APIDefinition.ANNEXE_MAPING_JSON_KEY):
        quality = int(the_json.get(APIDefinition.OUTPUT_QUALITY_JSON_KEY)) if the_json.get(APIDefinition.OUTPUT_QUALITY_JSON_KEY) else 150
        for annexe_key, annexe_value in the_json[APIDefinition.ANNEXE_MAPING_JSON_KEY].items():
            if helper.search_and_select(annexe_key):
                helper.insert_pdf(annexe_file_mapping[annexe_value], quality=quality)

    helper.execute("UpdateAllIndexes")

    if the_json.get(APIDefinition.OUTPUT_FORMAT_JSON_KEY) == 'pdf':
        render_in_pdf = True
        attachment_filename = "result.pdf"
        app.logger.debug("Response file format : PDF")
    else:
        render_in_pdf = False
        attachment_filename = "result.odt"
        app.logger.debug("Response file format : ODT")

    helper.save_and_close(out_result, pdf=render_in_pdf)
    app.logger.info("Send response : filename=%s" % attachment_filename)
    return send_file(out_result,
                     attachment_filename=attachment_filename,
                     as_attachment=True)


def default_app():
    return app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
