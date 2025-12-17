from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlite3 import connect as sqlconnect, Connection, Cursor
from flask import request, jsonify 
from http import HTTPStatus
from uuid import uuid4

from modules.RESTful_Builder import Builder


def send(code: int, response: dict = {}): return (jsonify({'status': code, 'data': response}), code) if response is not {} else (jsonify({'status': code}), code)
def abort(code: int, message: str): return jsonify({'status': code, 'error': HTTPStatus(code).phrase, 'message': message}), code

def uuid() -> str: return uuid4().hex


def connect() -> tuple[Connection, Cursor]:
    con = sqlconnect('database.sqlite')
    cur = con.cursor()
    return (con, cur)


@jwt_required()
def getAll():
    identity = get_jwt_identity()
    
    query = """
        SELECT
            showing
        FROM
            tickets
        WHERE
            user = ?
    """
    con, cur = connect()
    cur.execute(query, (identity,))
    results = cur.fetchall()
    
    if len(results) < 1: return abort(404, f'No tickets were not found.')
    
    return send(200, {'showings': [x[0] for x in results]})

@jwt_required()
def getOne(id: str):
    identity = get_jwt_identity()
    
    query = """
        SELECT
            showing
        FROM
            tickets
        WHERE
            uuid = ?
        AND
            user = ?
    """
    con, cur = connect()
    cur.execute(query, (id, identity))
    results = cur.fetchone()
    
    if len(results) < 1: return abort(404, f'The specified ticket was not found ({id})')
    
    return send(200, {'showing': results[0]})

@jwt_required()
def create():
    identity = get_jwt_identity()
    
    showing = request.json.get('showing', None)
    if showing is None: return abort(400, f'Missing value: showing')

    id = uuid()
    query = """
        INSERT INTO tickets (
            uuid,
            showing,
            user
        ) values (?, ?, ?)
    """
    con, cur = connect()
    cur.execute(query, (id, showing, identity))
    con.commit()
    
    return send(200, {'message': 'Ticket successfully created.', 'uuid': id})

@jwt_required()
def delete(id: str | None = None):
    identity = get_jwt_identity()
    
    if id is not None:
        query = """
            DELETE FROM
                tickets
            WHERE
                uuid = ?
            AND
                user = ?
        """
        con, cur = connect()
        cur.execute(query, (id, identity))
    else:
        query = """
            DELETE FROM
                tickets
            AND
                user = ?
        """
        con, cur = connect()
        cur.execute(query, (identity,))
    con.commit()
    
    return send(200, {
        'message': f'Ticket{("s" if id is not None else "")} successfully deleted.'
    })


bp = Builder('v1-tickets').bind(
    getAll = getAll,
    getOne = getOne,
    create = create,
    delete = delete
).bp
