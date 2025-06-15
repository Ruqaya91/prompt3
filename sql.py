from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///orders.db"
db = SQLAlchemy(app)

# Sample Model
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

# Create tables
with app.app_context():
    db.create_all()

@app.route('/search', methods=['GET'])
def search():
    customer = request.args.get('customer_name')
    product = request.args.get('product_name')
    order_id = request.args.get('order_id')
    query = Order.query

    if customer:
        query = query.filter(Order.customer_name.ilike(f"%{customer}%"))
    if product:
        query = query.filter(Order.product_name.ilike(f"%{product}%"))
    if order_id:
        query = query.filter(Order.id == int(order_id))
    
    results = query.all()
    return jsonify([
        {
            "order_id": order.id,
            "customer_name": order.customer_name,
            "product_name": order.product_name,
            "quantity": order.quantity
        }
        for order in results
    ])

@app.route('/update/<int:order_id>', methods=['PUT'])
def update(order_id):
    data = request.json
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    if "customer_name" in data:
        order.customer_name = data["customer_name"]
    if "product_name" in data:
        order.product_name = data["product_name"]
    if "quantity" in data:
        order.quantity = data["quantity"]

    db.session.commit()
    return jsonify({"message": "Order updated successfully"})

# (Optional) Add endpoint to create sample data
@app.route('/add', methods=['POST'])
def add_order():
    data = request.json
    order = Order(
        customer_name=data["customer_name"],
        product_name=data["product_name"],
        quantity=data["quantity"]
    )
    db.session.add(order)
    db.session.commit()
    return jsonify({"order_id": order.id}), 201

if __name__ == '__main__':
    app.run(debug=True)
