
from market import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Tables created successfully")
    app.run(host='0.0.0.0', port=8082, debug=True)

