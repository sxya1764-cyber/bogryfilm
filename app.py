import sqlite3
from flask import Flask, render_template_string, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'heart-secret-key'

# --- ระบบจัดการฐานข้อมูล ---
def init_db():
    with sqlite3.connect('new_data.db') as conn:
        # ตารางผู้ใช้งาน
        conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        # ตารางข้อความความในใจ
        conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user TEXT, content TEXT)')
    print("ระบบฐานข้อมูลพร้อมใช้งาน!")

# --- หน้าสมัครสมาชิก (Register) ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        hashed_pwd = generate_password_hash(pwd) # เข้ารหัสเพื่อความปลอดภัย
        try:
            with sqlite3.connect('new_data.db') as conn:
                conn.execute('INSERT INTO users VALUES (?, ?)', (user, hashed_pwd))
            return "สมัครสำเร็จ! <a href='/login'>ไปล็อกอินกันเลย</a>"
        except:
            return "ชื่อนี้มีคนใช้แล้ว! <a href='/register'>ลองชื่ออื่น</a>"
    return '''
        <style>body{text-align:center; padding-top:100px; font-family:sans-serif; background:#f0f2f5;}</style>
        <div style="background:white; display:inline-block; padding:30px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
            <h2>สมัครสมาชิก 📝</h2>
            <form method="post">
                <input type="text" name="username" placeholder="ตั้งชื่อผู้ใช้" required style="padding:10px; margin:5px;"><br>
                <input type="password" name="password" placeholder="ตั้งรหัสผ่าน" required style="padding:10px; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px; background:#2ecc71; color:white; border:none; border-radius:5px; cursor:pointer;">ยืนยันสมัครสมาชิก</button>
            </form>
            <p><a href="/login">มีบัญชีแล้ว? ล็อกอินที่นี่</a></p>
        </div>
    '''

# --- หน้าล็อกอิน (Login) ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = request.form.get('username')
        pwd = request.form.get('password')
        with sqlite3.connect('new_data.db') as conn:
            res = conn.execute('SELECT password FROM users WHERE username = ?', (user,)).fetchone()
        if res and check_password_hash(res[0], pwd):
            session['user'] = user
            return redirect('/')
        # กรณีพิเศษสำหรับแอดมิน (ล็อกไว้ให้คุณคนเดียว)
        if user == 'admin' and pwd == '1234':
            session['user'] = 'admin'
            return redirect('/')
        return "ชื่อหรือรหัสผิด! <a href='/login'>ลองใหม่</a>"
    return '''
        <style>body{text-align:center; padding-top:100px; font-family:sans-serif; background:#f0f2f5;}</style>
        <div style="background:white; display:inline-block; padding:30px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
            <h2>เข้าสู่ระบบ 🚀</h2>
            <form method="post">
                <input type="text" name="username" placeholder="ชื่อผู้ใช้" required style="padding:10px; margin:5px;"><br>
                <input type="password" name="password" placeholder="รหัสผ่าน" required style="padding:10px; margin:5px;"><br>
                <button type="submit" style="padding:10px 20px; background:#5f27cd; color:white; border:none; border-radius:5px; cursor:pointer;">Login</button>
            </form>
            <p><a href="/register">ยังไม่มีบัญชี? สมัครใหม่ฟรี</a></p>
        </div>
    '''

# --- หน้าเขียนความในใจ (Home) ---
@app.route('/')
def home():
    if 'user' not in session: return redirect('/login')
    return render_template_string('''
        <link rel="stylesheet" href="https://cloudflare.com"/>
        <style>
            body { font-family: sans-serif; text-align: center; padding: 50px; background: #fafafa; }
            .box { background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 20px rgba(0,0,0,0.1); display: inline-block; width: 80%; max-width: 500px; }
            textarea { width: 100%; height: 100px; padding: 10px; border-radius: 10px; border: 1px solid #ddd; margin: 10px 0; font-family: inherit; }
            .btn { background: #ff4757; color: white; border: none; padding: 10px 25px; border-radius: 50px; cursor: pointer; font-size: 16px; }
        </style>
        <div class="box animate__animated animate__fadeIn">
            <h1>พื้นที่ความในใจ 💖</h1>
            <p>สวัสดีคุณ <b>{{ user }}</b> พิมพ์สิ่งที่อยากบอกได้เลย</p>
            <form action="/send" method="post">
                <textarea name="msg" placeholder="เขียนความในใจตรงนี้..." required></textarea><br>
                <button type="submit" class="btn">ส่งความในใจ</button>
            </form>
            <br>
            {% if user == 'admin' %}<a href="/admin" style="color:blue;">🛠️ เข้าหน้าแอดมินดูความลับ</a><br>{% endif %}
            <a href="/logout" style="color:gray; font-size:12px;">ออกจากระบบ</a>
        </div>
    ''', user=session['user'])

@app.route('/send', methods=['POST'])
def send():
    msg = request.form.get('msg')
    with sqlite3.connect('new_data.db') as conn:
        conn.execute('INSERT INTO messages (user, content) VALUES (?, ?)', (session['user'], msg))
    return "<h3>บันทึกความในใจแล้ว! ✨</h3><a href='/'>กลับหน้าหลัก</a>"

@app.route('/admin')
def admin():
    if session.get('user') != 'admin': return "เฉพาะแอดมินเท่านั้น!", 403
    with sqlite3.connect('new_data.db') as conn:
        data = conn.execute('SELECT user, content FROM messages').fetchall()
    return render_template_string('''
        <h2>🛠️ รายการความในใจทั้งหมด (ลับเฉพาะแอดมิน)</h2>
        <table border="1" style="width:100%; border-collapse: collapse; text-align: left;">
            <tr style="background:#eee;">
                <th style="padding:10px;">ชื่อผู้ส่ง</th>
                <th style="padding:10px;">ข้อความความในใจ</th>
            </tr>
            {% for u, c in data %}
            <tr>
                <td style="padding:10px; border-bottom:1px solid #ddd;"><b>{{ u }}</b></td>
                <td style="padding:10px; border-bottom:1px solid #ddd;">{{ c }}</td>
            </tr>
            {% endfor %}
        </table>
        <br><a href="/">กลับหน้าหลัก</a>
    ''', data=data)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=10000)
