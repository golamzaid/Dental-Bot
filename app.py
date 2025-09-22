from flask import Flask, render_template, request, jsonify
from nlp import DentalNLP
from maps import geocode_address, find_dentists_near

app = Flask(__name__)
nlp = DentalNLP("kb/dental_conditions.yaml")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    text = data.get("text", "")
    lang, top = nlp.rank(text)   # now top is single dict not list
    loc = data.get("location")
    dentists = []
    if loc:
        ge = geocode_address(loc)
        if ge:
            dentists = find_dentists_near(ge[0], ge[1], radius=5000)
    return jsonify({"lang": lang, "result": top, "dentists": dentists})

if __name__ == "__main__":
    app.run(debug=True)
