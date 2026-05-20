import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, Response

app = Flask(__name__, static_folder='.', static_url_path='')
DB_FILE = 'database.json'

def load_data():
    if not os.path.exists(DB_FILE):
        default_data = {
            "products": [
                # --- 19糰區 (id: 10~18，單價 1100) ---
                {"id": 10, "name": "19糰-利特", "price": 1100, "stock": 10},
                {"id": 11, "name": "19糰-希澈", "price": 1100, "stock": 10},
                {"id": 12, "name": "19糰-藝聲", "price": 1100, "stock": 10},
                {"id": 13, "name": "19糰-神童", "price": 1100, "stock": 10},
                {"id": 14, "name": "19糰-銀赫", "price": 1100, "stock": 10},
                {"id": 15, "name": "19糰-始源", "price": 1100, "stock": 10},
                {"id": 16, "name": "19糰-東海", "price": 1100, "stock": 10},
                {"id": 17, "name": "19糰-厲旭", "price": 1100, "stock": 10},
                {"id": 18, "name": "19糰-圭賢", "price": 1100, "stock": 10},

                # --- 20糰區 (id: 21~29，單價 1100) ---
                {"id": 21, "name": "20糰-利特", "price": 1100, "stock": 10},
                {"id": 22, "name": "20糰-希澈", "price": 1100, "stock": 10},
                {"id": 23, "name": "20糰-藝聲", "price": 1100, "stock": 10},
                {"id": 24, "name": "20糰-神童", "price": 1100, "stock": 10},
                {"id": 25, "name": "20糰-銀赫", "price": 1100, "stock": 10},
                {"id": 26, "name": "20糰-始源", "price": 1100, "stock": 10},
                {"id": 27, "name": "20糰-東海", "price": 1100, "stock": 10},
                {"id": 28, "name": "20糰-厲旭", "price": 1100, "stock": 10},
                {"id": 29, "name": "20糰-圭賢", "price": 1100, "stock": 10},

                # --- 手燈套區 (id: 31~39，單價 790) ---
                {"id": 31, "name": "手燈套-利特", "price": 790, "stock": 10},
                {"id": 32, "name": "手燈套-希澈", "price": 790, "stock": 10},
                {"id": 33, "name": "手燈套-藝聲", "price": 790, "stock": 10},
                {"id": 34, "name": "手燈套-神童", "price": 790, "stock": 10},
                {"id": 35, "name": "手燈套-銀赫", "price": 790, "stock": 10},
                {"id": 36, "name": "手燈套-始源", "price": 790, "stock": 10},
                {"id": 37, "name": "手燈套-東海", "price": 790, "stock": 10},
                {"id": 38, "name": "手燈套-厲旭", "price": 790, "stock": 10},
                {"id": 39, "name": "手燈套-圭賢", "price": 790, "stock": 10},

                # --- 杯套區 (id: 41~49，單價 300) ---
                {"id": 41, "name": "杯套-利特", "price": 300, "stock": 10},
                {"id": 42, "name": "杯套-希澈", "price": 300, "stock": 10},
                {"id": 43, "name": "杯套-藝聲", "price": 300, "stock": 10},
                {"id": 44, "name": "杯套-神童", "price": 300, "stock": 10},
                {"id": 45, "name": "杯套-銀赫", "price": 300, "stock": 10},
                {"id": 46, "name": "杯套-始源", "price": 300, "stock": 10},
                {"id": 48, "name": "杯套-厲旭", "price": 300, "stock": 10},
                {"id": 49, "name": "杯套-圭賢", "price": 300, "stock": 10},
                
                # --- 襯衫區 (id: 51~59，單價 2100) ---
                {"id": 51, "name": "襯衫-利特", "price": 2100, "stock": 10},
                {"id": 52, "name": "襯衫-希澈", "price": 2100, "stock": 10},
                {"id": 53, "name": "襯衫-藝聲", "price": 2100, "stock": 10},
                {"id": 54, "name": "襯衫-神童", "price": 2100, "stock": 10},
                {"id": 55, "name": "襯衫-銀赫", "price": 2100, "stock": 10},
                {"id": 56, "name": "襯衫-始源", "price": 2100, "stock": 10},
                {"id": 57, "name": "襯衫-東海", "price": 2100, "stock": 10},
                {"id": 58, "name": "襯衫-厲旭", "price": 2100, "stock": 10},
                {"id": 59, "name": "襯衫-圭賢", "price": 2100, "stock": 10},
                
                # --- 所有商品區（原其他商品） ---
                {"id": 100, "name": "抱枕 TWD1390+PHOTO CARD POUCH SET TWD360", "price": 1750, "stock": 10},
                {"id": 20, "name": "成員磁鐵", "price": 550, "stock": 9},
                {"id": 240, "name": "超市磁鐵-SJ LOGO款", "price": 750, "stock": 1},
                {"id": 250, "name": "超市磁鐵-超市款", "price": 750, "stock": 1},
                {"id": 220, "name": "娃包", "price": 350, "stock": 5},
                {"id": 230, "name": "帽子", "price": 1190, "stock": 1}
            ],
            "orders": []
        }
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, indent=2, ensure_ascii=False)
        return default_data
    
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/products', methods=['GET'])
def get_products():
    data = load_data()
    return jsonify(data["products"])

