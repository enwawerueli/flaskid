#!/usr/bin/env python
import os

from flask_script import Manager

from app import create_app
from app.views import blueprints


app = create_app(os.environ.get('FLASKY_ENV') or 'default')
for blueprint in blueprints:
    app.register_blueprint(blueprint)
manager = Manager(app)


if __name__ == '__main__':
    manager.run()
