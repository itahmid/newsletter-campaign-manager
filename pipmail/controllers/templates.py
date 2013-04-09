from flask import Blueprint, render_template, current_app


mod = Blueprint('templates', __name__)


@mod.route('/templates')
def index():
    return render_template('templates/index.html')
