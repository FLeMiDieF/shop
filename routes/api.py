from flask import Blueprint, jsonify, request
from models import Product, Category

api = Blueprint("api", __name__, url_prefix="/api")


@api.route("/products")
def products_list():
    """
    Получить список товаров.
    ---
    tags:
      - Products
    parameters:
      - name: category_id
        in: query
        type: integer
        required: false
        description: Фильтр по ID категории
      - name: q
        in: query
        type: string
        required: false
        description: Поиск по названию
    responses:
      200:
        description: Список товаров
        schema:
          type: array
          items:
            $ref: '#/definitions/Product'
    definitions:
      Product:
        type: object
        properties:
          id:
            type: integer
          name:
            type: string
          description:
            type: string
          price:
            type: number
          stock:
            type: integer
          image:
            type: string
          category:
            type: string
          category_id:
            type: integer
    """
    category_id = request.args.get("category_id", type=int)
    search = request.args.get("q", "").strip()
    query = Product.query.filter(Product.stock > 0)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    products = query.order_by(Product.created_at.desc()).all()
    return jsonify([_product_to_dict(p) for p in products])


@api.route("/products/<int:product_id>")
def product_detail(product_id):
    """
    Получить товар по ID.
    ---
    tags:
      - Products
    parameters:
      - name: product_id
        in: path
        type: integer
        required: true
        description: ID товара
    responses:
      200:
        description: Данные товара
        schema:
          $ref: '#/definitions/Product'
      404:
        description: Товар не найден
    """
    p = Product.query.get_or_404(product_id)
    data = _product_to_dict(p)
    data["created_at"] = p.created_at.isoformat()
    return jsonify(data)


@api.route("/categories")
def categories_list():
    """
    Получить список категорий.
    ---
    tags:
      - Categories
    responses:
      200:
        description: Список категорий
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              product_count:
                type: integer
    """
    categories = Category.query.all()
    return jsonify([
        {"id": c.id, "name": c.name, "product_count": len(c.products)}
        for c in categories
    ])


def _product_to_dict(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "stock": p.stock,
        "image": p.image,
        "category": p.category.name if p.category else None,
        "category_id": p.category_id,
    }
