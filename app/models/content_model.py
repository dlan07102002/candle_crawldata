# model/content_model.py
import pandas as pd
from sqlalchemy import create_engine
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class ProductModel:
    def __init__(self):
        self.df_products = pd.DataFrame()
        self.similar = None
        self.engine = None  # Khởi tạo engine
        self._init_engine()
        self._load_data()

    def _init_engine(self):
        try:
            self.engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")
        except Exception as e:
            print(f"Error initializing database engine: {e}")
            self.engine = None

    def _load_data(self):
        """Tải dữ liệu từ cơ sở dữ liệu và xử lý ban đầu."""
        if self.engine is None:
            print("Database engine is not initialized.")
            return

        try:
            # Đọc dữ liệu từ bảng products và liên kế
            self.df_products = pd.read_sql("""
                SELECT 
                    p.product_id, 
                    description, 
                    sell_price, 
                    product_name, 
                    c.category_id, 
                    category_name 
                FROM candlelight_dev.products p 
                JOIN product_category pc ON p.product_id = pc.product_id  
                JOIN categories c ON c.category_id = pc.category_id 
                ORDER BY p.product_id
            """, self.engine)

            if self.df_products.empty:
                raise ValueError("Table 'products' is empty!")

            # Kiểm tra các cột cần thiết
            required_columns = {"description", "sell_price", "category_name"}
            missing_columns = required_columns - set(self.df_products.columns)
            if missing_columns:
                raise ValueError(f"Missing columns in the dataset: {missing_columns}")

            # Tạo đặc trưng kết hợp và tính toán ma trận tương đồng
            self._generate_features()
        except Exception as e:
            print(f"Error loading data: {e}")
            self.df_products = pd.DataFrame()  # Tạo DataFrame trống
        finally:
            # Đóng kết nối
            if self.engine:
                self.engine.dispose()
                print("MySQL connection closed.")

    def _generate_features(self):
        """Tạo đặc trưng kết hợp và tính toán ma trận TF-IDF."""
        if self.df_products.empty:
            print("No data available to generate features.")
            self.similar = None
            return

        try:
            # Hàm kết hợp các đặc trưng
            def combine_features(row):
                return f"{row['sell_price']} {row['description']} {row['category_name']}"

            self.df_products["combinedFeatures"] = self.df_products.apply(combine_features, axis=1)

            # Tạo ma trận TF-IDF
            tf = TfidfVectorizer()
            tf_matrix = tf.fit_transform(self.df_products["combinedFeatures"])

            # Tính toán độ tương đồng cosine
            self.similar = cosine_similarity(tf_matrix)
        except Exception as e:
            print(f"Error generating features: {e}")
            self.similar = None

    def get_similar_products(self, product_id, top_n=5):
        """
        Lấy danh sách các sản phẩm tương tự dựa trên ID sản phẩm.

        :param product_id: ID sản phẩm (int)
        :param top_n: Số lượng sản phẩm tương tự (int)
        :return: Danh sách ID sản phẩm tương tự (list)
        """
        if self.df_products.empty or self.similar is None:
            raise ValueError("No product data or similarity matrix available.")

        # Tìm chỉ mục sản phẩm
        try:
            product_index = self.df_products[self.df_products["product_id"] == product_id].index[0]
        except IndexError:
            raise ValueError(f"Product ID {product_id} not found.")

        # Tính toán sản phẩm tương tự
        similar_scores = list(enumerate(self.similar[product_index]))
        sorted_scores = sorted(similar_scores, key=lambda x: x[1], reverse=True)

        # Lấy top N sản phẩm (bỏ qua chính nó ở vị trí đầu tiên)
        similar_product_indices = [idx for idx, _ in sorted_scores[1:top_n + 1]]

        # Trả về danh sách product_id tương ứng
        return self.df_products.iloc[similar_product_indices]["product_id"].tolist()
