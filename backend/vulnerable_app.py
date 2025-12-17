from flask import Flask, request, jsonify, send_file
import time
import io

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <body>
        <h1>Vulnerable App</h1>
        <a href="/users">Users (PII)</a>
        <a href="/api/profile?id=1">Profile</a>
        <script src="/static/app.js"></script>
    </body>
    </html>
    """

# --- 1. Soft 404 Simulation ---
@app.route('/product/<id>')
def product(id):
    # Always returns 200, even if product "doesn't exist"
    # This should be detected as a Soft 404 by SimHash
    return f"""
    <html>
    <head><title>Product Page</title></head>
    <body>
        <div class="content">
            <h1>We could not find the product you are looking for</h1>
            <p>Sorry, the item with ID {id} is not available in our catalog.</p>
            <a href="/">Go Home</a>
        </div>
    </body>
    </html>
    """

# --- 2. PII Leakage ---
@app.route('/users')
def users():
    return jsonify([
        {"id": 1, "name": "Alice", "email": "alice.wonderland@example.com"},
        {"id": 2, "name": "Bob", "phone": "+1-555-0199", "notes": "VIP customer"},
        {"id": 3, "name": "Charlie", "ssn": "123-45-6789", "debug": "User object dump"}
    ])

# --- 3. Mass Assignment / Param Miner ---
@app.route('/api/profile')
def profile():
    # Helper to simulate processing time
    if request.args.get('admin') == 'true':
        time.sleep(0.3) # 300ms latency increase
        return jsonify({
            "id": 1, 
            "username": "admin_user", 
            "role": "admin", 
            "permissions": ["read", "write", "delete"],
            "debug_trace": "A" * 2000 # Size increase
        })
    
    return jsonify({
        "id": 1, 
        "username": "regular_user", 
        "role": "user"
    })

# --- 4. Deep JS Analysis (Source Map) ---
@app.route('/static/app.js')
def js_file():
    return """
    console.log("Welcome to the app");
    var secret_api = "https://internal-api.dev/v1";
    //# sourceMappingURL=app.js.map
    """, 200, {'Content-Type': 'application/javascript'}

@app.route('/static/app.js.map')
def js_map():
    # Fake source map
    return jsonify({
        "version": 3,
        "file": "app.js",
        "sources": ["app.ts"],
        "names": [],
        "mappings": "AAAA,OAAO,GAAG,CAAC,GAAG,CAAC,oBAAoB,CAAC,CAAC"
    })

if __name__ == '__main__':
    # Threaded=True to handle concurrent requests from scanner
    app.run(port=5050, threaded=True)
