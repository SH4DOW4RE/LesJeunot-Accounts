from werkzeug.exceptions import HTTPException
from flask_jwt_extended import JWTManager
from flask import Flask, Response
from datetime import timedelta
from os import urandom, getenv
from dotenv import load_dotenv
from sqlite3 import connect

from routes.Index import bp as index
from routes.v1.Users import bp as v1_users
from routes.v1.Tickets import bp as v1_tickets


load_dotenv('.env')
HOST = str(getenv('HOST'))
PORT = int(str(getenv('PORT')))


app = Flask(__name__)
app.config['SECRET_KEY'] = urandom(64)
app.config['JWT_SECRET_KEY'] = urandom(64)
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6).seconds
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7).seconds
app.config['JWT_ENCODE_ISSUER'] = ''
jwt = JWTManager(app)


con = connect('database.sqlite')
cur = con.cursor()
query = """
    CREATE TABLE IF NOT EXISTS users (
        uuid VARCHAR(32) PRIMARY KEY NOT NULL,
        lastname LONGTEXT NOT NULL,
        firstname LONGTEXT NOT NULL,
        age UNSIGNED INT NOT NULL,
        email LONGTEXT NOT NULL,
        email_hash LONGTEXT NOT NULL,
        password LONGTEXT NOT NULL,
        role VARCHAR(5) NOT NULL
    )
"""
cur.execute(query)
query = """
    CREATE TABLE IF NOT EXISTS tickets (
        uuid PRIMARY KEY NOT NULL,
        showing LONGTEXT NOT NULL,
        user VARCHAR(32) NOT NULL,
        FOREIGN KEY(user) REFERENCES users(uuid)
    )
"""
cur.execute(query)
con.commit()


app.register_blueprint(index, url_prefix='/')
app.register_blueprint(v1_users, url_prefix='/v1/user')
app.register_blueprint(v1_tickets, url_prefix='/v1/ticket')


@app.errorhandler(401)
def errorHandler401(error: HTTPException):
    return {
        'status': error.code,
        'error': error.name,
        'message': 'Authorization token required.'
    }, 401

@app.errorhandler(404)
def errorHandler404(error: HTTPException):
    return {
        'status': error.code,
        'error': error.name,
        'message': 'The requested URL was not found.'
    }, 404

@app.after_request
def afterRequest(response: Response):
    response.headers.update({'Content-Type': 'application/json'})
    return response


if __name__ == '__main__':
    app.run(
        host = HOST,
        port = PORT,
        debug = False
    )
