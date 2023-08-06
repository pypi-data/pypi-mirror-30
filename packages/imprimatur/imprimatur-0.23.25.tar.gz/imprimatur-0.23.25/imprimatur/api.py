import requests
import re
import time
from six import text_type
import traceback
import sre_constants
import zipfile
from io import BytesIO


def response_str(response, unzip):
    headers = response.headers
    res = []
    for k in sorted(headers.keys()):
        res.append(str((k, headers[k])) + '\n')
    res.append('\n')
    enc = 'utf8' if response.encoding is None else response.encoding
    if unzip:
        with zipfile.ZipFile(BytesIO(response.content)) as zfile:
            response_content = zfile.read(zfile.infolist()[0])
    else:
        response_content = response.content

    res.append(text_type(response_content, enc, 'ignore'))
    return ''.join(res)


CARRIED = frozenset(('host', 'port', 'scheme', 'auth', 'verify'))

NOT_CARRIED = frozenset(
    [
        'name', 'regexes', 'status_code', 'path', 'files', 'method', 'data',
        'tries', 'headers', 'unzip'])

KEYS = frozenset(CARRIED | NOT_CARRIED)


def run(script_str):
    try:
        reqs = eval(script_str)
    except SyntaxError:
        yield "Problem with script: " + traceback.format_exc()
        return

    s = requests.Session()

    defreq = {
        'host': 'localhost', 'port': 80, 'scheme': 'http', 'verify': False}
    failed = False
    for req in reqs:
        unrec = set(req.keys()) - KEYS
        if len(unrec) > 0:
            failed = True
            yield "The keys " + str(unrec) + " aren't recognized."
            break

        for k in CARRIED & set(req.keys()):
            defreq[k] = req[k]

        path = req.get('path', '/')
        url = defreq['scheme'] + '://' + defreq['host'] + ':' + \
            str(defreq['port']) + path

        auth = defreq.get('auth')
        verify = defreq['verify']

        method = req.get('method', 'get')

        try:
            yield "Name: " + req['name'] + '\n'
        except KeyError:
            pass

        try:
            files = dict(
                (k, open(v, 'rb')) for k, v in req['files'].items())
        except KeyError:
            files = None

        data = req.get('data')
        tries = req.get('tries', {'max': 1, 'period': 1})
        max_tries = tries.get('max', 10)
        period = tries.get('period', 1)
        headers = req.get('headers')
        unzip = req.get('unzip', False)
        allow_redirects = req.get('allow_redirects', False)

        j = 0
        failed = True
        msg = None
        while failed and j < max_tries:
            if j > 0:
                time.sleep(period)
            j += 1
            try:
                yield "Request: " + url + "\n"
                r = s.request(
                    method, url, files=files, data=data,
                    allow_redirects=allow_redirects, auth=auth, verify=verify,
                    headers=headers)
            except requests.exceptions.InvalidURL as e:
                msg = "Invalid URL: " + str(e) + '\n'
                break

            if 'status_code' in req:
                req_status_code = int(req['status_code'])
                if r.status_code != req_status_code:
                    msg = "The desired status code " + str(req_status_code) + \
                        " doesn't match the actual status code " + \
                        str(r.status_code) + ".\n" + response_str(r, unzip)
                    continue

            if 'regexes' in req:
                regex_failed = False
                k = 0
                while not regex_failed and k < len(req['regexes']):
                    pattern = req['regexes'][k]
                    k += 1
                    try:
                        if re.search(
                                pattern, response_str(r, unzip),
                                flags=re.MULTILINE | re.DOTALL) is None:
                            regex_failed = True
                    except sre_constants.error as e:
                        yield "Problem with regex: " + str(e) + '\n'
                        return
                if regex_failed:
                    msg = "The regular expression '" + pattern + \
                        "' fails.\n" + response_str(r, unzip)
                    continue

            failed = False

        if failed:
            yield msg
            break

    if not failed:
        yield "Passed all tests!\n"
        yield None
