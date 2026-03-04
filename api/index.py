from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import requests
import json
import hashlib
import hmac
import time

app = Flask(__name__)
CORS(app)

print("🚀 Starting The King Suits Store AI Assistant...")

# ===================== إعدادات فيسبوك =====================
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "the_king_store_bot_2024")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== المعلومات الأساسية للمحل =====================
STORE_INFO = {
    "name": "The King 👑",
    "description": "محل سوتيس (ملابس جاهزة) - The King",
    "address": "وسط البلد - شارع طلعت حرب - بجانب سينما مترو",
    "phone_numbers": ["01000000000", "01111111111", "01222222222"],
    "whatsapp_numbers": ["01000000000", "01111111111"],
    "working_hours": {
        "daily": "10:00 صباحاً - 12:00 منتصف الليل",
        "weekend": "10:00 صباحاً - 2:00 صباحاً"
    },
    "categories": [
        "سوتيس رجالية كاملة 👔",
        "جواكيت رجالية 🧥",
        "بناطيل رسمية 👖",
        "قمصان رجالية 👕",
        "ربطات عنق وتي شيرتات 🎀",
        "إكسسوارات رجالية 💼"
    ],
    "customer_service": "خدمة العملاء: اضغط على الرقم 01000000000 (واتساب)"
}

# ===================== جلسات المستخدمين (لتذكر من تفاعل مع البوت) =====================
# هذا قاموس بسيط في الذاكرة. ملاحظة: سيفقد البيانات عند إعادة تشغيل التطبيق.
user_sessions = {}

