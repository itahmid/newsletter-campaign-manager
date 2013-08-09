from pipmail import app
from pipmail.controllers import newsletters, lists, recipients, contents, users, templates, deliveries


if __name__ == '__main__':
    app.register_blueprint(newsletters.mod)
    app.register_blueprint(lists.mod)
    app.register_blueprint(recipients.mod)
    app.register_blueprint(users.mod)
    app.register_blueprint(contents.mod)
    app.register_blueprint(templates.mod)
    app.register_blueprint(deliveries.mod)
    app.run(host='0.0.0.0', port=5000, debug=True)
