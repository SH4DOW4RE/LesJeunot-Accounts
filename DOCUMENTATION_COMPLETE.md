# Documentation Complète du Projet LesJeunot-Accounts

## Introduction

Le projet **LesJeunot-Accounts** est un microservice dédié à la gestion des comptes utilisateurs et des tickets pour le projet **Les Jeunot**. Il s'agit d'une API RESTful construite avec Flask qui permet de gérer les utilisateurs, leurs authentifications et leurs réservations de tickets.

## Historique du Projet

Le projet a été initié avec un commit initial (`78fee46`) et a évolué à travers plusieurs étapes clés :

1. **Migration vers MySQL/SQLAlchemy** : Le projet a migré d'un système de stockage initial vers MySQL avec SQLAlchemy pour une meilleure gestion des données relationnelles.

2. **Normalisation des routes API** : Les routes ont été documentées et normalisées pour une meilleure cohérence.

3. **Fonctionnalités administratives** : Ajout de fonctionnalités permettant aux administrateurs de lister les utilisateurs et les réservations.

## Architecture Technique

### Technologies Utilisées

#### Backend Framework
- **Flask** (version 3.1.2) : Micro-framework Python pour la création d'APIs RESTful. Choisie pour sa légèreté et sa flexibilité.

#### Base de Données
- **MySQL** : Système de gestion de base de données relationnelle.
- **SQLAlchemy** (version 2.0.36) : ORM (Object-Relational Mapping) pour interagir avec la base de données de manière objet.
- **PyMySQL** (version 1.1.1) : Pilote Python pour MySQL.

#### Authentification et Sécurité
- **Flask-JWT-Extended** (version 4.7.1) : Gestion des tokens JWT pour l'authentification.
- **Argon2** (via `argon2-cffi` version 25.1.0) : Algorithme de hachage de mots de passe sécurisé.
- **Fernet** (via `cryptography` version 42.0.8) : Chiffrement des données sensibles des utilisateurs.

#### Autres Dépendances
- **python-dotenv** (version 1.2.1) : Gestion des variables d'environnement.
- **Flask-CORS** (version 4.0.0) : Gestion des requêtes cross-origin.

### Structure du Projet

```
LesJeunot-Accounts/
├── .idea/
├── modules/
│   ├── Hasher/
│   │   ├── __init__.py
│   │   └── main.py
│   └── RESTful_Builder/
│       ├── __init__.py
│       └── main.py
├── routes/
│   ├── v1/
│   │   ├── Tickets.py
│   │   └── Users.py
│   └── Index.py
├── .gitignore
├── API_ROUTES.md
├── config.py
├── database.py
├── Dockerfile
├── main.py
├── models.py
├── README.md
└── requirements.txt
```

### Modules Clés

#### 1. **Hasher** (`modules/Hasher/main.py`)

Ce module gère le hachage sécurisé des mots de passe en utilisant Argon2, un algorithme moderne et résistant aux attaques par force brute. Il fournit les fonctionnalités suivantes :

- **Hachage** : Conversion des mots de passe en hachages sécurisés.
- **Vérification** : Vérification de la correspondance entre un mot de passe et un hachage.
- **Rehachage** : Mise à jour automatique des hachages si les paramètres de sécurité changent.

**Paramètres Argon2** :
- `time_cost=1`
- `memory_cost=2097152` (2 GiB)
- `parallelism=8`
- `salt_len=64`
- `hash_len=1024`

#### 2. **RESTful Builder** (`modules/RESTful_Builder/main.py`)

Ce module est un constructeur de routes RESTful qui simplifie la création des endpoints. Il permet de lier des fonctions de rappel (callbacks) à des routes spécifiques (GET, POST, PUT, PATCH, DELETE) de manière déclarative.

### Configuration

La configuration est gérée via le fichier `config.py` qui charge les variables d'environnement depuis un fichier `.env`. Les principales configurations incluent :

