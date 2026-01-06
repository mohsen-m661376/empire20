import streamlit as st
import random
import requests
import time
import hashlib
import sqlite3

# --- ۱. تنظیمات امنیتی (مخصوص ادمین) ---
# این کلید باید با کلیدی که با آن لایسنس می‌سازی یکی باشد
SECRET_KEY = "EMPIRE-2026-SUPER-SECRET-KEY-@#$%" 
MY_CHAT_ID = "932654521"
MY_BOT_TOKEN = "7595178002:AAH4Tu8p97zN7yMxLh6WGyYkn3XJ438u-qI"

# --- ۲. دیتابیس برای قفل کردن کاربر (جایگزین روش سخت‌افزاری) ---
def init_db():
    """ایجاد دیتابیس برای ذخیره لایسنس‌های مصرف شده"""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses 
                 (license_key TEXT PRIMARY KEY, user_name TEXT, is_active INTEGER)''')
    conn.commit()
    conn.close()

def verify_and_lock_license(user_name, license_key):
    """
    ۱. صحت ریاضی لایسنس را چک می‌کند.
    ۲. چک می‌کند آیا قبلاً توسط شخص دیگری استفاده شده یا خیر.
    """
    # گام اول: بررسی امضای ریاضی
    try:
        parts = license_key.split('-')
        if len(parts) < 2: return False, "فرمت لایسنس اشتباه است."
        
        input_hash = parts[-1]
        user_part = "-".join(parts[:-1]) # نام کاربر در لایسنس
        
        # اگر نام وارد شده با نام داخل لایسنس یکی نباشد
        if user_part.lower() != user_name.lower():
            return False, "این لایسنس متعلق به نام کاربری دیگری است."

        # ساخت مجدد هش برای تایید
        raw_string = f"{user_part}{SECRET_KEY}"
        expected_hash = hashlib.sha256(raw_string.encode()).hexdigest()[:8].upper()
        
        if input_hash != expected_hash:
            return False, "لایسنس نامعتبر است."
    except:
        return False, "خطا در پردازش لایسنس."

    # گام دوم: بررسی در دیتابیس (قفل لایسنس)
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # آیا این لایسنس قبلا ثبت شده؟
    c.execute("SELECT user_name FROM licenses WHERE license_key=?", (license_key,))
    result = c.fetchone()
    
    if result:
        # لایسنس قبلا استفاده شده. آیا نام کاربر همان است؟
        saved_user = result[0]
        conn.close()
        if saved_user.lower() == user_name.lower():
            return True, "ورود موفق (کاربر قدیمی)."
        else:
            return False, "⛔ این لایسنس قبلاً توسط شخص دیگری فعال شده است!"
    else:
        # اولین بار است -> ثبت در دیتابیس
        c.execute("INSERT INTO licenses (license_key, user_name, is_active) VALUES (?, ?, 1)", 
                  (license_key, user_name))
        conn.commit()
        conn.close()
        return True, "ورود موفق (فعالسازی جدید)."

# --- ۳. محتوا ---
TRENDS_72H = [
    {"topic": "هوش مصنوعی مولد", "music": "Trending Techno Beats", "challenge": "AI Look-alike"},
    {"topic": "اقتصاد غیرمتمرکز", "music": "Lo-fi Chill", "challenge": "Future Self Prediction"},
    {"topic": "سبک زندگی مینیمال", "music": "Nature Sounds 2026", "challenge": "3-Day Fasting"}
]

class EmpireGlobalApp:
    def __init__(self):
        self.languages = {
            "Persian": {"welcome": "خوش آمدید قربان", "gen_btn": "تولید محتوای آریا و لونا", "send": "ارسال به تلگرام", "success": "با موفقیت ارسال شد"},
            "English": {"welcome": "Welcome Sir", "gen_btn": "Generate Aria & Luna Content", "send": "Send to Telegram", "success": "Sent Successfully"},
        }

    def generate_scenario(self, lang_name):
        trend = random.choice(TRENDS_72H)
        if lang_name == "Persian":
            return (
                f"🎬 **سناریوی مشترک آریا و لونا**\n\n"
                f"🔥 **ترند:** {trend['topic']}\n"
                f"🎵 **موزیک:** {trend['music']}\n"
                f"💡 **چالش:** {trend['challenge']}\n\n"
                f"👤 **آریا:** طبق تحلیل داده‌ها، {trend['topic']} آینده است.\n"
                f"💃 **لونا:** چطوری فالوور بگیریم؟ با {trend['challenge']} همه رو جذب می‌کنیم! 😉"
            )
        return f"Viral Content for {trend['topic']} using {trend['challenge']}."

    def send_to_telegram(self, message):
        try:
            url = f"https://api.telegram.org/bot{MY_BOT_TOKEN}/sendMessage"
            payload = {"chat_id": MY_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(url, data=payload, timeout=5)
            return True
        except:
            return False

# --- ۴. رابط کاربری اصلی ---
def main():
    st.set_page_config(page_title="Empire 2026", page_icon="👑", layout="centered")
    init_db() # اطمینان از وجود دیتابیس
    app = EmpireGlobalApp()

    if 'auth' not in st.session_state:
        st.session_state.auth = False

    # --- صفحه لاگین ---
    if not st.session_state.auth:
        st.markdown("<h1 style='text-align: center;'>👑 EMPIRE WEB SYSTEM</h1>", unsafe_allow_html=True)
        st.info("نسخه وب - سازگار با آیفون، اندروید و ویندوز")
        
        user_input_name = st.text_input("نام کاربری:")
        license_key = st.text_input("کد لایسنس:", type="password")
        
        if st.button("ورود به سیستم"):
            if not user_input_name or not license_key:
                st.warning("لطفاً نام و کد را وارد کنید.")
            else:
                is_valid, message = verify_and_lock_license(user_input_name, license_key)
                
                if is_valid:
                    st.success(message)
                    time.sleep(1)
                    st.session_state.auth = True
                    st.session_state.user = user_input_name
                    st.rerun()
                else:
                    st.error(message)
        return

    # --- پنل کاربری ---
    st.sidebar.write(f"👤 کاربر فعال: {st.session_state.user}")
    if st.sidebar.button("خروج"):
        st.session_state.auth = False
        st.rerun()

    lang = st.sidebar.selectbox("Language / زبان", ["Persian", "English"])
    texts = app.languages[lang]
    
    st.title(texts['welcome'])
    
    if st.button(texts['gen_btn'], use_container_width=True):
        st.session_state.current_post = app.generate_scenario(lang)
    
    if 'current_post' in st.session_state:
        st.info(st.session_state.current_post)
        if st.button(texts['send'], use_container_width=True):
            if app.send_to_telegram(st.session_state.current_post):
                st.success(texts['success'])
            else:
                st.error("خطا در اتصال.")

if __name__ == "__main__":
    main()