# دالة للتحقق مما إذا كان المستخدم جديدًا أم لا
def is_new_user(user_id):
    """تتحقق مما إذا كان المستخدم قد تفاعل مع البوت من قبل."""
    if user_id not in user_sessions:
        # مستخدم جديد، نقوم بتسجيله وإرجاع True
        user_sessions[user_id] = {"first_seen": time.time(), "has_interacted": True}
        return True
    return False

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد محل The King (سوتيس) الذكي 🤖",
        "status": "🟢 جاهز",
        "store": STORE_INFO["name"],
        "endpoints": {
            "/health": "GET - حالة النظام",
            "/ask": "POST - طرح الأسئلة",
            "/ask_get": "GET - طرح الأسئلة (بسيط)",
            "/webhook": "GET/POST - فيسبوك Messenger",
            "/fb_test": "GET - اختبار اتصال فيسبوك"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "facebook_ready": bool(FB_PAGE_TOKEN),
        "store": STORE_INFO["name"],
        "active_sessions": len(user_sessions)
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "يرجى إرسال سؤال"}), 400
            
        # هذا المسار للاختبار، لا يحتاج لحالة مستخدم
        answer = generate_response_for_test(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask_get', methods=['GET'])
def ask_get():
    question = request.args.get('q', '').strip()
    
    if not question:
        return jsonify({"error": "استخدم ?q=سؤالك"}), 400
        
    # هذا المسار للاختبار، لا يحتاج لحالة مستخدم
    answer = generate_response_for_test(question)
    
    return jsonify({
        "success": True,
        "question": question,
        "answer": answer
    })

def generate_response_for_test(question):
    """دالة للاختبار فقط (بدون حالة مستخدم)"""
    question_lower = question.lower().strip()
    
    # نفس منطق الردود ولكن بدون التحقق من حالة المستخدم
    address_keywords = ['عنوان', 'مكان', 'الفرع', 'اين', 'موقع']
    if any(keyword in question_lower for keyword in address_keywords):
        return f"📍 العنوان: {STORE_INFO['address']}"
    
    contact_keywords = ['تليفون', 'هاتف', 'اتصل', 'رقم', 'واتساب']
    if any(keyword in question_lower for keyword in contact_keywords):
        return f"📞 للتواصل: {', '.join(STORE_INFO['phone_numbers'])}"
    
    return f"👋 مرحباً! أنا مساعد {STORE_INFO['name']}. كيف يمكنني مساعدتك؟"

def generate_response(question, user_id):
    """
    توليد رد ذكي مع الأخذ في الاعتبار حالة المستخدم (جديد أم لا).
    """
    question_lower = question.lower().strip()
    new_user = is_new_user(user_id)
    
    # ============ التحية للمستخدمين الجدد فقط ============
    # إذا كان المستخدم جديداً، نرسل له الترحيب والمعلومات الأساسية
    if new_user:
        return f"""👋 مرحباً بك في **{STORE_INFO['name']}**! أنا المساعد الذكي.

**معلومات المحل:**
📍 **العنوان:** {STORE_INFO['address']}
📞 **أرقام التواصل:** {', '.join(STORE_INFO['phone_numbers'])}
🕒 **مواعيد العمل:** {STORE_INFO['working_hours']['daily']}

يمكنك الآن سؤالي عن:
🔹 العنوان - اكتب "العنوان"
🔹 أرقام التواصل - اكتب "التواصل"
🔹 مواعيد العمل - اكتب "المواعيد"
🔹 **للتحدث مع خدمة العملاء** - اكتب "خدمة العملاء"

كيف أقدر أخدمك؟ 😊"""
    
    # ============ للمستخدمين القدامى، نتعامل مع الاستفسارات بشكل طبيعي ============
    
    # العنوان
    address_keywords = ['عنوان', 'مكان', 'الفرع', 'اين', 'موقع', 'address', 'location', 'وين']
    if any(keyword in question_lower for keyword in address_keywords):
        return f"""📍 **عنوان {STORE_INFO['name']}:**

{STORE_INFO['address']}

🗺️ **كيف تصل إلينا:**
• قريب من محطة مترو وسط البلد
• بجوار سينما مترو
• أمام بنك مصر

🕒 **مواعيد العمل:**
يومياً: {STORE_INFO['working_hours']['daily']}"""

    # التواصل
    contact_keywords = ['تليفون', 'هاتف', 'اتصل', 'رقم', 'contact', 'واتساب', 'whatsapp']
    if any(keyword in question_lower for keyword in contact_keywords):
        phones = "\n".join([f"📞 {phone}" for phone in STORE_INFO['phone_numbers']])
        whatsapp = "\n".join([f"📱 واتساب: {phone}" for phone in STORE_INFO['whatsapp_numbers']])
        
        return f"""📞 **أرقام التواصل:**

{phones}

{whatsapp}

📍 **العنوان:** {STORE_INFO['address']}"""

    # مواعيد العمل
    hours_keywords = ['مواعيد', 'يفتح', 'يغلق', 'اوقات', 'open', 'time', 'ساعات']
    if any(keyword in question_lower for keyword in hours_keywords):
        return f"""🕒 **مواعيد العمل:**

⏰ الأحد - الخميس: {STORE_INFO['working_hours']['daily']}
🎉 الجمعة والسبت: {STORE_INFO['working_hours']['weekend']}

✨ نستقبلكم طوال أيام الأسبوع"""

    # ============ خدمة العملاء (مهم: هنا بنرد برسالة فقط، والرسالة الأصلية بتظهر للعميل) ============
    customer_service_keywords = ['خدمة العملاء', 'كلم موظف', 'موظف', 'محادثة', 'support', 'customer', 'الدعم']
    if any(keyword in question_lower for keyword in customer_service_keywords):
        return f"""👤 **تم تحويلك إلى خدمة العملاء**

شكراً لتواصلك مع {STORE_INFO['name']}. سيتم الرد عليك من أحد ممثلي خدمة العملاء في أقرب وقت.

⏳ **مدة الانتظار المتوقعة:** 5-15 دقيقة

📞 للتواصل السريع عبر واتساب: {STORE_INFO['whatsapp_numbers'][0]}"""

    # ============ أي استفسار آخر - نرد بشكل طبيعي ============
    # هنا بنرد على أي سؤال تاني (عشان كده شيلنا return None)
    return f"""👋 مرحباً في **{STORE_INFO['name']}**!

للحصول على المساعدة، اختر أحد الخيارات:

📍 اكتب "العنوان" لمعرفة موقعنا
📞 اكتب "التواصل" لأرقام التليفون
🕒 اكتب "المواعيد" لمعرفة أوقات العمل
👤 اكتب "خدمة العملاء" للتحدث مع موظف

كيف أقدر أساعدك؟ 😊"""

# ===================== فيسبوك Messenger =====================

def verify_fb_signature(payload, signature):
    if not FB_APP_SECRET or not signature:
        return True
    expected_sig = hmac.new(
        FB_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha1
    ).hexdigest()
    return hmac.compare_digest('sha1=' + expected_sig, signature)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == FB_VERIFY_TOKEN:
        print(f"✅ Facebook webhook verified!")
        return challenge, 200
    
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        signature = request.headers.get('X-Hub-Signature', '')
        if not verify_fb_signature(request.data, signature):
            print("❌ Invalid Facebook signature")
            return 'Invalid signature', 403

        data = request.get_json()

        if data.get('object') != 'page':
            return 'Not a page event', 404

        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):

                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')

                    if message_text:
                        print(f"📱 Facebook message from {sender_id}: {message_text}")
                        
                        # نمرر user_id للدالة
                        response_text = generate_response(message_text, sender_id)
                        
                        # ✅ الأهم: بس نبعتها لو مش None
                        if response_text is not None:
                            send_facebook_message(sender_id, response_text)
                            print(f"✅ تم إرسال رد تلقائي للرسالة: {message_text}")
                        else:
                            print(f"⏩ تم تخطي الرد التلقائي للرسالة: {message_text} (ستظهر في صندوق الوارد)")

        return 'EVENT_RECEIVED', 200

    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        import traceback
        traceback.print_exc()
        return 'Error processing request', 500

