from flask import Flask, render_template_string
import os
app = Flask(__name__)
VAULT_PATH = os.path.expanduser("~/Sentinel_Project/Vault/Filed_Intel")
@app.route('/')
def index():
    batches = sorted(os.listdir(VAULT_PATH), reverse=True) if os.path.exists(VAULT_PATH) else []
    return "<h1>SENTINEL DATA APP v1.0</h1>"
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8887)
