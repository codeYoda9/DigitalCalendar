from flask import Flask

app = Flask(__name__)

@app.get("/")
def hello():
    return "Hello, World!\n"

if __name__ == "__main__":
    # 0.0.0.0 makes it reachable from outside the container
    app.run(host="0.0.0.0", port=8000)      