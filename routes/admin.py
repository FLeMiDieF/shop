import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Product, Category, Order, User

admin = Blueprint("admin", __name__, url_prefix="/admin")


def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Доступ запрещён.", "danger")
            return redirect(url_for("shop.index"))
        return f(*args, **kwargs)
    return decorated


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in current_app.config["ALLOWED_EXTENSIONS"]


@admin.route("/")
@login_required
@admin_required
def dashboard():
    stats = {
        "products": Product.query.count(),
        "orders": Order.query.count(),
        "users": User.query.count(),
        "revenue": db.session.query(db.func.sum(Order.total)).scalar() or 0,
    }
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, orders=recent_orders)


@admin.route("/products")
@login_required
@admin_required
def products():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template("admin/products.html", products=items)


@admin.route("/products/new", methods=["GET", "POST"])
@login_required
@admin_required
def product_new():
    categories = Category.query.all()
    if request.method == "POST":
        image_filename = "no-image.png"
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            image_filename = filename
        p = Product(
            name=request.form["name"],
            description=request.form["description"],
            price=float(request.form["price"]),
            stock=int(request.form["stock"]),
            category_id=request.form.get("category_id") or None,
            image=image_filename,
        )
        db.session.add(p)
        db.session.commit()
        flash("Товар добавлен.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", product=None, categories=categories)


@admin.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def product_edit(product_id):
    p = Product.query.get_or_404(product_id)
    categories = Category.query.all()
    if request.method == "POST":
        p.name = request.form["name"]
        p.description = request.form["description"]
        p.price = float(request.form["price"])
        p.stock = int(request.form["stock"])
        p.category_id = request.form.get("category_id") or None
        file = request.files.get("image")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
            p.image = filename
        db.session.commit()
        flash("Товар обновлён.", "success")
        return redirect(url_for("admin.products"))
    return render_template("admin/product_form.html", product=p, categories=categories)


@admin.route("/products/<int:product_id>/delete", methods=["POST"])
@login_required
@admin_required
def product_delete(product_id):
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    flash("Товар удалён.", "success")
    return redirect(url_for("admin.products"))


@admin.route("/orders")
@login_required
@admin_required
def orders():
    items = Order.query.order_by(Order.created_at.desc()).all()
    return render_template("admin/orders.html", orders=items)


@admin.route("/orders/<int:order_id>/status", methods=["POST"])
@login_required
@admin_required
def order_status(order_id):
    order = Order.query.get_or_404(order_id)
    order.status = request.form["status"]
    db.session.commit()
    flash("Статус заказа обновлён.", "success")
    return redirect(url_for("admin.orders"))


@admin.route("/categories", methods=["GET", "POST"])
@login_required
@admin_required
def categories():
    if request.method == "POST":
        name = request.form["name"].strip()
        if name and not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))
            db.session.commit()
            flash("Категория добавлена.", "success")
    cats = Category.query.all()
    return render_template("admin/categories.html", categories=cats)
