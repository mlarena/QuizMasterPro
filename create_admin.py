from app import create_app, db, logger
from app.models import User

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin123')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
            logger.info('Admin user created successfully')
        else:
            logger.info('Admin user already exists')

if __name__ == '__main__':
    create_admin_user()