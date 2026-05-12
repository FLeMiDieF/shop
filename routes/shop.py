from flask import Blueprint, render_template, request
from models import Product, Category
from extensions import cache

shop = Blueprint("shop", __name__)


@shop.route("/")
@cache.cached(timeout=60, key_prefix="shop_index")
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


@shop.route("/product/<int:product_id>")
@cache.cached(timeout=120, key_prefix=lambda: f"product_{request.view_args['product_id']}")
def product(product_id):
    p = Product.query.get_or_404(product_id)
    related = Product.query.filter(
        Product.category_id == p.category_id,
        Product.id != p.id,
        Product.stock > 0
    ).limit(4).all()
    return render_template("shop/product.html", product=p, related=related)
