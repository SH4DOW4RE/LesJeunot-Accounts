# LesJeunot-Accounts

Microservice comptes du projet Les Jeunot. Il gere les utilisateurs et leurs tickets.

## Prerequisites

- Python >= 3.11
- MySQL disponible et configure

## Installation

### 1. Cloner le repo

```bash
# HTTPS
git clone https://github.com/SH4DOW4RE/LesJeunot-Accounts.git
# SSH
git clone git@github.com:SH4DOW4RE/LesJeunot-Accounts.git
```

### 2. Creer un virtualenv et installer les dependances

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Creer un fichier .env

```bash
# Host IP and Port to listen on
HOST=127.0.0.1
PORT=5000

# Flask secrets (defaults are randomly generated at boot if omitted)
# SECRET_KEY=<random hex string>
# JWT_SECRET_KEY=<random hex string>
# JWT_ISSUER=

# Comma-separated list of allowed origins (default: "*")
CORS_ORIGINS=*

# Encryption key for the users' data (Required)
KEY=<32 bytes encoded in base64>

# MySQL settings
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=lesjeunot
DB_USER=lesjeunot
DB_PASSWORD=<strong password>
```

### 4. Lancer le service

```bash
python3 main.py
```

## Docker

```bash
docker build -t microservice-comptes .

docker run --rm -p 8080:8080 \
  -e HOST=0.0.0.0 \
  -e PORT=8080 \
  -e DB_NAME=lesjeunot \
  -e DB_USER=lesjeunot \
  -e DB_PASSWORD=secret \
  -e DB_HOST=host.docker.internal \
  -e DB_PORT=3306 \
  -e KEY=<32 bytes encoded in base64> \
  microservice-comptes
```

## Architecture rapide

- Flask + Flask-JWT-Extended
- SQLAlchemy (MySQL via PyMySQL)
- Donnees sensibles chiffre es avec Fernet
- Mot de passe hache via Argon2

## API

Base URL par defaut: `http://127.0.0.1:5000` (variable via `HOST`/`PORT`).

Toutes les reponses suivent le format:

```json
{ "status": 200, "data": { ... } }
```

Erreurs generiques:
- 401: `Authorization token required.`
- 404: `The requested URL was not found.`

### Index

`GET /` Ping basique.

`GET /versions` Liste les versions disponibles (ex. `v1`).

### Users (`/v1/user`)

`POST /v1/user/` Cree un utilisateur.

Corps:
```json
{
  "lastname": "Doe",
  "firstname": "Jane",
  "age": 22,
  "email": "jane.doe@example.com",
  "password": "secret"
}
```

Reponse 201:
```json
{
  "status": 201,
  "data": { "message": "User successfully created." }
}
```

`POST /v1/user/login` Authentifie un utilisateur.

Corps:
```json
{ "email": "jane.doe@example.com", "password": "secret" }
```

Reponse 200:
```json
{
  "status": 200,
  "data": {
    "message": "User successfully logged in.",
    "token": { "access": "<token>", "refresh": "<token>" }
  }
}
```

`GET /v1/user/refresh` Retourne un nouvel access token (JWT refresh requis).

`GET /v1/user/me` Retourne le profil de l'utilisateur courant (JWT requis).

Note: `PUT/PATCH /v1/user/<id>` et `DELETE /v1/user/` sont enregistres par le builder, mais les handlers `modify` et `delete` ne prennent pas de parametre `id`. En l'etat, ces routes renvoient une erreur serveur (TypeError).

### Tickets (`/v1/ticket`)

Toutes les routes tickets exigent un JWT d'acces.

`GET /v1/ticket/` Liste les tickets de l'utilisateur.

Reponse 200:
```json
{ "status": 200, "data": { "showings": ["<showing>"] } }
```

`GET /v1/ticket/<id>` Retourne le `showing` d'un ticket appartenant a l'utilisateur.

`POST /v1/ticket/` Cree un ticket.

Corps:
```json
{ "showing": "showing-id-or-label" }
```

Reponse 201:
```json
{ "status": 201, "data": { "message": "Ticket successfully created.", "uuid": "<uuid>" } }
```

`DELETE /v1/ticket/` Supprime tous les tickets de l'utilisateur.

`DELETE /v1/ticket/<id>` Supprime un ticket specifique.

## Modele de donnees

User (table `users`)
- uuid: string (32)
- lastname: text (chiffre)
- firstname: text (chiffre)
- age: text (chiffre)
- email: text (chiffre)
- email_hash: string (64, unique)
- password: text (argon2)
- role: string (admin/user)

Ticket (table `tickets`)
- uuid: string (32)
- showing: text
- user_id: string (ref `users.uuid`)
