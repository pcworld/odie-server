#! /usr/bin/env python3

import crypt

import config
import models.acl as acl

from flask.ext.login import UserMixin
from odie import db, login_manager, Column

class User(db.Model, UserMixin):
    __tablename__ = 'benutzer'
    __table_args__ = config.public_table_args

    id = Column(db.Integer, name='benutzer_id', primary_key=True)
    username = Column(db.String(255), name='benutzername', unique=True)
    first_name = Column(db.Text, name='vorname')
    last_name = Column(db.Text, name='nachname')
    pw_hash = Column(db.String(255), name='passwort')
    effective_permissions = db.relationship('Permission', secondary=acl.effective_permissions, lazy='dynamic')

    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    def has_permission(self, perm_name):
        return self.effective_permissions.filter_by(name=perm_name).first() is not None

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if not user:
            return None
        if user.has_permission('homepage_login') and\
           crypt.crypt(password, user.pw_hash) == user.pw_hash:
            return user
        else:
            return None

    @login_manager.user_loader
    def load(user_id):  # pylint: disable=no-self-argument
        return User.query.get(user_id)
