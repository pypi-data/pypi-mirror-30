# encoding=utf-8

from ardj.models import Token
from database import connect
from users import resolve_alias
from util import run


def create_token(login, login_type=None):
    if login_type == "jid":
        raise RuntimeError("Tokens can only be sent by email.")
    token = Token.create(login)
    # TokenMailer(login, token["token"]).deliver()
    # connect().commit()
    return token


def confirm_token(token):
    saved = Token.get_by_id(token)
    if saved is None:
        return False

    if saved["active"]:
        return False

    saved["active"] = 1
    saved.put()

    return True


def get_id_by_token(token):
    saved = Token.get_by_id(token)
    if saved is None or not saved["active"]:
        return None
    return saved["login"]


def get_active_tokens():
    """Returns active tokens"""
    return [t for t in Token.find_all()
        if t["active"]]
