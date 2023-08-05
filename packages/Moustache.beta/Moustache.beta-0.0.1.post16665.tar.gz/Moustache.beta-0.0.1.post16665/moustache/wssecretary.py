# -*- coding: utf-8 -*-

import json
import tempfile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from flask import Flask, render_template, request, send_file, jsonify, redirect, url_for, session
from jinja2 import TemplateSyntaxError

from moustache.InvalidUsage import InvalidUsage
from moustache.APIDefinition import APIDefinition
from moustache.FileRetriever import FileRetriever
from moustache.MoustacheCore import MoustacheCore

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
    if 'validation' in session:
        validation = session.pop('validation')
    parse_url = url_for('parse', _external=True)
    return render_template("test_form.html", validation=validation, parse_url=parse_url)


@app.route('/validate', methods=['POST'])
def validate():
    session['validation'] = {
        'is_valid': False,
        'message': ""
    }
    app.logger.debug("Starting validate API call")

    temp_directory = tempfile.mkdtemp()

    temp_template_file = FileRetriever.retrieve(APIDefinition.TEMPLATE_FILE_FORM_NAME,temp_directory)
    app.logger.info("Save file %s into %s" % (APIDefinition.TEMPLATE_FILE_FORM_NAME, temp_template_file))

    if not temp_template_file:
        session['validation']['message'] = "Le fichier %s n'est pas présent"%(APIDefinition.TEMPLATE_FILE_FORM_NAME)
        return redirect(url_for('index'))

    moustache_core = MoustacheCore()
    the_json = json.load(StringIO("{}"))
    try:
        moustache_core.validateTemplate(temp_template_file,the_json)
        session['validation']['is_valid'] = True
        session['validation']['message'] = "Le template est valide"
    except TemplateSyntaxError as e:
        session['validation']['message'] = "Syntax error on line %d : %s" % (e.lineno, e.message)

    return redirect(url_for('index'))


@app.route('/parse', methods=['POST'])
def parse():
    app.logger.debug("Starting parse API call")

    temp_directory = tempfile.mkdtemp()

    temp_template_file = FileRetriever.retrieve(APIDefinition.TEMPLATE_FILE_FORM_NAME,temp_directory)

    if not temp_template_file:
        raise InvalidUsage("Le fichier template n'est pas présent")

    if APIDefinition.JSON_FILE_FORM_NAME not in request.files:
        raise InvalidUsage("Le fichier json n'est pas présent")

    j = request.files[APIDefinition.JSON_FILE_FORM_NAME]
    json_content = j.stream.read()
    the_json = json.load(StringIO(json_content.decode('utf-8')))

    app.logger.debug("Retrieving json data %s" % the_json)

    gabarit_file_mapping = FileRetriever.retrieve_multiple(APIDefinition.GABARIT_FORM_NAME,temp_directory)
    app.logger.info("Retrieving %s files %s" % (APIDefinition.GABARIT_FORM_NAME,gabarit_file_mapping))

    annexe_file_mapping = FileRetriever.retrieve_multiple(APIDefinition.ANNEXE_FORM_NAME, temp_directory)
    app.logger.info("Retrieving %s files %s" % (APIDefinition.ANNEXE_MAPING_JSON_KEY, annexe_file_mapping))

    moustache_core = MoustacheCore()

    out_result = moustache_core.fusion(temp_template_file, the_json, gabarit_file_mapping, annexe_file_mapping)

    return send_file(out_result,as_attachment=True)


def default_app():
    return app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
