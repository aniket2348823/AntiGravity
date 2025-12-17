from flask import Flask, jsonify, send_file, request
from flask_cors import CORS
import scan_engine
import db
import pdf_generator
import os

app = Flask(__name__)
CORS(app)

# Initialize DB
db.init_db()

@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.json
    target_url = data.get('target_url')
    
    if not target_url:
        return jsonify({"status": "error", "message": "Target URL is required"}), 400

    if scan_engine.scan_manager.start_scan(target_url):
        return jsonify({"status": "started", "message": f"Scan started on {target_url}"})
    else:
        return jsonify({"status": "error", "message": "A scan is already in progress."}), 409

@app.route('/api/status', methods=['GET'])
def get_status():
    is_running = scan_engine.scan_manager.is_scanning()
    real_time_data = scan_engine.scan_manager.get_realtime_data()
    return jsonify({
        "is_scanning": is_running,
        "logs": real_time_data.get("log", []),
        "current_findings": real_time_data.get("findings", [])
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    scans = db.get_all_scans()
    # Adding target info to history view would require DB schema update or extracting from result
    return jsonify(scans)

@app.route('/api/report/<int:scan_id>', methods=['GET'])
def get_report(scan_id):
    scan = db.get_scan(scan_id)
    if not scan:
        return jsonify({"error": "Scan not found"}), 404
    
    report_filename = f"report_{scan_id}.pdf"
    report_path = os.path.join(os.getcwd(), report_filename)
    
    pdf_generator.generate_pdf(scan, report_path)
    
    return send_file(report_path, as_attachment=True, download_name=report_filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
