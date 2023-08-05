#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
curl -i -X POST http://localhost:5000/api \
    -F "params=@ressources/test-ok/skyttles.json" \
    -F "principal=@ressources/test-ok/principal.pdf" \
    -F "annexe=@ressources/test-ok/annexe1.pdf" \
    -F "annexe=@ressources/test-ok/annexe2.pdf" > resultws.pdf
"""
import json
import tempfile
from moustache_fusion import skyttlesPY
import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from flask import Flask, request, send_file, jsonify

OUTPUT_FORMAT_JSON_KEY = "__output_format"
OUTPUT_QUALITY_JSON_KEY = "__output_quality"


app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# TODO a virer ?
app.secret_key = 'super secret key'


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/api', methods=['POST'])
def api():
    app.logger.debug("Starting API call")

    if 'params' not in request.files:
        raise InvalidUsage("Le fichier json de paramètres n'est pas présent")
    j = request.files['params']
    json_content = j.stream.read()
    the_json = json.load(StringIO(json_content.decode('utf-8')))
    app.logger.debug("Retrieving json data %s" % the_json)

    if 'principal' not in request.files:
        raise InvalidUsage("Le fichier principal n'est pas présent")
    f = request.files['principal']
    principal_file = tempfile.NamedTemporaryFile(suffix='.pdf').name
    f.save(principal_file)
    app.logger.info("Saving template file %s to %s" % (f.filename, principal_file))
    the_json["general"]["name"] = principal_file

    annexes_filelist = request.files.getlist("annexe")
    annexes_file_mapping = []
    app.logger.info("annexes file list %s" % annexes_filelist)

    for annexe_file in annexes_filelist:
        temp_annexe_file = tempfile.NamedTemporaryFile(suffix='.pdf').name
        annexe_file.save(temp_annexe_file)
        annexes_file_mapping.append(temp_annexe_file)
        app.logger.info("Saving gabarit %s to %s" % (annexe_file, temp_annexe_file))
        # TODO pb si nom de fichier non unique
        for annexe in the_json["annexes"]:
            if annexe["name"] == annexe_file.filename:
                annexe["name"] = temp_annexe_file
                break

    output_file = tempfile.NamedTemporaryFile(suffix='.pdf').name

    res = skyttlesPY.skyttles(the_json, output_file, True)
    if res is not True:
        raise InvalidUsage(res)

    # cleanup
    os.remove(principal_file)
    for n in range(len(annexes_file_mapping)):
        v = annexes_file_mapping[n]
        os.remove(v)

    return send_file(output_file, attachment_filename="result.pdf", as_attachment=True)


def default_app():
    return app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
