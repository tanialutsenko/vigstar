from flask import Flask, render_template, url_for, request, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tryiu859jgnbcgfy74lh8d9j'

menu = [{"name":"установка", "url": "install-flash"},
        {"name" :"первое приложение", "url": "first-app"},
        { "name" :"обратная связь", "url": "contact"}]

# get_flash_messages = ['Сообщение отправлено','Ошибка отправления']

@app.route("/")
def index():
    print(url_for('index'))
    return render_template('index.html', menu = menu )

@app.route("/about")
def about():
    print(url_for('about'))
    return render_template('about.html', title = "О сайте", menu = menu)

@app.route("/profile/<username>")
def profile(username):
    return render_template('base.html',title = f"Пользователь{username}")

@app.route("/contact", methods = ["POST", "GET"])
def contact():
    if request.method == "POST":
        if len(request.form['username'])>2:
            flash('Сообщение отправлено',category = 'success')
        else:
            flash('Ошибка отправления', category = 'error')
    return render_template('contact.html', title = "Обратная связь",menu = menu)

# with app.test_request_context():
#     print(url_for('about'))
#     print(url_for('index'))
#     print(url_for('profile', username="self"))


if __name__ == "__main__":
    app.run(debug=True)