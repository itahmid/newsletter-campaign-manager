from pipmail import app
from pipmail.controllers import campaigns, subscribers


if __name__ == '__main__':
    app.register_blueprint(campaigns.mod)
    app.register_blueprint(subscribers.mod)
    app.run(host='0.0.0.0', port=5000, debug=True)
