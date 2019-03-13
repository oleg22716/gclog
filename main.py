import os
from flask import Flask, render_template, request, url_for, jsonify, flash
from werkzeug.utils import redirect, secure_filename

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
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    filename = file.filename
    MLP2.ofname = filename
    destination = '/'.join([target, filename])
    print(destination)
    file.save(destination)
    MLP2.fname = destination
    # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    # file_id = 20000
    # file = request.files["file"]
    # # for file in request.files.getlist("file"):
    # print(file)
    # # fname = file.fname
    # filename = "thy_log_" + file_id.__str__()
    #
    # destination = '/'.join([target, filename])
    # print(destination)
    # file_id += 1
    # file.save(destination)
    MLP2.main()
    pause_timerange = MLP2.Metrics.pause_duration_timerange.value
    metrics = {  # todo: move this to the aggregator
        'programm_duration': utils.sex_formatter(MLP2.Metrics.total_program_duration.value),
        'fname': MLP2.Metrics.filename.value,
        'young_gen_allocated_formatted': kb_formatter(MLP2.Metrics.yg_allocated.value),
        'young_gen_allocated_plain': MLP2.Metrics.yg_allocated.value,
        'old_gen_allocated_formatted': kb_formatter(MLP2.Metrics.og_allocated.value),
        'old_gen_allocated_plain': MLP2.Metrics.og_allocated.value,
        'young_gen_peak_formatted': kb_formatter(MLP2.Metrics.yg_peak.value),
        'old_gen_peak_formatted': kb_formatter(MLP2.Metrics.og_peak.value),
        'meta_space_peak_formatted': kb_formatter(MLP2.Metrics.meta_peak.value),
        'meta_space_allocated_formatted': kb_formatter(MLP2.Metrics.meta_allocated.value),
        'yom_allocated_formatted': kb_formatter(MLP2.Metrics.yom_allocated.value),
        'yom_peak_formatted': kb_formatter(MLP2.Metrics.yom_peak.value),
        'throughput': "todo",  # todo
        'latency': "todo",
        'pause_timerange': MLP2.Metrics.pause_duration_timerange.value,
        'total_gc_count': MLP2.Metrics.full_gc_count.value + MLP2.Metrics.minor_gc_count.value,

        'full_gc_count': MLP2.Metrics.full_gc_count.value,
        'minor_gc_count': MLP2.Metrics.minor_gc_count.value,
        'total_reclaimed_bytes': kb_formatter(
            MLP2.Metrics.full_gc_reclaimed.value + MLP2.Metrics.minor_gc_reclaimed.value),
        # 'total_reclaimed_bytes': MLP2.Metrics.full_gc_reclaimed.value + MLP2.Metrics.minor_gc_reclaimed.value,
        'full_reclaimed_bytes': MLP2.Metrics.full_gc_reclaimed.value,
        'minor_reclaimed_bytes': MLP2.Metrics.minor_gc_reclaimed.value,
        'total_gc_time_total': MLP2.Metrics.full_gc_time_total.value + MLP2.Metrics.minor_gc_time_total.value,
        'full_gc_time_total': MLP2.Metrics.full_gc_time_total.value,
        'minor_gc_time_total': MLP2.Metrics.minor_gc_time_total.value,
        'total_gc_time_avg': (MLP2.Metrics.full_gc_time_total.value + MLP2.Metrics.minor_gc_time_total.value) /
                             (MLP2.Metrics.full_gc_count.value + MLP2.Metrics.minor_gc_count.value),
        'full_gc_time_avg': MLP2.Metrics.full_gc_time_avg.value,
        'minor_gc_time_avg': MLP2.Metrics.minor_gc_time_avg.value,
        'total_gc_time_stdev': MLP2.Metrics.total_pause_stdev.value,
        'full_gc_time_stdev': MLP2.Metrics.full_gc_time_stddev.value,
        'minor_gc_time_stdev': MLP2.Metrics.minor_gc_time_stddev.value,

        'total_gc_time_min': MLP2.Metrics.pause_min.value,
        'total_gc_time_max': MLP2.Metrics.pause_max.value,
        'full_gc_time_min_max': MLP2.Metrics.full_gc_time_min_max.value,
        'minor_gc_time_min_max': MLP2.Metrics.minor_gc_time_min_max.value,

        'total_interval_avg_time': MLP2.Metrics.total_pause_interval_average.value,
        'full_interval_avg_time': MLP2.Metrics.full_gc_interval_average.value,
        'minor_interval_avg_time': MLP2.Metrics.minor_gc_interval_average.value

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
                           metrics=metrics, pause_timerange=pause_timerange
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
    return render_template('v1.html',
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
