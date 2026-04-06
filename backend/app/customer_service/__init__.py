from flask import Blueprint

customer_service_bp = Blueprint('customer_service', __name__)

from . import routes, socket_events