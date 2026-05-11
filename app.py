from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from routes.auth import auth
from routes.shop import shop
from routes.cart import cart
from routes.admin import admin


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Войдите в аккаунт."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    app.register_blueprint(auth)
    app.register_blueprint(shop)
    app.register_blueprint(cart)
    app.register_blueprint(admin)

    with app.app_context():
        db.create_all()
        _seed(app)

    return app


def _seed(app):
    from models import Category, Product
    if Category.query.first():
        return
    cats = ["Электроника", "Одежда", "Книги", "Дом и сад"]
    for name in cats:
        db.session.add(Category(name=name))
    db.session.flush()

    electronics = Category.query.filter_by(name="Электроника").first()
    books = Category.query.filter_by(name="Книги").first()

    sample_products = [
        Product(name="Смартфон XPro", description="Мощный смартфон с отличной камерой.", price=29990, stock=15, category_id=electronics.id),
        Product(name="Ноутбук UltraBook", description="Тонкий и лёгкий ноутбук для работы.", price=59990, stock=8, category_id=electronics.id),
        Product(name="Наушники BassMax", description="Беспроводные наушники с шумоподавлением.", price=4990, stock=30, category_id=electronics.id),
        Product(name="Чистый код", description="Роберт Мартин. Обязательная книга для разработчика.", price=990, stock=20, category_id=books.id),
        Product(name="Python для всех", description="Отличная книга для изучения Python с нуля.", price=790, stock=25, category_id=books.id),
    ]
    for p in sample_products:
        db.session.add(p)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
