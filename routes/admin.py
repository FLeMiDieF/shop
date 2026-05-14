import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db, Product, Category, AboutPage

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
        "categories": Category.query.count(),
        "in_stock": Product.query.filter(Product.stock > 0).count(),
        "out_of_stock": Product.query.filter(Product.stock == 0).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


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
            sizes=request.form.get("sizes", "").strip(),
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
        p.sizes = request.form.get("sizes", "").strip()
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


@admin.route("/categories/<int:cat_id>/edit", methods=["POST"])
@login_required
@admin_required
def category_edit(cat_id):
    cat = Category.query.get_or_404(cat_id)
    name = request.form["name"].strip()
    if name and name != cat.name and not Category.query.filter_by(name=name).first():
        cat.name = name
        db.session.commit()
        flash("Категория переименована.", "success")
    else:
        flash("Имя уже занято или не изменилось.", "warning")
    return redirect(url_for("admin.categories"))


@admin.route("/about", methods=["GET", "POST"])
@login_required
@admin_required
def about_edit():
    page = AboutPage.query.first()
    if request.method == "POST":
        page.title = request.form["title"].strip()
        page.subtitle = request.form["subtitle"].strip()
        page.description = request.form["description"].strip()
        page.address = request.form["address"].strip()
        page.phone = request.form["phone"].strip()
        page.email = request.form["email"].strip()
        page.hours_weekday = request.form["hours_weekday"].strip()
        page.hours_weekend = request.form["hours_weekend"].strip()
        db.session.commit()
        flash("Страница «О нас» обновлена.", "success")
        return redirect(url_for("admin.about_edit"))
    return render_template("admin/about_form.html", page=page)


@admin.route("/categories/<int:cat_id>/delete", methods=["POST"])
@login_required
@admin_required
def category_delete(cat_id):
    cat = Category.query.get_or_404(cat_id)
    for p in cat.products:
        p.category_id = None
    db.session.delete(cat)
    db.session.commit()
    flash(f"Категория «{cat.name}» удалена.", "success")
    return redirect(url_for("admin.categories"))
