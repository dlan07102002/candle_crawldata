
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


class CF:
    """Collaborative Filtering (User-User or Item-Item)."""
    def __init__(self, Y_data, k, dist_func=cosine_similarity, uuCF=1):
        self.uuCF = uuCF  # 1: User-User CF, 0: Item-Item CF
        self.Y_data = Y_data if uuCF else Y_data[:, [1, 0, 2]]
        self.k = k  # Number of neighbors
        self.dist_func = dist_func
        self.Ybar_data = None

        self.n_users = int(np.max(self.Y_data[:, 0])) + 1
        self.n_items = int(np.max(self.Y_data[:, 1])) + 1

    def add(self, new_data):
        self.Y_data = np.concatenate((self.Y_data, new_data), axis=0)

    def normalize_Y(self):
        users = self.Y_data[:, 0]
        self.Ybar_data = self.Y_data.copy()
        # Initialization array[n_users] to save average rate value
        self.mu = np.zeros(self.n_users)

        for n in range(self.n_users):
            ids = np.where(users == n)[0]
            ratings = self.Y_data[ids, 2]

            if len(ratings) > 0:
                self.mu[n] = np.mean(ratings)

            self.Ybar_data[ids, 2] = ratings - self.mu[n]

        # Sparse matrix representation
        self.Ybar = sparse.coo_matrix((self.Ybar_data[:, 2],
                                       (self.Ybar_data[:, 1], self.Ybar_data[:, 0])),
                                      shape=(self.n_items, self.n_users))
        self.Ybar = self.Ybar.tocsr()

    # Calculate similarity
    def similarity(self):
        self.S = self.dist_func(self.Ybar.T, self.Ybar.T)

    # When new reviews insert to DB, recalculate
    def refresh(self):
        self.normalize_Y()
        self.similarity()

    def fit(self):
        self.refresh()

    #Predict rating of user u for item i.
    def __pred(self, u, i, normalized=1):
        ids = np.where(self.Y_data[:, 1] == i)[0]
        users_rated_i = self.Y_data[ids, 0].astype(int)

        sim = self.S[u, users_rated_i]
        a = np.argsort(sim)[-self.k:]
        nearest_s = sim[a]
        r = self.Ybar[i, users_rated_i[a]]

        if normalized:
            return (r * nearest_s).sum() / (np.abs(nearest_s).sum() + 1e-8)

        return (r * nearest_s).sum() / (np.abs(nearest_s).sum() + 1e-8) + self.mu[u]

    #  Prediction
    def pred(self, u, i, normalized=1):
        if self.uuCF:
            return self.__pred(u, i, normalized)
        return self.__pred(i, u, normalized)

    def recommend(self, u, normalized=1):
        ids = np.where(self.Y_data[:, 0] == u)[0]
        items_rated_by_u = self.Y_data[ids, 1].tolist()

        recommended_items = []
        for i in range(self.n_items):
            if i not in items_rated_by_u:
                rating = self.pred(u, i, normalized)
                if rating > 0:
                    recommended_items.append(i)

        return recommended_items[:5]

    def print_recommendation(self):
        print('Recommendations:')
        for u in range(self.n_users):
            recommended_items = self.recommend(u)
            top_5_items = recommended_items[:5]  # Lấy 5 sản phẩm đầu tiên
            if self.uuCF:
                print(f'  Recommend these products {top_5_items} to user {u}')
            else:
                print(f'  Recommend product with id: {u} to users {top_5_items}')

