from app import create_app

# Khởi tạo và chạy Flask app
app = create_app()

if __name__ == "__main__":
    app.run(port=5555, debug=True)
