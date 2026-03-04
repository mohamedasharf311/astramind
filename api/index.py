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
    ]
}

# ===================== جلسات المستخدمين =====================
# هنتتبع حالة كل مستخدم
user_sessions = {}

def get_user_session(user_id):
    """ترجع بيانات جلسة المستخدم، أو تنشئها لو مش موجودة"""
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            "first_seen": time.time(),
            "auto_reply_enabled": True,  # البوت شغال افتراضياً
            "handed_over_to_human": False,  # اتمسلم لموظف ولا لأ
            "last_interaction": time.time()
        }
    return user_sessions[user_id]

def disable_auto_reply(user_id):
    """بتعطل الرد التلقائي للمستخدم ده"""
    session = get_user_session(user_id)
    session["auto_reply_enabled"] = False
    session["handed_over_to_human"] = True
    session["last_interaction"] = time.time()
    print(f"🔴 Auto-reply disabled for user {user_id}")

def is_auto_reply_enabled(user_id):
    """بتتأكد لو الرد التلقائي شغال للمستخدم ده"""
    session = get_user_session(user_id)
    # لو معداش عليها كتير (اختياري)
    return session.get("auto_reply_enabled", True)

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
            "/fb_test": "GET - اختبار اتصال فيسبوك",
            "/reset_user/:id": "GET - إعادة تفعيل البوت لمستخدم (للاختبار)"
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

@app.route('/reset_user/<user_id>', methods=['GET'])
def reset_user(user_id):
    """للاختبار: إعادة تفعيل البوت لمستخدم معين"""
    if user_id in user_sessions:
        user_sessions[user_id]["auto_reply_enabled"] = True
        user_sessions[user_id]["handed_over_to_human"] = False
        return jsonify({"success": True, "message": f"User {user_id} reset"})
    return jsonify({"success": False, "message": "User not found"})

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "يرجى إرسال سؤال"}), 400
            
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
        
    answer = generate_response_for_test(question)
    
    return jsonify({
        "success": True,
        "question": question,
        "answer": answer
    })

def generate_response_for_test(question):
    """دالة للاختبار فقط"""
    question_lower = question.lower().strip()
    
    address_keywords = ['عنوان', 'مكان', 'الفرع', 'اين', 'موقع']
    if any(keyword in question_lower for keyword in address_keywords):
        return f"📍 العنوان: {STORE_INFO['address']}"
    
    contact_keywords = ['تليفون', 'هاتف', 'اتصل', 'رقم', 'واتساب']
    if any(keyword in question_lower for keyword in contact_keywords):
        return f"📞 للتواصل: {', '.join(STORE_INFO['phone_numbers'])}"
    
    return f"👋 مرحباً! أنا مساعد {STORE_INFO['name']}. كيف يمكنني مساعدتك؟"

