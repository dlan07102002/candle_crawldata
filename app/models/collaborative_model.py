import pandas as pd
import numpy as np
from sqlalchemy import create_engine

from candlelight.app.rcm_method.collaborative_filter import CF


class RecommendationModel:
    def __init__(self):
        # Kết nối cơ sở dữ liệu
        self.engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")
        self.df_products = pd.read_sql("SELECT user_id, product_id, rate FROM reviews", self.engine)

        # Chuyển đổi dữ liệu thành numpy array để xử lý
        self.utility = self.df_products.to_numpy()
        self.utility = self.utility.astype(int)

        # Khởi tạo hệ thống recommendation
        self.rs = CF(self.utility, k=32, CF_type=0)
        self.rs.fit()


    def recommend(self, user_id):
        # Lấy recommendation cho user cụ thể

        return self.rs.recommend(user_id)

    def evaluate(self):
        # Đánh giá mô hình bằng RMSE, MSE, MAE
        n_tests = self.utility.shape[0]
        SE = 0  # Squared error
        AE = 0  # Absolute error
        for n in range(n_tests):
            pred = self.rs.pred(self.utility[n, 0], self.utility[n, 1], normalized=0)
            SE += (pred - self.utility[n, 2]) ** 2
            AE += abs(pred - self.utility[n, 2])
        MSE = (SE / n_tests)
        RMSE = np.sqrt(SE / n_tests)
        MAE = AE/n_tests

        res = {}
        res["RMSE"] = RMSE
        res["MSE"] = MSE
        res["MAE"] = MAE

        return res
