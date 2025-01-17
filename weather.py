from flask import Flask, render_template, request
import service

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        country = request.form.get("country")  # Get the country name from the form
        data = service.get_weather(country)  # Fetch data for the specified country
        
    else:
        # Default to Haifa if no search is performed
        data = service.get_weather("haifa")
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)
