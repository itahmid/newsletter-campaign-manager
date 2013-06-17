from pipmail import app
from pipmail.controllers import campaigns, lists, recipients, contents, users, templates


if __name__ == '__main__':
    app.register_blueprint(campaigns.mod)
    app.register_blueprint(lists.mod)
    app.register_blueprint(recipients.mod)
    app.register_blueprint(users.mod)
    app.register_blueprint(contents.mod)
    app.register_blueprint(templates.mod)
    app.run(host='0.0.0.0', port=5000, debug=True)
