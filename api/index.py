from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import requests
import json
import hashlib
import hmac

app = Flask(__name__)
CORS(app)

print("🚀 Starting The King Suits Store AI Assistant...")

# ===================== إعدادات فيسبوك =====================
# 1. Verify Token (تختاره أنت)
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "the_king_store_bot_2024")

# 2. Page Access Token - ضروري جداً
# احصل عليه من: https://developers.facebook.com/apps/
# أو ضعه في متغيرات Vercel باسم FB_PAGE_TOKEN
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAKqctOyqecBQRvAeGXRkb11K2AzRMelttUC2zVL7FdS7VFAVhVT1anKKV9ACkfZCXr2UzpAaILw6rN65BUqmDjaZC0tM81wiOtQ5ZCZBtHMwe0qm678azp1PC6bXxsYYOHfLLZCJS5ShMKsgRZAxjbk6ZAT8uS275lWrYP7s3ST6faoseYCwMzmxsZBeDOZBplnn3ZAa6ygZDZD")

# 3. App Secret (اختياري)
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== المعلومات الأساسية للمحل =====================
STORE_INFO = {
    "name": "The King 👑",
    "description": "محل سوتيس (ملابس جاهزة) - The King",
    "address": "وسط البلد - شارع طلعت حرب - بجانب سينما مترو",
    "phone_numbers": ["01553082672", "01017788206", "01159110136"],
    "whatsapp_numbers": ["01553082672", "01017788206"],
    "working_hours": {
        "daily": "10:00 صباحاً - 12:00 منتصف الليل",
        "weekend": "10:00 صباحاً - 2:00 صباحاً"
    }
}

@app.route('/')
def home():
    return jsonify({
        "service": "مساعد محل The King (سوتيس) الذكي 🤖",
        "status": "🟢 جاهز" if FB_PAGE_TOKEN else "⚠️ يحتاج FB_PAGE_TOKEN",
        "facebook": "✅ متصل" if FB_PAGE_TOKEN else "❌ غير متصل",
        "tokens": {
            "verify_token": FB_VERIFY_TOKEN,
            "page_token_exists": bool(FB_PAGE_TOKEN),
            "page_token_length": len(FB_PAGE_TOKEN) if FB_PAGE_TOKEN else 0
        },
        "endpoints": {
            "/health": "GET - حالة النظام",
            "/ask": "POST - طرح الأسئلة",
            "/ask_get": "GET - طرح الأسئلة (بسيط)",
            "/webhook": "GET/POST - فيسبوك Messenger",
            "/fb_test": "GET - اختبار اتصال فيسبوك",
            "/test_reply": "GET - اختبار إرسال رسالة"
        },
        "instructions": "أرسل رسالة لصفحتك على فيسبوك وسأرد عليك تلقائياً!"
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "facebook_token": "present" if FB_PAGE_TOKEN else "missing",
        "webhook_active": True,
        "store": STORE_INFO["name"]
    })

@app.route('/test_reply', methods=['GET'])
def test_reply():
    """اختبار إرسال رسالة مباشرة"""
    recipient_id = request.args.get('user_id', '')
    test_message = request.args.get('message', 'مرحباً، هذا اختبار من The King! 👑')
    
    if not recipient_id:
        return jsonify({
            "error": "أضف ?user_id=رقم_المستخدم",
            "example": "/test_reply?user_id=123456&message=مرحباً"
        }), 400
    
    result = send_facebook_message(recipient_id, test_message)
    
    return jsonify({
        "success": result,
        "message": test_message,
        "recipient": recipient_id,
        "token_exists": bool(FB_PAGE_TOKEN)
    })

# ===================== توليد الردود =====================
def generate_response(question):
    """توليد رد ذكي - معدّل لمحل The King"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام']):
        return f"مرحباً! 👋 أنا مساعد محل {STORE_INFO['name']} - متخصص في السوتيس الجاهزة 👔\n\nكيف يمكنني خدمتك؟"
    
    elif any(word in question_lower for word in ['سوتيس', 'بدلة', 'جاكيت']):
        return """👔 **أنواع السوتيس المتوفرة:**
• سوتيس كاملة (3 قطع)
• جواكيت منفردة
• بناطيل رسمية
• قمصان رجالية

أي نوع تفضل؟"""
    
    elif any(word in question_lower for word in ['سعر', 'ثمن', 'كم']):
        return """💰 **أسعار السوتيس:**
• سوتيس كاملة: 800 - 4000 جنيه
• جواكيت: 500 - 1500 جنيه
• خصم 20% على السوتيس الكاملة!"""
    
    elif any(word in question_lower for word in ['عنوان', 'مكان', 'اين']):
        return f"📍 **العنوان:** {STORE_INFO['address']}"
    
    elif any(word in question_lower for word in ['هاتف', 'رقم', 'اتصل']):
        phones = "، ".join(STORE_INFO['phone_numbers'])
        return f"📞 **التليفونات:** {phones}"
    
    elif any(word in question_lower for word in ['مواعيد', 'يفتح', 'يغلق']):
        return f"🕒 **مواعيد العمل:**\nيومياً: {STORE_INFO['working_hours']['daily']}"
    
    else:
        return f"""مرحباً في {STORE_INFO['name']}! 👑

