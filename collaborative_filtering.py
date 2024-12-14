import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse
from sqlalchemy import create_engine

from candlelight.recommend_filter import CF

# Load data from db
engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")
df_products = pd.read_sql("SELECT user_id, product_id, rate from reviews", engine)

Y_data = df_products.to_numpy()
Y_data[:, :2] -= 1
Y_data = Y_data.astype(int)
# Instantiate and fit the model
rs = CF(Y_data, k=0, uuCF=1)
rs.fit()

recommended_items_for_user_125 = rs.recommend(125)
print(recommended_items_for_user_125)

# Evaluate the model
n_tests = Y_data.shape[0]
SE = 0  # Squared error

for n in range(n_tests):
    pred = rs.pred(Y_data[n, 0], Y_data[n, 1], normalized=0)
    SE += (pred - Y_data[n, 2]) ** 2

RMSE = np.sqrt(SE / n_tests)
print('Item-item CF, RMSE =', RMSE)
