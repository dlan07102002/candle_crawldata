# app.py
from flask import Flask
from flask_cors import CORS
from controller.product_controller import get_recommendations

app = Flask(__name__)

# Đăng ký CORS
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route("/api", methods=["GET"])
def api():
    return get_recommendations()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
