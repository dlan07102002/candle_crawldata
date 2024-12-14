import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from candlelight.app.filter.collaborative_filter import CF


class RecommendationModel:
    def __init__(self):
        # Kết nối cơ sở dữ liệu
        self.engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")
        self.df_products = pd.read_sql("SELECT user_id, product_id, rate FROM reviews", self.engine)

        # Chuyển đổi dữ liệu thành numpy array để xử lý
        self.Y_data = self.df_products.to_numpy()
        self.Y_data = self.Y_data.astype(int)

        # Khởi tạo hệ thống recommendation
        self.rs = CF(self.Y_data, k=32, uuCF=0)
        self.rs.fit()


    def recommend(self, user_id):
        # Lấy recommendation cho user cụ thể

        return self.rs.recommend(user_id)

    def evaluate(self):
        # Đánh giá mô hình bằng RMSE
        n_tests = self.Y_data.shape[0]
        SE = 0  # Squared error

        for n in range(n_tests):
            pred = self.rs.pred(self.Y_data[n, 0], self.Y_data[n, 1], normalized=0)
            SE += (pred - self.Y_data[n, 2]) ** 2

        RMSE = np.sqrt(SE / n_tests)
        return RMSE