- **Serveur** : `HOST`, `PORT`
- **Sécurité** : `SECRET_KEY`, `JWT_SECRET_KEY`, `JWT_ISSUER`
- **Base de Données** : `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- **CORS** : `CORS_ORIGINS`
- **Chiffrement** : `KEY` (clé de 32 octets encodée en base64)

### Base de Données

#### Modèles

##### User

Représente un utilisateur dans le système.

**Champs** :
- `uuid` : Identifiant unique (32 caractères)
- `lastname` : Nom de famille (chiffré)
- `firstname` : Prénom (chiffré)
- `age` : Âge (chiffré)
- `email` : Adresse email (chiffrée)
- `email_hash` : Hachage de l'email (64 caractères, unique)
- `password` : Mot de passe (haché avec Argon2)
- `role` : Rôle de l'utilisateur (`admin` ou `user`)

**Relations** :
- `tickets` : Relation one-to-many avec les tickets.

##### Ticket

Représente un ticket réservé par un utilisateur.

**Champs** :
- `uuid` : Identifiant unique (32 caractères)
- `showing` : Informations sur la séance (peut être une chaîne ou un JSON)
- `user_id` : Identifiant de l'utilisateur propriétaire

**Relations** :
- `user` : Relation many-to-one avec l'utilisateur.

### Routes API

#### Index

- `GET /` : Ping basique pour vérifier le statut du service.
- `GET /versions` : Liste les versions disponibles de l'API.

#### Users (`/v1/user`)

- `POST /v1/user/` : Création d'un utilisateur.
- `POST /v1/user/login` : Authentification d'un utilisateur.
- `GET /v1/user/refresh` : Rafraîchissement du token d'accès.
- `GET /v1/user/me` : Récupération du profil de l'utilisateur courant.
- `GET /v1/user/` : Liste tous les utilisateurs (réservé aux administrateurs).
- `PUT/PATCH /v1/user/<id>` : Modification d'un utilisateur.
- `DELETE /v1/user/` : Suppression d'un utilisateur.

#### Tickets (`/v1/ticket`)

- `GET /v1/ticket/` : Liste les tickets de l'utilisateur courant.
- `GET /v1/ticket/<id>` : Récupération d'un ticket spécifique.
- `POST /v1/ticket/` : Création d'un ticket.
- `DELETE /v1/ticket/` : Suppression de tous les tickets de l'utilisateur.
- `DELETE /v1/ticket/<id>` : Suppression d'un ticket spécifique.

### Sécurité

#### Chiffrement des Données

Les données sensibles des utilisateurs (nom, prénom, âge, email) sont chiffrées à l'aide de Fernet, un algorithme de chiffrement symétrique basé sur AES. La clé de chiffrement est stockée dans la variable d'environnement `KEY` et doit être une chaîne de 32 octets encodée en base64.

#### Hachage des Mots de Passe

Les mots de passe sont hachés avec Argon2, un algorithme conçu pour résister aux attaques par force brute. Les paramètres utilisés sont optimisés pour un bon équilibre entre sécurité et performance.

#### Authentification

L'authentification est gérée via JWT (JSON Web Tokens). Deux types de tokens sont utilisés :

- **Access Token** : Valide pendant 6 heures, utilisé pour accéder aux ressources protégées.
- **Refresh Token** : Valide pendant 7 jours, utilisé pour obtenir un nouvel access token.

### Gestion des Erreurs

L'API retourne des réponses standardisées avec un format JSON cohérent :

```json
{
  "status": 200,
  "data": { ... }
}
```

En cas d'erreur, le format est :

```json
{
  "status": 404,
  "error": "Not Found",
  "message": "The requested URL was not found."
}
```

### Déploiement

#### Local

1. Cloner le dépôt.
2. Créer un environnement virtuel et installer les dépendances.
3. Configurer le fichier `.env` avec les variables d'environnement nécessaires.
4. Lancer le service avec `python3 main.py`.

#### Docker

Le projet peut être déployé via Docker :

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

## Fonctionnalités Principales

### Gestion des Utilisateurs

- **Création** : Les utilisateurs peuvent s'inscrire avec leurs informations personnelles.
- **Authentification** : Connexion sécurisée avec email et mot de passe.
- **Profil** : Accès aux informations personnelles chiffrées.
- **Modification** : Mise à jour des informations utilisateur.
- **Suppression** : Suppression du compte utilisateur.

### Gestion des Tickets

- **Création** : Réservation de tickets pour des séances.
- **Liste** : Visualisation des tickets réservés.
- **Détails** : Accès aux informations d'un ticket spécifique.
- **Suppression** : Annulation de réservations.

### Rôles et Permissions

- **Utilisateur** : Accès aux fonctionnalités de base (gestion de son propre compte et de ses tickets).
- **Administrateur** : Accès à toutes les fonctionnalités, y compris la liste de tous les utilisateurs et de toutes les réservations.

## Bonnes Pratiques

### Sécurité

- **Chiffrement** : Toutes les données sensibles sont chiffrées avant d'être stockées.
- **Hachage** : Les mots de passe sont hachés avec un algorithme moderne et sécurisé.
- **JWT** : Utilisation de tokens pour une authentification stateless et sécurisée.

### Code

- **Modularité** : Le code est organisé en modules réutilisables.
- **Clarté** : Les fonctions sont bien documentées et les noms sont explicites.
- **Gestion des Erreurs** : Les erreurs sont gérées de manière cohérente et retournées avec des messages clairs.

### Base de Données

- **ORM** : Utilisation de SQLAlchemy pour une interaction objet avec la base de données.
- **Relations** : Les relations entre les modèles sont bien définies et gérées.

## Conclusion

Le projet **LesJeunot-Accounts** est un microservice bien conçu pour la gestion des comptes utilisateurs et des tickets. Il utilise des technologies modernes et sécurisées pour garantir la confidentialité et l'intégrité des données. L'architecture est modulaire et extensible, ce qui permet d'ajouter facilement de nouvelles fonctionnalités à l'avenir.

## Annexes

### Variables d'Environnement

```
HOST=127.0.0.1
PORT=5000
SECRET_KEY=<random hex string>
JWT_SECRET_KEY=<random hex string>
JWT_ISSUER=
CORS_ORIGINS=*
KEY=<32 bytes encoded in base64>
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=lesjeunot
DB_USER=lesjeunot
DB_PASSWORD=<strong password>
```

### Exemple de Requête

**Création d'un Utilisateur** :

```bash
curl -X POST http://127.0.0.1:5000/v1/user/ \
  -H "Content-Type: application/json" \
  -d '{
    "lastname": "Doe",
    "firstname": "Jane",
    "age": 22,
    "email": "jane.doe@example.com",
    "password": "secret"
  }'
```

**Réponse** :

```json
{
  "status": 201,
  "data": { "message": "User successfully created." }
}
```

### Exemple de Requête d'Authentification

```bash
curl -X POST http://127.0.0.1:5000/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.doe@example.com",
    "password": "secret"
  }'
```

**Réponse** :

```json
{
  "status": 200,
  "data": {
    "message": "User successfully logged in.",
    "token": { "access": "<token>", "refresh": "<token>" }
  }
}
```

### Exemple de Requête de Création de Ticket

```bash
curl -X POST http://127.0.0.1:5000/v1/ticket/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "showing": "showing-id-or-label"
  }'
```

**Réponse** :

```json
{
  "status": 201,
  "data": { "message": "Ticket successfully created.", "uuid": "<uuid>" }
}
```

## Liens Utiles

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [JWT Documentation](https://jwt.io/)
- [Argon2 Documentation](https://argon2-cffi.readthedocs.io/)
- [Fernet Documentation](https://cryptography.io/en/latest/fernet/)