def generate_response(question, user_id):
    """
    توليد رد ذكي مع الأخذ في الاعتبار حالة المستخدم
    """
    question_lower = question.lower().strip()
    
    # ============ التحقق من كلمات تحويل لموظف بشري ============
    human_agent_keywords = [
        'خدمة العملاء', 'كلم موظف', 'موظف', 'محادثة', 'support', 'customer',
        'الدعم', 'انسان', 'بشري', 'حقيقي', 'حد من الصفحة', 'رد بشري',
        'human', 'agent', 'representative', 'موظف بشري', 'انسان حقيقي',
        'عايز اتكلم مع حد', 'كلمني موظف', 'كلم مسؤول', 'الادمن', 'المسؤول'
    ]
    
    # لو المستخدم طلب التحدث مع موظف بشري
    if any(keyword in question_lower for keyword in human_agent_keywords):
        # نعطل الرد التلقائي نهائياً للمستخدم ده
        disable_auto_reply(user_id)
        print(f"🟡 User {user_id} requested human agent. Auto-reply disabled.")
        
        # نرسل رسالة تأكيد إنه هيتحول لموظف
        return f"""👤 **تم تحويلك إلى خدمة العملاء البشرية**

شكراً لتواصلك مع {STORE_INFO['name']}. تم إيقاف الردود التلقائية وسيتم الرد عليك شخصياً من أحد ممثلي خدمة العملاء في أقرب وقت.

⏳ **مدة الانتظار المتوقعة:** 5-15 دقيقة

📞 للتواصل السريع عبر واتساب: {STORE_INFO['whatsapp_numbers'][0]}

**ملاحظة:** لن تصلك أي ردود تلقائية بعد الآن. رسائلك القادمة ستظهر مباشرة في صندوق الوارد لخدمة العملاء."""
    
    # ============ التحقق من حالة المستخدم ============
    # لو الرد التلقائي معطل للمستخدم ده، منبعتهاش أي رد
    if not is_auto_reply_enabled(user_id):
        print(f"⏩ Auto-reply disabled for user {user_id}. Message will appear in inbox.")
        return None  # منردش على الرسالة خالص
    
    # ============ للمستخدمين الجدد ============
    session = get_user_session(user_id)
    is_new = session.get("first_interaction", True)
    
    if is_new:
        session["first_interaction"] = False
        return f"""👋 مرحباً بك في **{STORE_INFO['name']}**! أنا المساعد الذكي.

**معلومات المحل:**
📍 **العنوان:** {STORE_INFO['address']}
📞 **أرقام التواصل:** {', '.join(STORE_INFO['phone_numbers'])}
🕒 **مواعيد العمل:** {STORE_INFO['working_hours']['daily']}

يمكنك الآن سؤالي عن:
🔹 العنوان - اكتب "العنوان"
🔹 أرقام التواصل - اكتب "التواصل"
🔹 مواعيد العمل - اكتب "المواعيد"
🔹 **للتحدث مع موظف بشري** - اكتب "خدمة العملاء" أو "انسان حقيقي"

كيف أقدر أخدمك؟ 😊"""
    
    # ============ العنوان ============
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

    # ============ التواصل ============
    contact_keywords = ['تليفون', 'هاتف', 'اتصل', 'رقم', 'contact', 'واتساب', 'whatsapp']
    if any(keyword in question_lower for keyword in contact_keywords):
        phones = "\n".join([f"📞 {phone}" for phone in STORE_INFO['phone_numbers']])
        whatsapp = "\n".join([f"📱 واتساب: {phone}" for phone in STORE_INFO['whatsapp_numbers']])
        
        return f"""📞 **أرقام التواصل:**

{phones}

{whatsapp}

📍 **العنوان:** {STORE_INFO['address']}"""

    # ============ مواعيد العمل ============
    hours_keywords = ['مواعيد', 'يفتح', 'يغلق', 'اوقات', 'open', 'time', 'ساعات']
    if any(keyword in question_lower for keyword in hours_keywords):
        return f"""🕒 **مواعيد العمل:**

⏰ الأحد - الخميس: {STORE_INFO['working_hours']['daily']}
🎉 الجمعة والسبت: {STORE_INFO['working_hours']['weekend']}

✨ نستقبلكم طوال أيام الأسبوع"""

    # ============ أي استفسار آخر ============
    return f"""👋 مرحباً في **{STORE_INFO['name']}**!

للحصول على المساعدة، اختر أحد الخيارات:

📍 اكتب "العنوان" لمعرفة موقعنا
📞 اكتب "التواصل" لأرقام التليفون
🕒 اكتب "المواعيد" لمعرفة أوقات العمل
👤 اكتب "خدمة العملاء" أو "انسان حقيقي" للتحدث مع موظف

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

                # ✅ هنا الأهم: بنتأكد لو الرسالة من الصفحة نفسها (أي أنا برد)
                # فيسبوك بتبعت حاجة إسمها is_echo عشان تقول دي رسالة من البوت أو من الصفحة
                message = messaging_event.get('message', {})
                sender_id = messaging_event['sender']['id']
                
                # لو دي رسالة من الصفحة (أنا الي برد)، بنعطل الرد التلقائي للمستخدم ده
                if message.get('is_echo'):
                    print(f"🔄 Echo message detected (page replied). Disabling auto-reply for {sender_id}")
                    disable_auto_reply(sender_id)
                    continue
                
                # لو في رسالة عادية من المستخدم
                if message:
                    message_text = message.get('text', '')

                    if message_text:
                        print(f"📱 Facebook message from {sender_id}: {message_text}")
                        
                        # نمرر user_id للدالة
                        response_text = generate_response(message_text, sender_id)
                        
                        # نبعتها لو مش None
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
        "auto_reply": "✓ الترحيب للمستخدمين الجدد\n✓ الردود على العنوان، التواصل، المواعيد\n✗ يتوقف نهائياً عندما:\n  - يطلب المستخدم 'خدمة العملاء' أو 'انسان حقيقي'\n  - تبدأ أنت بالرد على المستخدم",
        "active_sessions": len(user_sessions)
    })

# ===================== تشغيل التطبيق =====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server running on port {port}")
    print(f"👑 Store: {STORE_INFO['name']}")
    print("🚀 Auto-reply rules:")
    print("  ✓ New users: Welcome message")
    print("  ✓ Address, contact, hours: Auto-reply")
    print("  ✗ When user asks for 'human' or 'customer service': Disable auto-reply permanently")
    print("  ✗ When page admin replies: Disable auto-reply permanently")
    app.run(host='0.0.0.0', port=port, debug=False)
