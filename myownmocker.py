import random
import string
import os
from flask import Flask, jsonify, request, abort, Response, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.exceptions import default_exceptions
from werkzeug.exceptions import HTTPException


def make_json_app(import_name, **kwargs):
    """
    Creates a JSON-oriented Flask app.

    All error responses that you don't specifically
    manage yourself will have application/json content
    type, and will contain JSON like this (just an example):

    { "message": "405: Method Not Allowed" }
    """
    def make_json_error(ex):
        if isinstance(ex, HTTPException):
            response = jsonify(message=ex.description)
            response.status_code = ex.code
        else:
            response = jsonify(message=str(ex))
            response.status_code = 500

        return response

    app = Flask(import_name, **kwargs)

    for code in default_exceptions.iterkeys():
        app.error_handler_spec[None][code] = make_json_error

    return app

app = make_json_app(__name__)
app.config.update(dict(
    SQLALCHEMY_DATABASE_URI='sqlite:///dev.db',
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
))

if 'DATABASE_URL' in os.environ:
    print 'got it', os.environ['DATABASE_URL']
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']

db = SQLAlchemy(app)


@app.route('/')
def index():
    return redirect('http://fopina.github.io/myownmocker/')


@app.route('/register/', methods=['GET'])
def register():
    token = None

    for t in xrange(5):
        ttoken = ''.join(random.SystemRandom().choice(string.letters + string.digits) for _ in range(16))
        if db.session.query(MockToken).filter_by(token=ttoken).first() is None:
            token = ttoken
            break

    if token is not None:
        db.session.add(MockToken(token))
        db.session.commit()
        return jsonify(token=token)
    else:
        abort(503, 'Unable to generate a token, please try again')


@app.route('/setup/<token>/', methods=['POST'])
def setup(token):
    '''
    expected JSON dictionary with:
    {
        "path": "/action/path/",
        "status_code": 200,
        "content_type": "application/json",
        "body": "{\"field\": \"value\"}"
    }
    '''

    mt = db.session.query(MockToken).filter_by(token=token).first()

    if mt is None:
        abort(404, 'Invalid token')

    data = request.get_json()
    try:
        path = data['path']
        if path[0] == '/':
            path = path[1:]
        pt = mt.paths.filter_by(path=path).first()
        if pt is None:
            pt = MockPath(mt.token, path)
        pt.status_code = data['status_code']
        pt.content_type = data['content_type']
        pt.body = data.get('body')
        db.session.add(pt)
        db.session.commit()
    except KeyError as e:
        abort(400, 'Missing required field: %s' % e.args[0])
    return jsonify(message='ok')


@app.route('/mock/<token>/<path:path>', methods=['GET', 'POST'])
def use_api(token, path):
    pt = db.session.query(MockPath).filter_by(token_id=token, path=path).first()

    if pt is None:
        abort(404, 'Method not found')

    resp = Response(
        pt.body,
        content_type=pt.content_type,
        status=pt.status_code,
    )
    return resp


class MockPath(db.Model):
    __table_args__ = (
        db.UniqueConstraint('path', 'token_id', name='_path_token_uc'),
        db.Index('_token_path_ix', 'token_id', 'path')
    )

    id = db.Column(db.Integer, primary_key=True)
    token_id = db.Column(db.String(16), db.ForeignKey('mock_token.token'), nullable=False)
    path = db.Column(db.String(200), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    content_type = db.Column(db.String(30), nullable=False)
    body = db.Column(db.String(500))

    token = db.relationship('MockToken', backref=db.backref('paths', lazy='dynamic'))

    def __init__(self, token, path):
        self.token_id = token
        self.path = path


class MockToken(db.Model):
    token = db.Column(db.String(16), primary_key=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())

    def __init__(self, token=None):
        self.token = token

    def __repr__(self):
        return '<MockToken %r>' % (self.token)
