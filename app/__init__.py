from flask_bootstrap import Bootstrap
from flask import Flask
import os, config
app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.DevelopementConfig')

from . import views
# app.config['SECRET_KEY'] = 'YsXpm3myJCgJa'
# bootstrap = Bootstrap(app)
# if __name__ == "__main__":
#     app.run(debug=True)
