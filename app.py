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
                # --- 最新修正代購品項清單 ---
                {"id": 100, "name": "抱枕 TWD1390+PHOTO CARD POUCH SET TWD360(不拆)", "price": 1750, "stock": 1},
                {"id": 102, "name": "20糰 TWD780+成員四格照片TWD320(不拆)", "price": 1100, "stock": 1},
                {"id": 103, "name": "手燈套 TWD780+成員ID證件照 TWD420(不拆)", "price": 1200, "stock": 1}, # 名稱修正，金額改為 1200
                {"id": 104, "name": "襯衫 TWD2100", "price": 2100, "stock": 1},
                
                # --- 其它保留周邊 ---
                {"id": 20, "name": "隨機成員磁鐵", "price": 550, "stock": 1},
                {"id": 250, "name": "超市磁鐵-超市款/SJ LOGO款 2選1", "price": 750, "stock": 1},
                {"id": 220, "name": "娃包", "price": 350, "stock": 5},
                {"id": 230, "name": "帽子", "price": 1190, "stock": 1},
                
                # --- 追加周邊品項 ---
                {"id": 105, "name": "COUPON SET", "price": 430, "stock": 1},
                {"id": 106, "name": "ACRYLIC STAND SET", "price": 850, "stock": 1},
                {"id": 107, "name": "RANDOM PACKAGE KEYRING", "price": 300, "stock": 1},
                {"id": 108, "name": "RANDOM MALRANG KEYRING", "price": 150, "stock": 1},
                {"id": 109, "name": "RANDOM ACRYLIC KEYRING", "price": 300, "stock": 5},
                {"id": 110, "name": "RANDOM TRADING CARD SET (紅版)", "price": 250, "stock": 3},
                {"id": 111, "name": "RANDOM TRADING CARD SET (黃版)", "price": 250, "stock": 3}
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

    if len(items) < 3:
        return jsonify({"success": False, "message": "下單失敗：本團最少需選擇 3 個品項才能送出訂單！"}), 400

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