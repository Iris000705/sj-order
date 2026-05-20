import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, Response

app = Flask(__name__, static_folder='.', static_url_path='')
DB_FILE = 'database.json'

def get_default_data():
    return {
        "products": [
            {"id": 100, "name": "抱枕 TWD1390+PHOTO CARD POUCH SET TWD360(不拆)", "price": 1750, "stock": 1},
            {"id": 102, "name": "20糰 TWD780+成員四格照片TWD320(不拆)", "price": 1100, "stock": 1},
            {"id": 103, "name": "手燈套 TWD780+成員ID證件照 TWD420(不拆)", "price": 1200, "stock": 1},
            {"id": 106, "name": "COUPON SET+ACRYLIC STAND SET", "price": 1280, "stock": 1},
            {"id": 104, "name": "襯衫 TWD2100", "price": 2100, "stock": 1},
            {"id": 20, "name": "隨機成員磁鐵", "price": 550, "stock": 1},
            {"id": 250, "name": "超市磁鐵-超市款/SJ LOGO款 2選1", "price": 750, "stock": 1},
            {"id": 107, "name": "RANDOM PACKAGE KEYRING+RANDOM MALRANG KEYRING", "price": 450, "stock": 1},
            {"id": 109, "name": "RANDOM ACRYLIC KEYRING", "price": 300, "stock": 5},
            {"id": 110, "name": "RANDOM TRADING CARD SET (紅版+黃版)", "price": 500, "stock": 3},
            {"id": 220, "name": "娃包", "price": 350, "stock": 5},
            {"id": 230, "name": "帽子", "price": 1190, "stock": 1}
        ],
        "orders": []
    }

def load_data():
    if not os.path.exists(DB_FILE):
        default_data = get_default_data()
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
        return jsonify({"success": False, "message": "請填寫完整正確的訂購資訊"}), 400

    if len(items) < 3:
        return jsonify({"success": False, "message": "下單失敗：最少需選擇 3 個品項才能送出訂單！"}), 400

    data = load_data()
    
    # 檢查庫存
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
        note = item.get('note', '').strip()
        
        product = next((p for p in data["products"] if p["id"] == p_id), None)
        product["stock"] -= qty
        grand_total += product["price"] * qty
        
        if note:
            item_summary = f"{product['name']}(備註:{note})x{qty}"
        else:
            item_summary = f"{product['name']}x{qty}"
            
        order_details.append(item_summary)

    now = datetime.now()
    time_prefix = now.strftime('%y%m%d%H%M')
    same_time_orders = [o for o in data["orders"] if o["orderId"].startswith(time_prefix)]
    sequence_number = len(same_time_orders) + 1
    order_id = f"{time_prefix}{sequence_number:03d}"

    # 🔄 ✨ 重點調整：品項之間改用 "\n" 換行字元串接，不再用加號
    new_order = {
        "orderId": order_id,
        "customerName": customer_name,
        "instagramId": instagram_id,
        "productSummary": "\n".join(order_details), 
        "totalPrice": grand_total,
        "orderTime": now.strftime('%Y-%m-%d %H:%M:%S')
    }
    data["orders"].append(new_order)
    save_data(data)
    return jsonify({"success": True, "message": f"🎉 下單成功！單號：{order_id}"})

@app.route('/api/reset-database', methods=['POST'])
def reset_database():
    req_data = request.get_json() or {}
    password = req_data.get('password', '')
    if password != 'sj888':
        return jsonify({"success": False, "message": "密碼錯誤，拒絕重置！"}), 403
    default_data = get_default_data()
    save_data(default_data)
    return jsonify({"success": True, "message": "🚀 系統重置成功！測試訂單已清空，所有庫存已恢復初始狀態！"})

@app.route('/api/export-excel', methods=['GET'])
def export_excel():
    data = load_data()
    orders = data.get("orders", [])
    if not orders:
        return "<script>alert('目前後台沒有任何訂單可供匯出！'); window.history.back();</script>"
    
    csv_lines = ["訂單編號,顧客姓名,IG帳號,購買商品明細(含備註),總金額,下單時間"]
    for order in orders:
        ig = order.get('instagramId', '')
        summary = order.get('productSummary', '')
        
        # 🔄 ✨ 重點調整：因為商品明細裡面有換行符號，在 CSV 中必須用雙引號 "" 包裹起來，Excel 才能正確識別在同一格內換行
        line = f"{order['orderId']},{order['customerName']},{ig},\"{summary}\",{order['totalPrice']},{order['orderTime']}"
        csv_lines.append(line)
        
    csv_content = "\n".join(csv_lines)
    bom_content = b'\xef\xbb\xbf' + csv_content.encode('utf-8')
    today = datetime.now().strftime('%Y-%m-%d')
    return Response(bom_content, mimetype="text/csv", headers={"Content-disposition": f"attachment; filename=order_report_{today}.csv"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)