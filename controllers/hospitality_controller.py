from flask import jsonify, request
from werkzeug.exceptions import BadRequest

from . import api
from services.hospitality_service import HospitalityService


@api.get("/restaurants/source")
def external_restaurants():
    try:
        return jsonify(HospitalityService.get_external_restaurants())
    except RuntimeError as exc:
        return jsonify(error=str(exc)), 502


def _json_object():
    if not request.is_json:
        return None, (jsonify(error="Content-Type must be application/json"), 415)
    try:
        payload = request.get_json()
    except BadRequest:
        return None, (jsonify(error="Request body contains invalid JSON"), 400)
    if not isinstance(payload, dict):
        return None, (jsonify(error="Request body must be a JSON object"), 400)
    return payload, None


@api.get("/menu")
def list_menu():
    return jsonify([item.to_dict() for item in HospitalityService.list_menu(request.args.get("category"))])


@api.post("/bookings")
def create_booking():
    payload, error = _json_object()
    if error:
        return error
    try:
        booking = HospitalityService.create_booking(payload)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(booking.to_dict()), 201


@api.post("/orders")
def create_order():
    payload, error = _json_object()
    if error:
        return error
    try:
        order = HospitalityService.create_order(payload)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(order.to_dict()), 201

