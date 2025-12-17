from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    # Intentionally missing security headers
    return "Welcome to the vulnerable app."

@app.route('/admin')
def admin():
    # Intentionally accessible admin panel
    return "Admin Panel - Sensitive Info Here"

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        return "Logged in"
    return "Login Page"

@app.route('/.env')
def env():
    # Intentionally exposed env file
    return "SECRET_KEY=123456"

if __name__ == '__main__':
    app.run(port=5050)
