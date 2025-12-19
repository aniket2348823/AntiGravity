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
        
        <!-- New Vulnerabilities -->
        <a href="/api/search?q=test">Search (SQLi)</a>
        <a href="/api/echo?q=hello">Echo (XSS)</a>
        <a href="/api/orders/1">Order 1 (IDOR)</a>
        <a href="/api/coupon">Claim (Race)</a>
        <a href="/api/admin/data">Admin (Auth Bypass)</a>
        
        <!-- v20.0 Omniscient Vectors -->
        <a href="/api/buy_step1">Start Checkout (Stateful)</a>
        <a href="/api/protected_waf">WAF Protected (Mutation)</a>
        
        <!-- v30.0 Aether Vectors -->
        <a href="/api/desync">Test Desync (CL.TE)</a>
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

# --- 5. SQL Injection ---
@app.route('/api/search')
def search():
    query = request.args.get('q', '')
    # Vulnerable to ' OR 1=1 --
    if "'" in query or "OR 1=1" in query.upper():
         return "Error: You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version"
    return "No results found."

# --- 6. Reflected XSS ---
@app.route('/api/echo')
def echo():
    query = request.args.get('q', '')
    # Vulnerable to <script>
    if "<script>" in query:
        return f"Results for: {query}" # Unescaped reflection
    return "Search for something."

# --- 7. IDOR ---
@app.route('/api/orders/<int:order_id>')
def get_order(order_id):
    # Simulate IDOR: Any ID works and returns valid JSON
    return jsonify({
        "order_id": order_id,
        "amount": 100 * order_id,
        "customer": "Generic Customer"
    })

# --- 8. Race Condition (The Chronomancer) ---
# Global coupon limit
COUPON_LIMIT = 1
coupons_claimed = 0

@app.route('/api/coupon', methods=['POST'])
def claim_coupon():
    global coupons_claimed
    # Simulate TOCTOU: Check first
    if coupons_claimed >= COUPON_LIMIT:
        return jsonify({"status": "failed", "error": "Coupons exhausted"}), 400
    
    # Simulate IO Delay (Time Gap)
    time.sleep(0.005) # 5ms gap
    
    # Use
    coupons_claimed += 1
    return jsonify({"status": "success", "msg": "Coupon claimed!"}), 200

@app.route('/api/reset_coupons', methods=['POST'])
def reset_coupons():
    global coupons_claimed
    coupons_claimed = 0
    return "Reset OK"

# --- 9. Auth Bypass (Doppelganger) ---
@app.route('/api/admin/data', methods=['GET'])
def admin_data():
    # Vulnerable: Checks for header, but allows any value or no real token validation
    # in a real Doppelganger scenario, we'd test if a low-priv token works.
    # Here, we simulate that even a "user" token works for this admin endpoint.
    auth = request.headers.get('Authorization')
    if auth:
        return jsonify({"secret": "Admin Data Leaked", "role": "admin"})
    return "Unauthorized", 401

# --- 10. Stateful Logic Flow (Checkout) ---
@app.route('/api/buy_step1')
def buy_step1():
    return """
    <html><body>
        <h1>Step 1: Shipping</h1>
        <form action="/api/buy_step2" method="POST">
            <input name="address" type="text" />
            <button type="submit">Next: Payment</button>
        </form>
    </body></html>
    """

@app.route('/api/buy_step2', methods=['POST', 'GET'])
def buy_step2():
    return """
    <html><body>
        <h1>Step 2: Payment</h1>
        <form action="/api/buy_complete" method="POST">
            <input name="cc" type="text" />
            <button type="submit">Complete Order</button>
        </form>
    </body></html>
    """
    
@app.route('/api/buy_complete', methods=['POST', 'GET'])
def buy_complete():
    return jsonify({"status": "Order Placed", "flow": "complete"})

# --- 11. WAF Simulation (Adversarial Mutation) ---
@app.route('/api/protected_waf')
def protected_waf():
    # Only allows requests with specific adversarial bypass
    # e.g., &bypass=... (simulating a mutation found by feedback loop)
    # The mutator tries: lambda p: p + "&bypass=true"
    bypass = request.args.get('bypass')
    if bypass and "true" in bypass:
         return jsonify({"status": "Bypassed", "secret": "WAF_Bypassed_1337"})
    return "Forbidden: Blocked by AI WAF", 403

# --- 12. Protocol Desync (CL.TE Simulation) ---
@app.route('/api/desync', methods=['POST', 'GET'])
def desync_sim():
    # Simulation: specific bad headers cause a "hang" or 500
    # In Flask, we can't easily hang the socket at raw level without middleware,
    # but we can check headers to simulate the response scanners look for.
    if request.headers.get('Transfer-Encoding') and request.headers.get('Content-Length'):
        # Conflicting headers!
        return "Internal Server Error: Desynchronization Detected", 500
    return "OK"

if __name__ == '__main__':
    # Threaded=True to handle concurrent requests from scanner
    app.run(port=5051, threaded=True)
