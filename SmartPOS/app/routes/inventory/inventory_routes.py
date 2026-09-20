"""Placeholder routes for the inventory module (domain: inventory).

TODO: replace with real request handling that calls the inventory service layer.
"""
from flask import Blueprint, jsonify

bp = Blueprint("inventory", __name__)


@bp.route("/")
def index():
    return jsonify({"module": "inventory", "domain": "inventory", "status": "not implemented yet"})
