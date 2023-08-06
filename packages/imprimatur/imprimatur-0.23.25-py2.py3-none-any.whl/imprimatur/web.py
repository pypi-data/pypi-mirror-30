from flask import (
    Flask, request, redirect, make_response, render_template, send_file)
import sys
from six import text_type
import threading
import imprimatur
import traceback
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile


app = Flask(__name__)

procs = {}

proc_lock = threading.Lock()


class RunThread(threading.Thread):
    def __init__(self, script, **kwargs):
        threading.Thread.__init__(self, **kwargs)
        self.script = script
        self.results = []
        self.results_lock = threading.Lock()

    def run(self):
        try:
            for txt in imprimatur.run(self.script):
                with self.results_lock:
                    self.results.append(txt)

        except:
            sys.stderr.write("An error:\n")
            sys.stderr.write(traceback.format_exc())

    def results_str(self):
        with self.results_lock:
            if len(self.results) == 0:
                return "Hasn't started yet..."
            elif self.results[-1] is None:
                txts = self.results[:-1]
            else:
                txts = self.results[:]
        return ''.join(txts)


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        with proc_lock:
            runs = procs.keys()
        return render_template('home.html', runs=runs)
    else:
        fl = request.files['file']
        script = text_type(fl.stream.read(), 'utf8')
        proc = RunThread(script)
        with proc_lock:
            proc_id = len(procs)
            procs[proc_id] = proc
            proc.start()
        return redirect('/runs/' + str(proc_id), 303)


@app.route('/runs/<int:run_id>')
def runs(run_id):
    with proc_lock:
        proc = procs[run_id]
    return render_template('run.html', proc=proc, run_id=run_id)


@app.route('/text_1')
def test_1():
    response = make_response(b'\xfeThe best of all possible worlds.')
    response.headers['content-length'] = '33'
    response.headers['content-type'] = 'text; charset=utf-8'
    response.headers['date'] = 'Sat, 17 Jan 2015 13:30:54 GMT'
    response.headers['server'] = 'Werkzeug/0.9.6 Python/3.4.0'
    return response


@app.route('/text_2')
def test_2():
    return 'I warn you Mr Bond, my patience is not inexhaustible.'


@app.route('/text_2_zip')
def test_2_zip():
    zfile = BytesIO()
    with ZipFile(zfile, mode='w', compression=ZIP_DEFLATED) as zf:
        zf.writestr(
            'bond.zip',
            'I warn you Mr Bond, my patience is not inexhaustible.')
    zfile.seek(0)
    return send_file(zfile, attachment_filename='bond.zip', as_attachment=True)


@app.route('/blank')
def blank():
    response = make_response('')
    response.headers['content-length'] = '0'
    response.headers['content-type'] = 'text; charset=utf-8'
    response.headers['date'] = 'Sat, 17 Jan 2015 13:30:54 GMT'
    response.headers['server'] = 'Werkzeug/0.9.6 Python/3.4.0'
    return response


@app.route('/echo', methods=['POST'])
def echo():
    ret = []
    fls = list(request.files.items())
    if len(fls) > 0:
        fname, fval = fls[0]
        ret.append(fname + ": " + text_type(fval.stream.read(), 'utf8') + '\n')
    ret.append(str(request.form) + '\n')
    return ''.join(ret)


@app.route('/echo_bin', methods=['POST'])
def echo_bin():
    return "okay"


@app.route('/redirect')
def redir():
    location = request.args['location']
    return redirect(location)


@app.route('/auth')
def auth():
    auth = request.authorization
    if auth is not None and auth.username == 'conrad' and \
            auth.password == 'kurtz':
        response = make_response('authorized')
    else:
        response = make_response('not authorized', 403)
    response.headers['content-length'] = '14'
    response.headers['content-type'] = 'text; charset=utf-8'
    response.headers['date'] = 'Sat, 17 Jan 2015 13:30:54 GMT'
    response.headers['server'] = 'Werkzeug/0.9.6 Python/3.4.0'
    return response


count = 0


@app.route('/counter_reset')
def counter_reset():
    global count
    count = 0
    return "Counter reset.\n"


@app.route('/counter')
def counter():
    global count
    count += 1
    if count == 3:
        return "The Decline And Fall Of The Roman Empire\n"
    else:
        return str(count) + "Gibbon\n"


@app.errorhandler(500)
def page_not_found(e):
    error = traceback.format_exc()
    sys.stderr.write(error)
    return error, 500


if __name__ == '__main__':
        app.run(debug=True)