def send_facebook_message(recipient_id, message_text):
    if not FB_PAGE_TOKEN:
        print("⚠️ FB_PAGE_TOKEN not set.")
        return None

    url = f"https://graph.facebook.com/v18.0/me/messages"
    params = {'access_token': FB_PAGE_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ Message sent to {recipient_id}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending Facebook message: {e}")
        return False

@app.route('/fb_test', methods=['GET'])
def facebook_test():
    return jsonify({
        "store": STORE_INFO["name"],
        "address": STORE_INFO["address"],
        "phones": STORE_INFO["phone_numbers"],
        "hours": STORE_INFO["working_hours"],
        "webhook_url": "https://astramind-two.vercel.app/webhook",
        "verify_token": FB_VERIFY_TOKEN,
        "status": "✅ جاهز",
        "auto_reply": "الترحيب للمستخدمين الجدد فقط، ثم الردود التلقائية للعنوان والتواصل والمواعيد",
        "customer_service": "رسائل خدمة العملاء يرد عليها البوت برسالة تأكيد ثم تظهر في صندوق الوارد",
        "active_sessions": len(user_sessions)
    })

# ===================== تشغيل التطبيق =====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server running on port {port}")
    print(f"👑 Store: {STORE_INFO['name']}")
    print(f"📍 Address: {STORE_INFO['address']}")
    print(f"📞 Phones: {', '.join(STORE_INFO['phone_numbers'])}")
    print(f"🔗 Webhook: https://astramind-two.vercel.app/webhook")
    print(f"🔐 Verify Token: {FB_VERIFY_TOKEN}")
    print(f"🤖 Auto-reply: الترحيب للمستخدمين الجدد فقط، ثم الردود التلقائية للعنوان والتواصل والمواعيد")
    print(f"👤 Customer service: بيرد برسالة تأكيد ثم تظهر في inbox")
    app.run(host='0.0.0.0', port=port, debug=False)
