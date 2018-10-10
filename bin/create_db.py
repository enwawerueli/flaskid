#!/usr/bin/env python

import os
import sys
sys.path.append(os.getcwd())

from app import create_app
from app.models import db


if __name__ == '__main__':
    app = create_app(os.environ.get('FLASKY_ENV') or 'default')
    with app.app_context():
        db.create_all()
