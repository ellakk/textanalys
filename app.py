from flask import Flask, request, jsonify, render_template
from src.helpers import create_response
from src.analyzer import Analyzer
from src.report import Report

APP = Flask(__name__)
APP.config["JSON_AS_ASCII"] = False


class APIError(Exception):
    "Class for handling error responses for the API."
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        return create_response(self.message, self.status_code)


@APP.errorhandler(APIError)
def handle_error(error):
    """Method for handling API error responses."""
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@APP.route("/", methods=["GET"])
def start():
    """This route serves both the main index.html template and the result of the
    analysis template."""
    return render_template("index.html")


@APP.route("/api/docx", methods=["POST"])
def docx_post():
    """This is the API route to analyze docx files."""
    if len(request.files) != 1:
        raise APIError("Du måste POSTa exakt en fil.")
    if "file" not in request.files:
        raise APIError("Dokumentet måste POSTas som en fil.")

    file = request.files["file"]
    if ".docx" not in file.filename:
        raise APIError("Dokumentet måste vara i docx format", 415)

    report = None
    try:
        report = Report(file)
    except:
        raise APIError("Kunde inte läsa dokumentet.", 400)

    analyser = Analyzer(report)
    analyser.run()

    if analyser.has_errors():
        return jsonify(create_response(
            f"Hittade {len(analyser.errors)} fel i dokumentet.",
            data=analyser.errors))
    return jsonify(create_response("Inga fel hittades i dokumentet."))


if __name__ == "__main__":
    APP.run(debug=True)
