from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from sqlite3 import connect as sqlconnect, Connection, Cursor
from cryptography.fernet import Fernet, InvalidToken
from flask import request, jsonify
from dotenv import load_dotenv
from http import HTTPStatus
from hashlib import sha256
from uuid import uuid4
from os import getenv

from modules.RESTful_Builder import Builder
from modules.Hasher import Hasher


load_dotenv('.env')
KEY = str(getenv('KEY'))


HASHER = Hasher()


def send(code: int, response: dict = {}): return (jsonify({'status': code, 'data': response}), code) if response is not {} else (jsonify({'status': code}), code)
def abort(code: int, message: str): return jsonify({'status': code, 'error': HTTPStatus(code).phrase, 'message': message}), code

def uuid() -> str: return uuid4().hex


def connect() -> tuple[Connection, Cursor]:
    con = sqlconnect('database.sqlite')
    cur = con.cursor()
    return (con, cur)


def checkKey() -> None:
    k = KEY.encode('utf-8')
    try: Fernet(k)
    except ValueError: raise KeyError('The key is not in a valid format. (32 Bytes URL-Safe Encoded Base64)')

def encrypt(message: str) -> str:
    checkKey()
    f = Fernet(KEY)
    return f.encrypt(message.encode('utf-8')).decode('utf-8')

def decrypt(message: str) -> str | None:
    checkKey()
    f = Fernet(KEY)
    try: return f.decrypt(message).decode('utf-8')
    except InvalidToken: return None 

@jwt_required()
def getMe():
    identity = get_jwt_identity()
    
    query = """
        SELECT
        uuid,
            lastname,
            firstname,
            age,
            email,
            role
        FROM
            users
        WHERE
            uuid = ?
    """
    con, cur = connect()
    cur.execute(query, (identity,))
    results = cur.fetchone()
    
    return send(200, {
        'lastname': decrypt(results[0]),
        'firstname': decrypt(results[1]),
        'age': decrypt(results[2]),
        'email': decrypt(results[3]),
        'role': results[4]
    })

def create():
    lastname = request.json.get('lastname', None)
    firstname = request.json.get('firstname', None)
    age = request.json.get('age', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    role = 'admin' if email is not None and email.endswith('@shadoweb.fr') else 'user'
    
    data = {'lastname': lastname, 'firstname': firstname, 'age': age, 'email': email, 'password': password, 'role': role }
    if None in list(data.values()):
        return abort(400, f'Missing value(s): [{", ".join([x for x in list(data.keys()) if data[x] is None])}]') # type: ignore

    email_hash = sha256(email.encode('utf-8')).digest().hex()
    
    lastname = encrypt(lastname) # type: ignore
    firstname = encrypt(firstname) # type: ignore
    age = encrypt(age) # type: ignore
    email = encrypt(email) # type: ignore
    password = HASHER.hash(password) # type: ignore

    identity = uuid()
    query = """
        INSERT INTO users (
            uuid,
            lastname,
            firstname,
            age,
            email,
            email_hash,
            password,
            role
        ) values (?, ?, ?, ?, ?, ?, ?, ?)
    """
    con, cur = connect()
    cur.execute(query, (identity, lastname, firstname, age, email, email_hash, password, role))
    con.commit()
    
    return send(200, {'message': 'User successfully created.'})

@jwt_required()
def modify():
    identity = get_jwt_identity()
    
    lastname = request.json.get('lastname', None)
    firstname = request.json.get('firstname', None)
    age = request.json.get('age', None)
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    role = 'admin' if email is not None and email.endswith('@shadoweb.fr') else 'user'

    n = 0
    if lastname is not None:
        lastname = encrypt(lastname)
        n += 1
    if firstname is not None:
        firstname = encrypt(firstname)
        n += 1
    if age is not None:
        age = encrypt(age)
        n += 1
    if email is not None:
        email_hash = sha256(email.encode('utf-8')).digest().hex()
        email = encrypt(email)
        n += 1
    if password is not None:
        password = HASHER.hash(password)
        n += 1
    
    if n < 1 and request.method.upper() == 'PATCH': return abort(400, 'At least one field is required.')
    if n < 5 and request.method.upper() != 'PATCH': return abort(400, 'Use PATCH for a partial modification of user data.')
    
    con, cur = connect()
    
    if lastname is not None:
        query = """UPDATE users lastname = ? WHERE uuid = ?"""
        cur.execute(query, (lastname, identity))
    
    if firstname is not None:
        query = """UPDATE users firstname = ? WHERE uuid = ?"""
        cur.execute(query, (firstname, identity))
    
    if age is not None:
        query = """UPDATE users age = ? WHERE uuid = ?"""
        cur.execute(query, (age, identity))
    
    if email is not None:
        query = """UPDATE users email = ?, email_hash = ? WHERE uuid = ?"""
        cur.execute(query, (email, email_hash, identity)) # type: ignore
    
    if password is not None:
        query = """UPDATE users password = ? WHERE uuid = ?"""
        cur.execute(query, (password, identity))
    
    if role is not None:
        query = """UPDATE users role = ? WHERE uuid = ?"""
        cur.execute(query, (role, identity))
    
    con.commit()
    
    return send(200, {'message': 'User successfully modified.'})

@jwt_required()
def delete():
    identity = get_jwt_identity()
    
    query = """
        DELETE FROM
            users
        WHERE
            uuid = ?
    """
    con, cur = connect()
    cur.execute(query, (identity,))
    con.commit()
    
    return send(200, {
        'message': 'User successfully deleted.'
    })

def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    
    data = {'email': email, 'password': password}
    if None in list(data.values()):
        return abort(400, f'Missing value(s): [{", ".join([x for x in list(data.keys()) if data[x] is None])}]') # type: ignore
    
    email_hash = sha256(email.encode('utf-8')).digest().hex()
    
    query = """
        SELECT
            uuid,
            email,
            password
        FROM
            users
        WHERE
            email_hash = ?
    """
    con, cur = connect()
    cur.execute(query, (email_hash,))
    results = cur.fetchall()
    
    identity: str | None = None
    for result in results:
        u, e, p = result
        email_valid = (decrypt(e) == email)
        password_valid, new_password = HASHER.verify_and_rehash(p, password)
        if email_valid and password_valid:
            query = """UPDATE users SET password = ? WHERE uuid = ?"""
            cur.execute(query, (new_password, identity))
            con.commit()
            identity = u
    
    if identity is None: return abort(401, 'Email or Password invalid.')
    
    access = create_access_token(identity = identity, fresh = True)
    refresh = create_refresh_token(identity = identity)
    
    return send(200, {
        'message': 'User successfully logged in.',
        'token': {
            'access': access,
            'refresh': refresh
        }
    })

@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    
    access = create_access_token(identity=identity, fresh=False)
    
    return send(200, {
        'token': {
            'access': access
        }
    })


bp = Builder('v1-users').bind(
    login = login,
    refresh = refresh,
    getMe = getMe,
    create = create,
    modify = modify,
    delete = delete
).bp
