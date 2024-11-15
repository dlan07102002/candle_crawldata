from sqlalchemy import create_engine
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify, request

app = Flask(__name__)

# SQLAlchemy connection string
engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")

try:
    # Đọc bảng `products` từ cơ sở dữ liệu
    df_products = pd.read_sql("SELECT * FROM products", engine)

    if df_products.empty:
        raise ValueError("Table 'products' is empty!")
    print(df_products.head())

    # Các cột cần thiết
    features = ["description", "sell_price"]

    # Kiểm tra cột có tồn tại
    for feature in features:
        if feature not in df_products.columns:
            raise ValueError(f"Column '{feature}' is missing in the 'products' table.")

except Exception as e:
    print(f"Error: {e}")
    df_products = pd.DataFrame()  # Tạo DataFrame trống để ngăn mã bị crash
finally:
    # Đóng kết nối SQLAlchemy
    engine.dispose()
    print("MySQL connection closed.")


# Hàm kết hợp đặc trưng
def combine_features(row):
    return f"{row['sell_price']} {row['description']}"


if not df_products.empty:
    df_products["combinedFeatures"] = df_products.apply(combine_features, axis=1)

    # Tạo ma trận TF-IDF
    tf = TfidfVectorizer()
    tfMatrix = tf.fit_transform(df_products["combinedFeatures"])

    # Tính toán độ tương đồng cosine
    similar = cosine_similarity(tfMatrix)
else:
    tfMatrix = None
    similar = None


@app.route("/api", methods=["GET"])
def get_data():
    if df_products.empty:
        return jsonify({"Error": "No products available in the database."})

    product_id = request.args.get("product_id")
    if not product_id:
        return jsonify({"Error": "Missing 'product_id' parameter."})

    try:
        product_id = int(product_id)
    except ValueError:
        return jsonify({"Error": "'product_id' must be an integer."})

    # Kiểm tra `product_id` có tồn tại
    if product_id not in df_products["product_id"].values:
        return jsonify({'Error': 'Product ID is not available'})

    index_product = df_products[df_products["product_id"] == product_id].index[0]

    # So sánh sản phẩm
    similarProducts = list(enumerate(similar[index_product]))
    sortedSimilarProduct = sorted(similarProducts, key=lambda x: x[1], reverse=True)

    # Hàm lấy tên sản phẩm
    def get_name(index):
        return df_products.iloc[index]["product_name"]

    result = []
    for i in range(1, 6):  # Lấy 5 sản phẩm tương tự
        result.append(get_name(sortedSimilarProduct[i][0]))

    data = {"Recommend": result}
    return jsonify(data)


if __name__ == "__main__":
    app.run(port=5555)
