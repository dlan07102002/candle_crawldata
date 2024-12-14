# controller/product_controller.py
from flask import jsonify, request

from candlelight.model.product_model import ProductModel

product_model = ProductModel()

def get_recommendations():
    if product_model.df_products.empty:
        return jsonify({"Error": "No products available in the database."})

    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"Error": "Missing 'product_id' parameter."})

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"Error": "'product_id' must be an integer."})

    # Kiểm tra `product_id` có tồn tại
    if product_id not in product_model.df_products["product_id"].values:
        return jsonify({'Error': 'Product ID is not available'})

    index_product = product_model.df_products[product_model.df_products["product_id"] == product_id].index[0]

    # So sánh sản phẩm
    similarProducts = list(enumerate(product_model.similar[index_product]))
    sortedSimilarProduct = sorted(similarProducts, key=lambda x: x[1], reverse=True)

    result = []
    for i in range(1, 6):  # Lấy 5 sản phẩm tương tự
        result.append(sortedSimilarProduct[i][0])

    data = {"Recommend": result}
    return jsonify(data)
