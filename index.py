from sqlalchemy import create_engine
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, jsonify

app = Flask(__name__)
# SQLAlchemy connection string
engine = create_engine("mysql+mysqlconnector://spring:spring@localhost/candlelight_dev")

try:
    # Read products table into DataFrame
    df_products = pd.read_sql("SELECT * FROM products", engine)
    print(df_products.head())

    features = ["description", "list_price"]

except Exception as e:
    print(f"Error: {e}")
finally:
    # Close SQLAlchemy engine connection
    engine.dispose()
    print("MySQL connection closed.")

def combinefeatures(row):
    return str(row["list_price"]) + " " + str(row["description"])

df_products["combinedFeatures"] = df_products.apply(combinefeatures, axis=1)

tf = TfidfVectorizer()
tfMatrix = tf.fit_transform(df_products["combinedFeatures"])

similar = cosine_similarity(tfMatrix)

# first item for compare
similarProducts = list(enumerate(similar[0]))

sortedSimilarProduct = sorted(similarProducts, key = lambda x:x[1], reverse=True)

def get_name(index):
    return (df_products[df_products.index == index]["product_name"].values[0])

number = 5
ketQua = []
for i in range(1, number + 1):
    print(get_name(sortedSimilarProduct[i][0]))
    ketQua.append(get_name(sortedSimilarProduct[i][0]))

@app.route("/api", methods = ["GET"])
def get_data():
    data = {"Recommend:": ketQua}
    return jsonify(data)

if __name__ == "__main__":
    app.run(port=5555)
