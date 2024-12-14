# model/product_model.py
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ProductModel:
    def __init__(self):
        self.df_products = None
        self.similar = None
        self.engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")
        self._load_data()

    def _load_data(self):
        try:
            # Đọc bảng `products` từ cơ sở dữ liệu
            self.df_products = pd.read_sql(
                "SELECT p.product_id, description, sell_price, product_name, c.category_id, category_name FROM candlelight_dev.products p "
                "JOIN product_category pc ON p.product_id = pc.product_id  JOIN categories c ON c.category_id = pc.category_id "
                "ORDER BY p.product_id", self.engine
            )

            if self.df_products.empty:
                raise ValueError("Table 'products' is empty!")

            # Các cột cần thiết
            features = ["description", "sell_price", "category_name"]

            # Kiểm tra cột có tồn tại
            for feature in features:
                if feature not in self.df_products.columns:
                    raise ValueError(f"Column '{feature}' is missing in the 'products' table.")

            self._generate_features()
        except Exception as e:
            print(f"Error: {e}")
            self.df_products = pd.DataFrame()  # Tạo DataFrame trống để ngăn mã bị crash
        finally:
            # Đóng kết nối SQLAlchemy
            self.engine.dispose()
            print("MySQL connection closed.")

    def _generate_features(self):
        # Hàm kết hợp đặc trưng
        def combine_features(row):
            return f"{row['sell_price']} {row['description']} {row['category_name']}"

        if not self.df_products.empty:
            self.df_products["combinedFeatures"] = self.df_products.apply(combine_features, axis=1)

            # Tạo ma trận TF-IDF
            tf = TfidfVectorizer()
            tfMatrix = tf.fit_transform(self.df_products["combinedFeatures"])

            # Tính toán độ tương đồng cosine
            self.similar = cosine_similarity(tfMatrix)
