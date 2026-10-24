from flask import jsonify, request
from werkzeug.exceptions import BadRequest

from . import api
from services.resto_service import RestoService


def _json_body():
    if not request.is_json:
        return None, (jsonify(error="Content-Type must be application/json"), 415)

    try:
        payload = request.get_json()
    except BadRequest:
        return None, (jsonify(error="Request body contains invalid JSON"), 400)

    if not isinstance(payload, dict):
        return None, (jsonify(error="Request body must be a JSON object"), 400)

    return payload, None


@api.get("/hello")
def hello():
    return jsonify(message="Hello from Flask")


@api.get("/restaurants")
def list_restaurants():
    restaurants = RestoService.list_restaurants()
    return jsonify([restaurant.to_dict() for restaurant in restaurants])


@api.post("/restaurants")
def create_restaurant():
    payload, error = _json_body()
    if error:
        return error

    try:
        restaurant = RestoService.create_restaurant(payload)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    return jsonify(restaurant.to_dict()), 201


@api.get("/restaurants/<int:resto_id>")
def get_restaurant(resto_id):
    restaurant = RestoService.get_restaurant(resto_id)
    if restaurant is None:
        return jsonify(error="Restaurant not found"), 404
    return jsonify(restaurant.to_dict())


@api.route("/restaurants/<int:resto_id>", methods=["PUT", "PATCH"])
def update_restaurant(resto_id):
    payload, error = _json_body()
    if error:
        return error

    try:
        restaurant = RestoService.update_restaurant(
            resto_id,
            payload,
            partial=request.method == "PATCH",
        )
    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    if restaurant is None:
        return jsonify(error="Restaurant not found"), 404
    return jsonify(restaurant.to_dict())


@api.delete("/restaurants/<int:resto_id>")
def delete_restaurant(resto_id):
    if not RestoService.delete_restaurant(resto_id):
        return jsonify(error="Restaurant not found"), 404
    return "", 204