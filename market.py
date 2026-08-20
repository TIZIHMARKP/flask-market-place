from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return "Hello flaskMarket"

@app.route('/about/<username>')
def about_page(username):
    return f"<h1> About Page of {username} <h1>"



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8082, debug=True)

