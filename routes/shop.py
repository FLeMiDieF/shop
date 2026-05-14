from flask import Blueprint, render_template, request
from models import Product, Category, AboutPage
from extensions import cache

shop = Blueprint("shop", __name__)


@shop.route("/")
def index():
    featured = Product.query.filter(Product.stock > 0).order_by(Product.created_at.desc()).limit(8).all()
    categories = Category.query.all()
    return render_template("shop/index.html", products=featured, categories=categories)


@shop.route("/catalog")
def catalog():
    category_id = request.args.get("category", type=int)
    search = request.args.get("q", "").strip()
    query = Product.query.filter(Product.stock > 0)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = query.order_by(Product.created_at.desc()).all()
    categories = Category.query.all()
    return render_template("shop/catalog.html", products=products, categories=categories,
                           current_category=category_id, search=search)


@shop.route("/about")
def about():
    page = AboutPage.query.first()
    return render_template("shop/about.html", page=page)


@shop.route("/product/<int:product_id>")
def product(product_id):
    p = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == p.category_id,
        Product.id != p.id,
        Product.stock > 0
    ).limit(4).all()
    return render_template("shop/product.html", product=p, related=related)
