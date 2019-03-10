import os
from flask import Flask, render_template, request, url_for, jsonify

import MLP2
from utils import utils
from utils.utils import kb_formatter

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


@app.route('/ex')
def dyg_example():
    return "2"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route("/on_upload", methods=['POST'])
def on_upload():
    target = os.path.join(APP_ROOT, 'files/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    file_id = 20000
    file = request.files["file"]
    # for file in request.files.getlist("file"):
    print(file)
    # filename = file.filename
    filename = "thy_log_" + file_id.__str__()

    destination = '/'.join([target, filename])
    print(destination)
    file_id += 1
    file.save(destination)
    MLP2.main()
    metrics = {
            'young_gen_allocated_formatted': kb_formatter(MLP2.Metrics.yg_allocated.value),
            'young_gen_allocated_plain': MLP2.Metrics.yg_allocated.value,
            'old_gen_allocated_formatted': kb_formatter(MLP2.Metrics.og_allocated.value),
            'old_gen_allocated_plain': MLP2.Metrics.og_allocated.value
            }
    return render_template('v1.html',
                           zipYoung=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[3],
                                        # young_gen:before->after->allocated
                                        MLP2.Graphics.minor.data[4], MLP2.Graphics.minor.data[5]),
                           zipHeap=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[6],
                                       MLP2.Graphics.minor.data[7], MLP2.Graphics.minor.data[8]),
                           metaSpace=zip(MLP2.Graphics.full.data[0], MLP2.Graphics.full.data[12],
                                         MLP2.Graphics.full.data[13], MLP2.Graphics.full.data[14]),
                           pauseDurationFull=zip(MLP2.Graphics.full.data[0], MLP2.Graphics.full.data[15]),
                           pauseDurationMinor=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[9]),
                           metrics=metrics
                           )


@app.route("/react")
def react():
    return render_template("react.html")
# @app.route('/legend.css')
# def css():
#     return """
#        .dygraph-legend {
#   left: 140px !important;
#   background-color: transparent !important;ktf
# }
#     """


@app.route('/process')
def process():
    MLP2.main()
    return """<meta http-equiv="refresh" content="0; URL='result'" />"""


@app.route('/result')
def result():
    # return render_template('result.html',
    return render_template('v4.html',
                           zipYoung=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[3],
                                        # young_gen:before->after->allocated
                                        MLP2.Graphics.minor.data[4], MLP2.Graphics.minor.data[5]),
                           zipHeap=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[6],
                                       MLP2.Graphics.minor.data[7], MLP2.Graphics.minor.data[8]),
                           metaSpace=zip(MLP2.Graphics.full.data[0], MLP2.Graphics.full.data[12],
                                         MLP2.Graphics.full.data[13], MLP2.Graphics.full.data[14]),
                           pauseDurationFull=zip(MLP2.Graphics.full.data[0], MLP2.Graphics.full.data[15]),
                           pauseDurationMinor=zip(MLP2.Graphics.minor.data[0], MLP2.Graphics.minor.data[9])
                           )


if __name__ == "__main__":
    app.run(port=4555, debug=True)
