from flask import Flask, render_template

app = Flask(__name__)

menu = ["установка", "первое приложение", "обратная связь"]
@app.route("/")
def index():
    return render_template('index.html', menu = menu )

@app.route("/about")
def about():
    return "<h1> О Flask </h1>"

if __name__ == "__main__":
    app.run(debug=True)

