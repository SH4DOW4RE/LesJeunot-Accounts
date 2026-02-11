import json

from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from http import HTTPStatus
from uuid import uuid4

from sqlalchemy import delete as sql_delete, select

from database import get_session
from models import Ticket, User
from modules.RESTful_Builder import Builder
from modules.Tariffs import get_tariff


def send(code: int, response: dict | None = None):
    payload = {"status": code}
    if response is not None:
        payload["data"] = response
    return jsonify(payload), code


def abort(code: int, message: str):
    return (
        jsonify(
            {"status": code, "error": HTTPStatus(code).phrase, "message": message}
        ),
        code,
    )


def uuid() -> str:
    return uuid4().hex


def _serialize_showing(showing: dict | str) -> str:
    if isinstance(showing, str):
        return showing
    return json.dumps(showing, separators=(",", ":"))


def _deserialize_showing(showing: str | dict):
    if not isinstance(showing, str):
        return showing
    try:
        return json.loads(showing)
    except json.JSONDecodeError:
        return showing


def _ticket_payload(ticket: Ticket, include_owner: bool = False):
    payload = {
        "uuid": ticket.uuid,
        "showing": _deserialize_showing(ticket.showing),
        "tariff": ticket.tariff,
        "price_cents": ticket.price_cents,
    }
    if include_owner:
        payload["user_id"] = ticket.user_id
    return payload


@jwt_required()
def getAll():
    identity = get_jwt_identity()
    scope = request.args.get("scope")

    with get_session() as session:
        if scope == "all":
            current = session.get(User, identity)
            if current is None:
                return abort(404, "User not found.")
            if current.role != "admin":
                return abort(403, "Admin role required.")

            tickets = session.execute(select(Ticket)).scalars().all()
            reservations = [
                _ticket_payload(ticket, include_owner=True) for ticket in tickets
            ]
            return send(200, {"tickets": reservations})

        tickets = session.scalars(
            select(Ticket).where(Ticket.user_id == identity)
        ).all()
        reservations = [_ticket_payload(ticket) for ticket in tickets]

    if not reservations:
        return abort(404, "No tickets were found.")

    return send(200, {"tickets": reservations})


@jwt_required()
def getOne(id: str):
    identity = get_jwt_identity()

    with get_session() as session:
        ticket = session.scalar(
            select(Ticket).where(Ticket.uuid == id, Ticket.user_id == identity)
        )

    if ticket is None:
        return abort(404, f"The specified ticket was not found ({id}).")

    return send(200, {"ticket": _ticket_payload(ticket)})


@jwt_required()
def create():
    identity = get_jwt_identity()

    showing = request.json.get("showing")
    if showing is None:
        return abort(400, "Missing value: showing")
    if not isinstance(showing, (dict, str)):
        return abort(400, "Invalid value: showing")

    with get_session() as session:
        user = session.get(User, identity)
        if user is None:
            return abort(404, "User not found.")
        tariff = get_tariff(user.tariff)
        ticket = Ticket(
            uuid=uuid(),
            showing=_serialize_showing(showing),
            user_id=identity,
            tariff=tariff.code,
            price_cents=tariff.price_cents,
        )
        ticket_uuid = ticket.uuid
        session.add(ticket)

    return send(
        201,
        {
            "message": "Ticket successfully created.",
            "uuid": ticket_uuid,
            "tariff": tariff.code,
            "price_cents": tariff.price_cents,
        },
    )


@jwt_required()
def delete(id: str | None = None):
    identity = get_jwt_identity()

    with get_session() as session:
        if id is not None:
            result = session.execute(
                sql_delete(Ticket).where(
                    Ticket.uuid == id,
                    Ticket.user_id == identity,
                )
            )
            if result.rowcount == 0:
                return abort(404, f"Ticket {id} not found.")
        else:
            session.execute(
                sql_delete(Ticket).where(
                    Ticket.user_id == identity,
                )
            )

    plural = "s" if id is None else ""
    return send(200, {"message": f"Ticket{plural} successfully deleted."})


bp = Builder("v1-tickets").bind(
    getAll=getAll,
    getOne=getOne,
    create=create,
    delete=delete,
).bp
