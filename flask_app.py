from application import create_app
from application.models import db

app = create_app('ProductionConfig')


# Creates all database tables
with app.app_context():
    # db.drop_all()  # Commented out - only use to reset database if needed
    db.create_all()

if __name__ == '__main__':
    app.run()
