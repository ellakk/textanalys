from flask import Flask, request, jsonify, render_template
from src.helpers import parse_docx
from src.analyzer import Analyzer

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False


class Error(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(Error)
def handle_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/api/docx", methods=["POST"])
def docx_post():
    if len(request.files) != 1:
        raise Error("You need to post exactly one file.")
    if "file" not in request.files:
        raise Error("The document need to be POSTed as a file.")

    file = request.files["file"]
    if ".docx" not in file.filename:
        raise Error("The document has to be in docx format", 415)

    document = None
    try:
        document = parse_docx(file)
    except:
        raise Error("Could not parse the supplied document.", 400)

    analyser = Analyzer(document)
    analyser.run()

    if analyser.has_errors():
        return jsonify(analyser.errors)
    return "OK"


if __name__ == "__main__":
    app.run(debug=True)
