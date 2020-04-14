
from flask import Flask, Blueprint, render_template
from record import videoType

api = Blueprint('api', __name__)

@app.route("/")
def hello():
    status = "Streaming"
    if videoType.is_pressed:
        status = "Recording"
    return render_template('index.html', status=status)


@app.route("/preview")
def preview():
    return render_template('index.html')