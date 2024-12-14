from flask import Blueprint, jsonify

from candlelight.app.models.collaborative_model import RecommendationModel

# Khởi tạo blueprint cho recommendation
recommendation_blueprint = Blueprint('recommendation', __name__)

# Khởi tạo mô hình recommendation
recommendation_model = RecommendationModel()

# Route cho API recommendation
@recommendation_blueprint.route("/", methods=["GET"])
def get_recommendations():
    try:
        user_id = 125  # User ID có thể được truyền qua tham số query hoặc động
        recommended_items = recommendation_model.recommend(user_id)
        return jsonify({"user_id": user_id, "recommended_items": recommended_items.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
