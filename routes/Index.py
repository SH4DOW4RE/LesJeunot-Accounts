from os.path import join, isdir
from flask import Blueprint
from http import HTTPStatus
from os import listdir


bp = Blueprint('index', __name__)


def send(code: int, response: dict | None = None): return {'status': code, 'data': response} if response is not None else {'status': code}
def abort(code: int, message: str): return {'status': code, 'error': HTTPStatus(code).phrase, 'message': message}


@bp.get('/')
def index():
    return send(200)


@bp.get('/versions')
def versions():
    versions = [d for d in listdir('routes') if isdir(join('routes', d)) and d != '__pycache__']
    return send(200, {
        'versions': versions
    })
