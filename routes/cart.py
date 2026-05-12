from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user
from models import db, Product, Order, OrderItem

cart = Blueprint("cart", __name__)


def get_cart():
    return session.setdefault("cart", {})


@cart.route("/cart")
def view():
    cart_data = get_cart()
    items = []
    total = 0
    for product_id, qty in cart_data.items():
        p = Product.query.get(int(product_id))
        if p:
            subtotal = p.price * qty
            total += subtotal
            items.append({"product": p, "qty": qty, "subtotal": subtotal})
    return render_template("cart/cart.html", items=items, total=total)


@cart.route("/cart/add/<int:product_id>", methods=["POST"])
def add(product_id):
    product = Product.query.get_or_404(product_id)
    qty = int(request.form.get("qty", 1))
    cart_data = get_cart()
    key = str(product_id)
    cart_data[key] = cart_data.get(key, 0) + qty
    session.modified = True
    flash(f"«{product.name}» добавлен в корзину.", "success")
    return redirect(request.referrer or url_for("shop.catalog"))


@cart.route("/cart/remove/<int:product_id>")
def remove(product_id):
    cart_data = get_cart()
    cart_data.pop(str(product_id), None)
    session.modified = True
    return redirect(url_for("cart.view"))


@cart.route("/cart/checkout", methods=["POST"])
@login_required
def checkout():
    cart_data = get_cart()
    if not cart_data:
        flash("Корзина пуста.", "warning")
        return redirect(url_for("cart.view"))

    total = 0
    order_items = []
    for product_id, qty in cart_data.items():
        p = Product.query.get(int(product_id))
        if p and p.stock >= qty:
            total += p.price * qty
            order_items.append(OrderItem(product_id=p.id, quantity=qty, price=p.price))
            p.stock -= qty
        else:
            flash(f"Товар «{p.name if p else product_id}» недоступен в нужном количестве.", "danger")
            return redirect(url_for("cart.view"))

    order = Order(user_id=current_user.id, total=total)
    db.session.add(order)
    db.session.flush()
    for item in order_items:
        item.order_id = order.id
        db.session.add(item)
    db.session.commit()
    session.pop("cart", None)

    # Async task: send confirmation email
    try:
        from tasks import send_order_confirmation
        send_order_confirmation.delay(order.id, current_user.email, total)
    except Exception:
        pass  # Celery unavailable in local dev without Redis — that's fine

    flash(f"Заказ №{order.id} оформлен! Сумма: {total:.2f} ₽", "success")
    return redirect(url_for("shop.index"))
