"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web
from hashlib import sha256
from uuid import uuid4
from sqlalchemy.exc import IntegrityError
import json

from pubkeeper.server.core.auth.local.models import Token, Right
from pubkeeper.server.core.auth.local.handlers import api_authenticated
from pubkeeper.server.core.auth.local.handlers.base import BaseHandler


class TokenHandler(BaseHandler):

    @api_authenticated
    def get(self):
        tokens = self._db.query(Token).all()
        self.output_json(tokens)

    def _token_exists(self):
        if not self.token:
            return False
        else:
            return self._db.query(Token).filter_by(token=self.token).first()

    def _write_rights(self, reset=False):
        writable_rights = []

        for right in self.json_data['rights']:
            if 'topic' not in right:
                self._db.rollback()
                raise web.HTTPError(400, "Each right must define a "
                                         "topic for which it is valid")

            read = right['read'] if 'read' in right else 0
            write = right['write'] if 'write' in right else 0

            writable_rights.append(Right(token=self.token,
                                         topic=right['topic'],
                                         read=read,
                                         write=write))

        if reset:
            self._db.query(Right).filter_by(token=self.token).delete()

        self._db.add_all(writable_rights)

    @api_authenticated
    def post(self):
        if 'rights' not in self.json_data:
            self._db.rollback()
            raise web.HTTPError(400, "A set of rights for this token "
                                     "is required")

        if not self.token:
            self.token = sha256(uuid4().bytes).hexdigest()

        description = self.json_data['description'] or "No Description Given"

        try:
            token = Token(token=self.token, description=description)
            self._db.add(token)
            self._write_rights(True)
            self._db.commit()
        except IntegrityError:
            self._db.rollback()
            raise web.HTTPError(409, "Token already exists") from None

        self.set_status(201)
        self.write(json.dumps({"token": self.token}))

    @api_authenticated
    def put(self):
        token = self._token_exists()
        if token is None:
            self._db.rollback()
            raise web.HTTPError(404, "A valid token is required to PUT")

        self._db.delete(token)
        self.post()
        self.set_status(200)

    @api_authenticated
    def patch(self):
        token = self._token_exists()
        if token is None:
            self._db.rollback()
            raise web.HTTPError(404, "A valid token is required to PATCH")

        try:
            if 'description' in self.json_data:
                token.description = self.json_data['description']

            if 'rights' in self.json_data:
                self._write_rights()

            self._db.commit()
            self.set_status(200)
            self.write(json.dumps({"token": self.token}))
        except IntegrityError:
            self._db.rollback()
            raise web.HTTPError(409, "Unable to PATCH") from None

    @api_authenticated
    def delete(self):
        token = self._token_exists()
        if token is None:
            self._db.rollback()
            raise web.HTTPError(404, "A valid token is required to DELETE")

        self._db.delete(token)
        self._db.commit()