يمكنني مساعدتك في:
• أنواع السوتيس والأسعار
• العنوان ومواعيد العمل
• أرقام التواصل
• خدمة التوصيل

اسألني عمّا تريد! 😊"""

# ===================== فيسبوك Webhook =====================
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """التحقق من Webhook"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"🔍 Facebook verification: mode={mode}, token={token}")
    
    if mode == 'subscribe' and token == FB_VERIFY_TOKEN:
        print("✅ Facebook webhook verified!")
        return challenge, 200
    
    return 'Verification failed', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال رسائل Messenger"""
    try:
        data = request.get_json()
        
        if data.get('object') != 'page':
            return 'Not a page event', 404
        
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                
                # رسالة نصية
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')
                    
                    if message_text:
                        print(f"📱 رسالة من {sender_id}: {message_text}")
                        
                        # توليد الرد
                        response_text = generate_response(message_text)
                        
                        # إرسال الرد
                        success = send_facebook_message(sender_id, response_text)
                        
                        if success:
                            print(f"✅ تم إرسال الرد لـ {sender_id}")
                        else:
                            print(f"❌ فشل إرسال الرد لـ {sender_id}")
                
                # Postback (ضغط زر)
                elif messaging_event.get('postback'):
                    sender_id = messaging_event['sender']['id']
                    payload = messaging_event['postback']['payload']
                    
                    print(f"📱 Postback من {sender_id}: {payload}")
                    
                    # ردود للأزرار
                    if payload == 'GET_STARTED':
                        response_text = f"مرحباً! 👋 أنا مساعد {STORE_INFO['name']}\nكيف يمكنني خدمتك؟"
                    else:
                        response_text = generate_response(payload)
                    
                    send_facebook_message(sender_id, response_text)
        
        return 'EVENT_RECEIVED', 200
        
    except Exception as e:
        print(f"❌ خطأ في webhook: {e}")
        import traceback
        traceback.print_exc()
        return 'Error', 500

def send_facebook_message(recipient_id, message_text):
    """إرسال رسالة إلى مستخدم فيسبوك"""
    if not FB_PAGE_TOKEN:
        print("❌ FB_PAGE_TOKEN غير موجود!")
        return False
    
    url = "https://graph.facebook.com/v18.0/me/messages"
    
    params = {'access_token': FB_PAGE_TOKEN}
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
        
        print(f"📤 إرسال لـ {recipient_id}: status={response.status_code}")
        
        if response.status_code == 200:
            return True
        else:
            print(f"❌ فشل الإرسال: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الإرسال: {e}")
        return False

@app.route('/fb_test', methods=['GET'])
def facebook_test():
    """صفحة اختبار مفصلة"""
    return jsonify({
        "store": STORE_INFO["name"],
        "status": "running",
        "tokens": {
            "verify_token": FB_VERIFY_TOKEN,
            "page_token_configured": bool(FB_PAGE_TOKEN),
            "page_token_preview": FB_PAGE_TOKEN[:20] + "..." if FB_PAGE_TOKEN and len(FB_PAGE_TOKEN) > 20 else FB_PAGE_TOKEN
        },
        "webhook": {
            "url": "https://astramind-nine.vercel.app/webhook",
            "verification_url": f"https://astramind-nine.vercel.app/webhook?hub.mode=subscribe&hub.verify_token={FB_VERIFY_TOKEN}&hub.challenge=123456"
        },
        "diagnostic": {
            "received_webhook_requests": True,  # كما يظهر في السجلات
            "message_sending_ready": bool(FB_PAGE_TOKEN),
            "store_info_loaded": bool(STORE_INFO)
        },
        "setup_steps": [
            "1. تأكد من وجود FB_PAGE_TOKEN في Vercel Environment Variables",
            "2. في Facebook Developers → Messenger → Settings",
            "3. Webhooks → Setup Webhooks",
            f"4. Callback URL: https://astramind-nine.vercel.app/webhook",
            f"5. Verify Token: {FB_VERIFY_TOKEN}",
            "6. Subscribe to: messages, messaging_postbacks",
            "7. اختر الصفحة → Generate Token → نسخه → وضعه في Vercel",
            "8. أرسل رسالة لصفحتك على فيسبوك!"
        ]
    })

# ===================== تشغيل التطبيق =====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 السيرفر شغال على port {port}")
    print(f"👑 محل: {STORE_INFO['name']}")
    print(f"📍 العنوان: {STORE_INFO['address']}")
    print(f"📞 التليفونات: {', '.join(STORE_INFO['phone_numbers'])}")
    print(f"🔗 Webhook URL: https://astramind-nine.vercel.app/webhook")
    print(f"🔐 Verify Token: {FB_VERIFY_TOKEN}")
    print(f"📱 FB_PAGE_TOKEN موجود: {'✅ نعم' if FB_PAGE_TOKEN else '❌ لا'}")
    
    if FB_PAGE_TOKEN:
        print("🎉 التطبيق جاهز للرد على رسائل فيسبوك!")
    else:
        print("⚠️ تحتاج إلى إضافة FB_PAGE_TOKEN في Vercel")
        print("💡 اذهب إلى Vercel → Project → Settings → Environment Variables")
        print("💡 أضف متغير: FB_PAGE_TOKEN=رقم_التوكن_الطويل")
    
    app.run(host='0.0.0.0', port=port, debug=False)
