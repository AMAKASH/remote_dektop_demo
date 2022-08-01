import io
import bcrypt
from flask import Flask, Response, request, jsonify, render_template, redirect
from werkzeug.wsgi import FileWrapper
from time import sleep

global STATE
STATE = {}
global terminate_session_key
terminate_session_key = ""

app = Flask(__name__)

''' Client '''


@app.route('/')
def root():
    return render_template('/index.html')


@app.route('/auth', methods=['POST'])
def autho():
    global STATE
    print(STATE.keys())
    req = request.get_json()
    print(req)
    key = req['_key']
    secret = req['_secret'].encode('utf-8')

    if key in STATE.keys() and bcrypt.checkpw(secret, STATE[key]['secret']):
        return Response({'ok': True},
                        mimetype='application/json', status=200)
    else:
        return Response({'Notok': False},
                        mimetype='application/json', status=401)


@app.route('/rd', methods=['POST'])
def rd():
    req = request.get_json()
    key = req['_key']
    secret = req['_secret'].encode('utf-8')
    global terminate_session_key
    print("terminate:   ", terminate_session_key)
    if key == terminate_session_key:
        sleep(1)
        terminate_session_key = ""
        return redirect("/", code=302)

    if key not in STATE.keys() or not bcrypt.checkpw(secret, STATE[key]['secret']):
        return Response({'msg': "Invalid Auth"},
                        mimetype='application/json', status=401)

    if req['filename'] == STATE[key]['filename']:
        attachment = io.BytesIO(b'')
    else:
        attachment = io.BytesIO(STATE[key]['im'])

    w = FileWrapper(attachment)
    resp = Response(w, mimetype='text/plain', direct_passthrough=True)
    resp.headers['filename'] = STATE[key]['filename']

    return resp


@ app.route('/event_post', methods=['POST'])
def event_post():
    global STATE

    req = request.get_json()
    key = req['_key']

    secret = req['_secret'].encode('utf-8')

    if key not in STATE.keys() or not bcrypt.checkpw(secret, STATE[key]['secret']):
        return Response({'msg': "Invalid Auth"},
                        mimetype='application/json', status=401)

    STATE[key]['events'].append(request.get_json())
    return jsonify({'ok': True})


''' Remote '''


@ app.route('/new_session', methods=['POST'])
def new_session():
    global STATE

    req = request.get_json()
    key = req['_key']
    secret = req['_secret']

    secret_hashed = bcrypt.hashpw(secret.encode('utf-8'), bcrypt.gensalt())

    STATE[key] = {
        'im': b'',
        'filename': 'none.png',
        'events': [],
        'secret': secret_hashed
    }

    return jsonify({'ok': True})


@ app.route('/terminate_session', methods=['POST'])
def terminate():
    global terminate_session_key
    req = request.get_json()
    key = req['_key']
    terminate_session_key = key

    return jsonify({'ok': True})


@ app.route('/capture_post', methods=['POST'])
def capture_post():
    global STATE

    with io.BytesIO() as image_data:
        filename = list(request.files.keys())[0]
        key = filename.split('_')[1]
        request.files[filename].save(image_data)
        STATE[key]['im'] = image_data.getvalue()
        STATE[key]['filename'] = filename

    return jsonify({'ok': True})


@ app.route('/events_get', methods=['POST'])
def events_get():
    req = request.get_json()
    key = req['_key']
    events_to_execute = STATE[key]['events'].copy()
    STATE[key]['events'] = []
    return jsonify({'events': events_to_execute})


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
    # app.run('0.0.0.0')
