from flask import Blueprint, jsonify

from candlelight.app.models.collaborative_model import RecommendationModel

# Khởi tạo blueprint cho collaborative
collaborative_blueprint = Blueprint('collaborative', __name__)

# Route cho API collaborative
@collaborative_blueprint.route("/<int:user_id>", methods=["GET"])
def get_collaborative_recommendations(user_id):
    try:
        recommendation_model = RecommendationModel()
        # Ví dụ lấy collaborative recommendations cho user 125
        recommended_items = recommendation_model.recommend(user_id)
        return jsonify({"user_id": user_id, "CFBased": recommended_items})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@collaborative_blueprint.route("/evaluate", methods=["GET"])
def get_collaborative_evaluate():
    try:
        recommendation_model = RecommendationModel()
        return jsonify( recommendation_model.evaluate())
    except Exception as e:
        return jsonify({"error": str(e)}), 400

