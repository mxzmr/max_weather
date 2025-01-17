from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import service

app = Flask(__name__)
load_dotenv()

@app.route("/", methods=["GET", "POST"])
def home():
    data = None
    error = False
    if request.method == "POST":
        city = request.form.get("country")
        try:
            data = service.get_weather(city)
            if not data or not data.get("weather"):
                error = True
        except Exception:
            error = True
    return render_template("index.html", data=data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
