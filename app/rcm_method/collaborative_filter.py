
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy import sparse


class CF:
    """Collaborative Filtering (User-User or Item-Item)."""
    def __init__(self, utility_matrix, k, dist_func=cosine_similarity, CF_type=1):
        self.CF_type = CF_type  # 1: User-User CF, 0: Item-Item CF
        self.utility_matrix = utility_matrix if CF_type else utility_matrix[:, [1, 0, 2]]
        self.k = k  # Number of neighbors
        self.dist_func = dist_func
        self.temp = None

        self.n_users = int(np.max(self.utility_matrix[:, 0])) + 1
        self.n_items = int(np.max(self.utility_matrix[:, 1])) + 1

    def add(self, new_data):
        self.utility_matrix = np.concatenate((self.utility_matrix, new_data), axis=0)

    def normalize(self):
        users = self.utility_matrix[:, 0]
        self.temp = self.utility_matrix.copy()
        # Initialization array[n_users] to save average rate value
        self.av = np.zeros(self.n_users)

        for n in range(self.n_users):
            ids = np.where(users == n)[0]
            ratings = self.utility_matrix[ids, 2]

            if len(ratings) > 0:
                self.av[n] = np.mean(ratings)

            self.temp[ids, 2] = ratings - self.av[n]

        # Sparse matrix representation
        self.normalized_utility = sparse.coo_matrix((self.temp[:, 2],
                                       (self.temp[:, 1], self.temp[:, 0])),
                                      shape=(self.n_items, self.n_users))
        self.normalized_utility = self.normalized_utility.tocsr()

    # Calculate similarity
    def similarity(self):
        self.S = self.dist_func(self.normalized_utility.T, self.normalized_utility.T)

    # When new reviews insert to DB, recalculate
    def refresh(self):
        self.normalize()
        self.similarity()

    def fit(self):
        self.refresh()

    #Predict rating of user u for item i.
    def __pred(self, u, i, normalized=1):
        ids = np.where(self.utility_matrix[:, 1] == i)[0]
        users_rated_i = self.utility_matrix[ids, 0].astype(int)

        sim = self.S[u, users_rated_i]
        a = np.argsort(sim)[-self.k:]
        nearest_s = sim[a]
        r = self.normalized_utility[i, users_rated_i[a]]

        if normalized:
            return (r * nearest_s).sum() / (np.abs(nearest_s).sum() + 1e-8)

        return (r * nearest_s).sum() / (np.abs(nearest_s).sum() + 1e-8) + self.av[u]

    #  Prediction
    def pred(self, u, i, normalized=1):
        if self.CF_type:
            return self.__pred(u, i, normalized)
        return self.__pred(i, u, normalized)

    def recommend(self, u, normalized=1):
        ids = np.where(self.utility_matrix[:, 0] == u)[0]
        items_rated_by_u = self.utility_matrix[ids, 1].tolist()

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
            if self.CF_type:
                print(f'  Recommend these products {top_5_items} to user {u}')
            else:
                print(f'  Recommend product with id: {u} to users {top_5_items}')