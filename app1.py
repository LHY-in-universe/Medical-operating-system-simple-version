from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

# 数据库文件路径
DB_FILE = 'device_records.xlsx'

# 初始化数据库（如果不存在）
def init_db():
    if not os.path.exists(DB_FILE):
        # 创建包含必要列的DataFrame
        df = pd.DataFrame(columns=[
            'device_id', 
            'update_content', 
            'update_time'
        ])
        # 保存到Excel文件
        df.to_excel(DB_FILE, index=False)

@app.route('/')
def index():
    """主页，显示查询表单"""
    return render_template('index.html')

@app.route('/add_record', methods=['GET', 'POST'])
def add_record():
    """添加新记录"""
    if request.method == 'POST':
        # 获取表单数据
        device_id = request.form['device_id']
        update_content = request.form['update_content']
        update_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 读取现有数据
        try:
            df = pd.read_excel(DB_FILE)
        except:
            df = pd.DataFrame(columns=['device_id', 'update_content', 'update_time'])
        
        # 添加新记录
        new_record = {
            'device_id': device_id,
            'update_content': update_content,
            'update_time': update_time
        }
        df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
        
        # 保存回Excel
        df.to_excel(DB_FILE, index=False)
        
        return redirect(url_for('index'))
    
    return render_template('add_record.html')

@app.route('/query', methods=['GET'])
def query():
    """查询记录"""
    device_id = request.args.get('device_id', '').strip()
    
    # 读取数据
    try:
        df = pd.read_excel(DB_FILE)
    except:
        df = pd.DataFrame(columns=['device_id', 'update_content', 'update_time'])
    
    # 如果提供了device_id，筛选相关记录
    if device_id:
        result = df[df['device_id'] == device_id]
    else:
        result = df
    
    # 将结果转换为字典列表
    records = result.to_dict('records')
    
    return jsonify(records)

if __name__ == '__main__':
    init_db()  # 确保数据库文件存在
    app.run(debug=True)