@app.route('/api/order', methods=['POST'])
def create_order():
    req_data = request.get_json()
    customer_name = req_data.get('customerName', '').strip()
    instagram_id = req_data.get('instagramId', '').strip()
    items = req_data.get('items', [])

    if not customer_name or not instagram_id or not items:
        return jsonify({"success": False, "message": "請填寫完整正確的訂購資訊(姓名與IG皆為必填)"}), 400

    data = load_data()
    
    for item in items:
        p_id = int(item.get('productId'))
        qty = int(item.get('quantity'))
        product = next((p for p in data["products"] if p["id"] == p_id), None)
        if not product:
            return jsonify({"success": False, "message": "包含未知的商品項目"}), 404
        if product["stock"] < qty:
            return jsonify({"success": False, "message": f"庫存不足！『{product['name']}』目前僅剩：{product['stock']}"}), 400

    order_details = []
    grand_total = 0
    for item in items:
        p_id = int(item.get('productId'))
        qty = int(item.get('quantity'))
        product = next((p for p in data["products"] if p["id"] == p_id), None)
        
        product["stock"] -= qty
        grand_total += product["price"] * qty
        order_details.append(f"{product['name']}x{qty}")

    now = datetime.now()
    time_prefix = now.strftime('%y%m%d%H%M')
    same_time_orders = [o for o in data["orders"] if o["orderId"].startswith(time_prefix)]
    sequence_number = len(same_time_orders) + 1
    order_id = f"{time_prefix}{sequence_number:03d}"

    new_order = {
        "orderId": order_id,
        "customerName": customer_name,
        "instagramId": instagram_id,
        "productSummary": " + ".join(order_details),
        "totalPrice": grand_total,
        "orderTime": now.strftime('%Y-%m-%d %H:%M:%S')
    }
    data["orders"].append(new_order)
    save_data(data)

    return jsonify({"success": True, "message": f"🎉 下單成功！單號：{order_id}\n訂購人：{customer_name} ({instagram_id})\n購買明細：{new_order['productSummary']}"})

@app.route('/api/export-excel', methods=['GET'])
def export_excel():
    data = load_data()
    orders = data.get("orders", [])
    if not orders:
        return "<script>alert('目前後台沒有任何訂單可供匯出！'); window.history.back();</script>"

    csv_lines = ["訂單編號,顧客姓名,IG帳號,購買商品明細,總金額,下單時間"]
    for order in orders:
        ig = order.get('instagramId', '')
        line = f"{order['orderId']},{order['customerName']},{ig},{order['productSummary']},{order['totalPrice']},{order['orderTime']}"
        csv_lines.append(line)
    
    csv_content = "\n".join(csv_lines)
    bom_content = b'\xef\xbb\xbf' + csv_content.encode('utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    return Response(
        bom_content,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename=order_report_{today}.csv"}
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)