from flask import Flask
from flask_login import LoginManager
from flasgger import Swagger
from config import Config
from models import db, User
from extensions import cache, migrate
from routes.auth import auth
from routes.shop import shop
from routes.cart import cart
from routes.admin import admin
from routes.api import api

SWAGGER_CONFIG = {
    "title": "California Skateshop API",
    "uiversion": 3,
    "specs_route": "/api/docs/",
}


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    cache.init_app(app)
    Swagger(app, template={"info": {"title": "California Skateshop API", "version": "1.0"}})

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
    app.register_blueprint(api)

    with app.app_context():
        db.create_all()
        _seed(app)

    return app


def _seed(app):
    from models import Category, Product, OrderItem, Order, User, AboutPage
    from sqlalchemy import text

    if not AboutPage.query.first():
        db.session.add(AboutPage(
            title="California Skateshop",
            subtitle="Los Angeles, CA",
            description="California Skateshop — это магазин одежды и аксессуаров для тех, кто живёт скейт-культурой. Мы собрали всё лучшее из уличной моды Лос-Анджелеса: от классических скейт-образов до современных стилей Old Money, Y2K и Street Wear.\n\nНаш ассортимент охватывает все сезоны и любые поводы — будь то летний скейт-парк, зимняя прогулка или вечеринка в городе. Каждая вещь подобрана с вниманием к деталям и духу Калифорнии.",
            address="Los Angeles, California, USA\nMelrose Ave, 90046",
            phone="+1 (323) 555-0198",
            email="hello@californiaskateshop.com",
            hours_weekday="Пн–Пт: 10:00 — 21:00",
            hours_weekend="Сб–Вс: 11:00 — 20:00",
        ))
        db.session.commit()

    if not User.query.filter_by(username="Admin").first():
        admin = User(username="Admin", is_admin=True)
        admin.set_password("UiZPb6_2uq")
        db.session.add(admin)
        db.session.commit()

    all_categories = [
        "Футболки", "Худи и толстовки", "Штаны и шорты", "Обувь", "Аксессуары",
        "Old Money", "Casual", "Star Boy", "Street Wear",
        "Archive", "Sk8", "Y2K", "Classic", "Sport Wear",
        "Лето", "Зима", "Весна", "Осень",
    ]
    existing = {c.name for c in Category.query.all()}
    if existing == set(all_categories):
        return

    # Очищаем старые данные
    OrderItem.query.delete()
    Order.query.delete()
    Product.query.delete()
    Category.query.delete()
    db.session.flush()

    for name in all_categories:
        db.session.add(Category(name=name))
    db.session.flush()

    def cat(name):
        return Category.query.filter_by(name=name).first()

    CLOTH = "XS, S, M, L, XL, XXL"
    BOTTOM = "XS, S, M, L, XL, XXL"
    SHOE  = "38, 39, 40, 41, 42, 43, 44, 45"
    ONE   = "One Size"
    SOCK  = "36-39, 40-43, 44-46"

    products = [
        # Футболки
        Product(name="Tee California Logo", description="Классическая белая футболка с принтом California Skateshop. Плотный хлопок 100%.", price=2490, stock=40, sizes=CLOTH, category_id=cat("Футболки").id),
        Product(name="Tee Sunset Graphic", description="Оверсайз-футболка с графикой заката над Лос-Анджелесом.", price=2790, stock=25, sizes=CLOTH, category_id=cat("Футболки").id),
        Product(name="Tee Skate or Die Classic", description="Чёрная футболка с культовым принтом в стиле 90-х.", price=2290, stock=18, sizes=CLOTH, category_id=cat("Футболки").id),

        # Худи и толстовки
        Product(name="Hoodie Classic Black", description="Тяжёлый худи с вышитым логотипом. Начёс внутри, кенгуру-карман.", price=6990, stock=15, sizes=CLOTH, category_id=cat("Худи и толстовки").id),
        Product(name="Crewneck Palm Wave", description="Свитшот с принтом пальм и волны, свободный крой.", price=5490, stock=20, sizes=CLOTH, category_id=cat("Худи и толстовки").id),
        Product(name="Zip Hoodie Grey", description="Серый зип-худи с боковыми карманами, унисекс.", price=7490, stock=10, sizes=CLOTH, category_id=cat("Худи и толстовки").id),

        # Штаны и шорты
        Product(name="Чинос Skate Fit", description="Прямые чинос из плотного хлопка с усиленными коленями.", price=5990, stock=22, sizes=BOTTOM, category_id=cat("Штаны и шорты").id),
        Product(name="Карго Wide Leg", description="Широкие карго-штаны с множеством карманов.", price=6490, stock=14, sizes=BOTTOM, category_id=cat("Штаны и шорты").id),
        Product(name="Шорты Boardshort", description="Лёгкие шорты для скейтинга, длина до колена.", price=3290, stock=30, sizes=BOTTOM, category_id=cat("Штаны и шорты").id),

        # Обувь
        Product(name="Кеды Vulc Low White", description="Низкие вулканизированные кеды с плоской подошвой — классика скейтбординга.", price=8490, stock=12, sizes=SHOE, category_id=cat("Обувь").id),
        Product(name="Кеды High Top Black", description="Высокие кеды с усиленным носком и боковыми накладками.", price=9290, stock=9, sizes=SHOE, category_id=cat("Обувь").id),
        Product(name="Слипоны Skate Pro", description="Слипоны без шнурков, с липучкой и амортизирующей стелькой.", price=7290, stock=16, sizes=SHOE, category_id=cat("Обувь").id),

        # Аксессуары
        Product(name="Кепка 5-Panel Logo", description="Пятипанельная кепка с вышивкой California Skateshop.", price=1990, stock=35, sizes=ONE, category_id=cat("Аксессуары").id),
        Product(name="Носки Stripe Pack (3 пары)", description="Набор из 3 пар носков с полосками в фирменных цветах.", price=990, stock=60, sizes=SOCK, category_id=cat("Аксессуары").id),
        Product(name="Рюкзак Session Bag", description="Прочный рюкзак 20 л с отделением для скейтборда.", price=4990, stock=8, sizes=ONE, category_id=cat("Аксессуары").id),

        # Old Money
        Product(name="Polo Knit Cream", description="Вязаное поло молочного цвета, приталенный крой. Мериносовая шерсть.", price=8990, stock=12, sizes=CLOTH, category_id=cat("Old Money").id),
        Product(name="Trench Coat Beige", description="Классический бежевый тренч с поясом, длина миди.", price=21990, stock=6, sizes=CLOTH, category_id=cat("Old Money").id),
        Product(name="Oxford Shirt White", description="Белая оксфордская рубашка из хлопка, button-down воротник.", price=6490, stock=18, sizes=CLOTH, category_id=cat("Old Money").id),

        # Casual
        Product(name="Tee Basic Oversize", description="Оверсайз-футболка из плотного хлопка, без принта.", price=2290, stock=45, sizes=CLOTH, category_id=cat("Casual").id),
        Product(name="Chino Pants Sand", description="Прямые чинос песочного цвета, универсальный крой.", price=5490, stock=20, sizes=BOTTOM, category_id=cat("Casual").id),
        Product(name="Linen Shirt Blue", description="Льняная рубашка голубого цвета, свободный крой.", price=4990, stock=15, sizes=CLOTH, category_id=cat("Casual").id),

        # Star Boy
        Product(name="Satin Bomber Black", description="Атласный бомбер чёрного цвета с вышивкой на спине.", price=12990, stock=8, sizes=CLOTH, category_id=cat("Star Boy").id),
        Product(name="Mesh Jersey Graphic", description="Сетчатый джерси с крупным принтом, полупрозрачный.", price=4990, stock=14, sizes=CLOTH, category_id=cat("Star Boy").id),
        Product(name="Velvet Trousers Purple", description="Бархатные брюки фиолетового цвета, прямой крой.", price=9490, stock=7, sizes=BOTTOM, category_id=cat("Star Boy").id),

        # Street Wear
        Product(name="Hoodie California Drop", description="Дроп-худи с вышитым лого, плотный флис 450г.", price=8990, stock=20, sizes=CLOTH, category_id=cat("Street Wear").id),
        Product(name="Cargo Pants Black", description="Карго чёрные с боковыми карманами на молниях, широкий крой.", price=7490, stock=16, sizes=BOTTOM, category_id=cat("Street Wear").id),
        Product(name="Graphic Tee Cali Sun", description="Футболка с большим принтом калифорнийского солнца.", price=2990, stock=30, sizes=CLOTH, category_id=cat("Street Wear").id),

        # Archive
        Product(name="Vintage Denim Jacket", description="Джинсовая куртка с эффектом выцветания, архивный крой 90-х.", price=13990, stock=5, sizes=CLOTH, category_id=cat("Archive").id),
        Product(name="Windbreaker Retro", description="Ветровка с архивным логотипом, нейлон, подкладка в сетку.", price=9990, stock=9, sizes=CLOTH, category_id=cat("Archive").id),
        Product(name="Flannel Shirt Plaid", description="Фланелевая рубашка в клетку, оверсайз, тяжёлый хлопок.", price=5990, stock=11, sizes=CLOTH, category_id=cat("Archive").id),

        # Sk8
        Product(name="Tee Skate or Die", description="Чёрная футболка с принтом в стиле 90-х скейт-культуры.", price=2490, stock=25, sizes=CLOTH, category_id=cat("Sk8").id),
        Product(name="Кеды Vulc Low White Sk8", description="Низкие вулканизированные кеды с плоской подошвой.", price=8490, stock=12, sizes=SHOE, category_id=cat("Sk8").id),
        Product(name="Boardshort Sk8", description="Шорты для скейтинга с усиленными швами, длина до колена.", price=3490, stock=22, sizes=BOTTOM, category_id=cat("Sk8").id),

        # Y2K
        Product(name="Butterfly Top Silver", description="Топ с эффектом металлик и бабочками, облегающий крой.", price=3990, stock=14, sizes="XS, S, M, L", category_id=cat("Y2K").id),
        Product(name="Low Rise Jeans Blue", description="Джинсы с низкой посадкой, потёртости и стразы.", price=7990, stock=10, sizes=BOTTOM, category_id=cat("Y2K").id),
        Product(name="Visor Cap Holographic", description="Козырёк с голографическим покрытием, регулируемый.", price=2290, stock=20, sizes=ONE, category_id=cat("Y2K").id),

        # Classic
        Product(name="White Tee Essential", description="Базовая белая футболка из 100% хлопка, плотность 200г.", price=1990, stock=60, sizes=CLOTH, category_id=cat("Classic").id),
        Product(name="Black Crewneck", description="Чёрный свитшот без принта, прямой крой, начёс.", price=5490, stock=25, sizes=CLOTH, category_id=cat("Classic").id),
        Product(name="Denim Straight Jeans", description="Прямые джинсы тёмно-синего цвета, классический крой.", price=6990, stock=18, sizes=BOTTOM, category_id=cat("Classic").id),

        # Sport Wear
        Product(name="Track Jacket Retro", description="Спортивная куртка с полосками на рукавах, лёгкий нейлон.", price=7490, stock=15, sizes=CLOTH, category_id=cat("Sport Wear").id),
        Product(name="Jogger Pants Grey", description="Серые джоггеры с манжетами, хлопок с эластаном.", price=4990, stock=28, sizes=BOTTOM, category_id=cat("Sport Wear").id),
        Product(name="Sports Bra Logo", description="Спортивный топ с логотипом, поддержка средней нагрузки.", price=3290, stock=20, sizes="XS, S, M, L, XL", category_id=cat("Sport Wear").id),

        # Лето
        Product(name="Linen Shorts Beige", description="Льняные шорты бежевого цвета, лёгкие и дышащие.", price=3490, stock=30, sizes=BOTTOM, category_id=cat("Лето").id),
        Product(name="Tee Tie-Dye Summer", description="Тай-дай футболка в ярких летних цветах, оверсайз.", price=2790, stock=25, sizes=CLOTH, category_id=cat("Лето").id),
        Product(name="Bucket Hat Canvas", description="Панама из плотного канваса, защита от солнца.", price=2190, stock=40, sizes=ONE, category_id=cat("Лето").id),

        # Зима
        Product(name="Puffer Jacket Black", description="Пуховик чёрного цвета, наполнитель 80% пух, удлинённый крой.", price=18990, stock=8, sizes=CLOTH, category_id=cat("Зима").id),
        Product(name="Knit Beanie Logo", description="Вязаная шапка с вышитым лого, 100% шерсть мериноса.", price=2490, stock=35, sizes=ONE, category_id=cat("Зима").id),
        Product(name="Thermal Longsleeve", description="Термолонгслив с начёсом, плотность 300г, облегающий крой.", price=3990, stock=20, sizes=CLOTH, category_id=cat("Зима").id),

        # Весна
        Product(name="Coach Jacket Pastel", description="Тренерская куртка пастельного цвета, лёгкий нейлон.", price=8490, stock=14, sizes=CLOTH, category_id=cat("Весна").id),
        Product(name="Denim Shirt Overshirt", description="Джинсовая рубашка-оверширт, можно носить как куртку.", price=6990, stock=18, sizes=CLOTH, category_id=cat("Весна").id),
        Product(name="Sweatpants Spring", description="Спортивные брюки из лёгкого хлопка, весенний крой.", price=4490, stock=22, sizes=BOTTOM, category_id=cat("Весна").id),

        # Осень
        Product(name="Corduroy Overshirt", description="Вельветовая рубашка-оверширт тёмно-зелёного цвета.", price=7490, stock=12, sizes=CLOTH, category_id=cat("Осень").id),
        Product(name="Wool Blend Coat", description="Пальто из шерстяного микса, приталенный крой, длина до колена.", price=24990, stock=5, sizes=CLOTH, category_id=cat("Осень").id),
        Product(name="Knit Sweater Autumn", description="Вязаный свитер с фактурным узором, цвет ржавчина.", price=8990, stock=16, sizes=CLOTH, category_id=cat("Осень").id),
    ]
    for p in products:
        db.session.add(p)
    db.session.commit()


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
