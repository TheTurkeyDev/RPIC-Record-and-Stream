
from flask import Flask, Blueprint, render_template
from settings import videoType

api = Blueprint('api', __name__)


@api.route("/")
def hello():
    status = "Streaming"
    if videoType == "Recording":
        status = "Recording"
    return render_template('index.html', status=status)


@api.route("/preview")
def preview():
    return render_template('index.html')
