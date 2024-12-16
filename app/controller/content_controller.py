from flask import Blueprint, jsonify

from candlelight.app.models.content_model import ProductModel


# Khởi tạo blueprint cho content
content_blueprint = Blueprint('content', __name__)

# Route cho API content
@content_blueprint.route("/<int:product_id>", methods=["GET"])
def get_cb_recommendation(product_id):
    product_model = ProductModel()

    # Kiểm tra nếu dữ liệu sản phẩm trống
    if product_model.df_products.empty:
        return jsonify({"error": "No products available in the database."}), 404

    # Kiểm tra nếu product_id không tồn tại trong cơ sở dữ liệu
    if product_id not in product_model.df_products["product_id"].values:
        return jsonify({"error": f"Product ID {product_id} does not exist."}), 404

    try:
        # Lấy danh sách các sản phẩm tương tự từ ProductModel
        similar_products = product_model.get_similar_products(product_id, top_n=4)

        # Trả về danh sách sản phẩm tương tự
        return jsonify({"contentBased": similar_products})
    except Exception as e:
        # Xử lý lỗi và log chi tiết nếu có
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
