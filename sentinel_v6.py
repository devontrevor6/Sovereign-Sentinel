from flask import Flask, Response
import os, time, json
app = Flask(__name__)
RAW_PATH = os.path.expanduser("~/Sentinel_Project/Vault/Raw_Cache")
def event_stream():
    processed_files = set()
    while True:
        if os.path.exists(RAW_PATH):
            current_files = set(os.listdir(RAW_PATH))
            new_files = current_files - processed_files
            for f in new_files:
                yield f"data: {json.dumps({'file': f, 'time': time.strftime('%H:%M:%S')})}\n\n"
                processed_files.add(f)
        time.sleep(1)
@app.route('/stream')
def stream():
    return Response(event_stream(), mimetype="text/event-stream")
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8887)
