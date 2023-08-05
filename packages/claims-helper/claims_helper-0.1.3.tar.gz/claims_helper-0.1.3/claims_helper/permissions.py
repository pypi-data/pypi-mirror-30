import requests

from flask import Blueprint, jsonify, request
from claims_helper import ClaimsHelper

permissions = Blueprint('permissions', __name__)

class NotAuthorized(Exception):
    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

@permissions.app_errorhandler(NotAuthorized)
def handle_unauthorized_error(exception):
    return jsonify({'message': exception.message}), exception.status_code

def check_is_specified_user_or_admin(request, user_id):
    claims_helper = ClaimsHelper(request)

    request_user_id = claims_helper.get_user_id()
    if request_user_id is None:
        raise NotAuthorized('No user associated with request', requests.codes.unauthorized)

    if request_user_id != user_id and not claims_helper.is_admin():
        raise NotAuthorized('Not authorised', requests.codes.forbidden)

def check_is_any_user(request):
    claims_helper = ClaimsHelper(request)

    request_user_id = claims_helper.get_user_id()
    if request_user_id is None:
        raise NotAuthorized('No user associated with request', requests.codes.unauthorized)

def check_is_admin(request):
    claims_helper = ClaimsHelper(request)

    request_user_id = claims_helper.get_user_id()
    if request_user_id is None:
        raise NotAuthorized('No user associated with request', requests.codes.unauthorized)

    if not claims_helper.is_admin():
        raise NotAuthorized('Not authorised', requests.codes.forbidden)

