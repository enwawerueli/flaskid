#!/usr/bin/env python

import os

from flask import current_app
from flask_script import Manager, Shell, prompt_bool

from app import create_app, db, models, forms


manager = Manager(create_app)
manager.add_option('-c', '--config', dest='env', default='default', required=False,
                   help="The environment configuration to use: [development | testing | production]")


@manager.command
def create_db():
    """Create database tables."""
    return db.create_all()


@manager.command
def seed_db():
    """Populate database with initial data after it is created."""
    models.Role.populate()


@manager.command
def drop_db():
    """Drop all database tables."""
    if prompt_bool('Drop all database tables? (y/n)'):
        return db.drop_all()


@manager.command
def create_admin():
    """Create an admin user account."""
    name = 'admin'
    email = os.environ.get('SKY_ADMIN_USERNAME')
    password = os.environ.get('SKY_ADMIN_PASSWORD')
    admin_role = models.Role.query.filter_by(name='admin').first()
    if email is None or password is None or admin_role is None:
        return None
    admin = models.User(name=name, email=email, password=password, role=admin_role, active=True)
    db.session.add(admin)
    db.session.commit()
    return None


def shell_context():
    return dict(app=current_app, db=db, models=models, forms=forms)


manager.add_command('shell', Shell(make_context=shell_context))

if __name__ == '__main__':
    manager.run()
