import csv
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse

# 配置常量
DB_FILE = 'device_records.csv'
PORT = 8000

# ===== 数据库操作 =====
def init_db():
    """初始化CSV数据库文件"""
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['device_id', 'update_content', 'update_time'])

def add_record(device_id, update_content):
    """添加新记录"""
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(DB_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([device_id, update_content, update_time])

def query_records(device_id=None):
    """查询记录"""
    records = []
    if not os.path.exists(DB_FILE):
        return records

    with open(DB_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not device_id or row['device_id'] == device_id:
                records.append(dict(row))
    return records

# ===== 美化版HTML模板 =====
def render_template(title, content):
    """基础模板框架"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{title} | 设备记录系统</title>
        <style>
            :root {{
                --primary: #4a6bdf;
                --primary-dark: #3a56b2;
                --secondary: #f8f9fa;
                --text: #333;
                --light: #fff;
                --border: #dee2e6;
                --success: #28a745;
            }}
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                           "Helvetica Neue", Arial, sans-serif;
                line-height: 1.6;
                color: var(--text);
                background-color: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background: var(--primary);
                color: var(--light);
                padding: 20px;
                border-radius: 5px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1, h2 {{
                font-weight: 500;
            }}
            .card {{
                background: var(--light);
                border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                padding: 25px;
                margin-bottom: 20px;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 500;
            }}
            input, textarea, select {{
                width: 100%;
                padding: 10px;
                border: 1px solid var(--border);
                border-radius: 4px;
                font-family: inherit;
            }}
            textarea {{
                min-height: 120px;
                resize: vertical;
            }}
            .btn {{
                display: inline-block;
                background: var(--primary);
                color: var(--light);
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                cursor: pointer;
                text-decoration: none;
                font-size: 16px;
                transition: all 0.3s;
            }}
            .btn:hover {{
                background: var(--primary-dark);
                transform: translateY(-1px);
            }}
            .btn-secondary {{
                background: #6c757d;
            }}
            .btn-group {{
                display: flex;
                gap: 10px;
                margin-top: 20px;
            }}
            .record-card {{
                background: var(--light);
                border-radius: 5px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                padding: 20px;
                margin-bottom: 15px;
            }}
            .record-header {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                font-weight: 500;
                color: var(--primary);
            }}
            .empty-state {{
                text-align: center;
                padding: 40px 20px;
                color: #6c757d;
            }}
            .search-form {{
                display: flex;
                gap: 10px;
                margin-bottom: 20px;
            }}
            .search-form input {{
                flex: 1;
            }}
            @media (max-width: 768px) {{
                .search-form {{
                    flex-direction: column;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>设备记录管理系统</h1>
            </header>
            {content}
        </div>
    </body>
    </html>
    """

def render_index():
    """首页"""
    content = """
    <div class="card">
        <h2>记录查询</h2>
        <form class="search-form" action="/query" method="GET">
            <input type="text" name="device_id" placeholder="输入设备ID (留空查询全部)">
            <button type="submit" class="btn">查询记录</button>
        </form>
        <div class="btn-group">
            <a href="/add" class="btn">添加新记录</a>
        </div>
    </div>
    """
    return render_template("首页", content)

def render_add_form():
    """添加记录表单"""
    content = """
    <div class="card">
        <h2>添加新记录</h2>
        <form method="POST" action="/add_record">
            <div class="form-group">
                <label for="device_id">设备ID</label>
                <input type="text" id="device_id" name="device_id" required>
            </div>
            <div class="form-group">
                <label for="update_content">更新内容</label>
                <textarea id="update_content" name="update_content" required></textarea>
            </div>
            <div class="btn-group">
                <button type="submit" class="btn">提交记录</button>
                <a href="/" class="btn btn-secondary">取消返回</a>
            </div>
        </form>
    </div>
    """
    return render_template("添加记录", content)

def render_records(records):
    """记录列表"""
    if not records:
        content = '<div class="card"><div class="empty-state">没有找到匹配的记录</div></div>'
    else:
        records_html = []
        for record in records:
            records_html.append(f"""
            <div class="record-card">
                <div class="record-header">
                    <span>设备ID: {record['device_id']}</span>
                    <span>更新时间: {record['update_time']}</span>
                </div>
                <div class="record-content">
                    <p>{record['update_content']}</p>
                </div>
            </div>
            """)
        content = f"""
        <div class="card">
            <h2>查询结果</h2>
            <div class="records-list">
                {"".join(records_html)}
            </div>
            <div class="btn-group">
                <a href="/" class="btn">返回首页</a>
            </div>
        </div>
        """
    return render_template("查询结果", content)

# ===== HTTP请求处理器 =====
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """处理GET请求"""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(render_index().encode('utf-8'))

        elif parsed.path == '/add':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(render_add_form().encode('utf-8'))

        elif parsed.path == '/query':
            query = urllib.parse.parse_qs(parsed.query)
            device_id = query.get('device_id', [None])[0]
            records = query_records(device_id)

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(render_records(records).encode('utf-8'))

        else:
            self.send_error(404, "页面不存在")

    def do_POST(self):
        """处理POST请求"""
        if self.path == '/add_record':
            length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)

            add_record(
                device_id=params['device_id'][0],
                update_content=params['update_content'][0]
            )

            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

# ===== 主程序 =====
if __name__ == '__main__':
    init_db()

    server = HTTPServer(('', PORT), RequestHandler)
    print(f"服务器已启动，访问 http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已关闭")
