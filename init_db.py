from app import create_app, db, logger

def init_db():
    app = create_app()
    with app.app_context():
        try:
            db.create_all()
            logger.info('Database initialized successfully')
        except Exception as e:
            logger.error(f'Error initializing database: {str(e)}')
            raise

if __name__ == '__main__':
    init_db()