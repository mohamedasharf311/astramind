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

print("🚀 Starting Dental AI Assistant with Facebook Messenger...")

# ===================== إعدادات فيسبوك =====================
# 1. Verify Token (تختاره أنت)
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "astra_dental_bot_2024")

# 2. Page Access Token (ستأخذه من Facebook Developers)
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")

# 3. App Secret (للتحقق من التوقيع - أمان إضافي)
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد عيادة الأسنان الذكي 🤖",
        "status": "🟢 جاهز مع فيسبوك",
        "version": "2.0.0",
        "messenger": "✅ متصل",
        "verify_token": FB_VERIFY_TOKEN,
        "endpoints": {
            "/health": "GET - حالة النظام",
            "/ask": "POST - طرح الأسئلة",
            "/ask_get": "GET - طرح الأسئلة (بسيط)",
            "/webhook": "GET/POST - فيسبوك Messenger",
            "/fb_test": "GET - اختبار اتصال فيسبوك",
            "/setup_fb": "GET - إعداد صفحة فيسبوك"
        },
        "facebook_setup": {
            "webhook_url": "https://astramind-nine.vercel.app/webhook",
            "verify_token": FB_VERIFY_TOKEN,
            "steps": "1. أضف Webhook في Facebook Developers 2. أدخل Verify Token 3. اشترك في الأحداث"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "dental-ai-messenger",
        "facebook_ready": bool(FB_PAGE_TOKEN),
        "webhook_url": "https://astramind-nine.vercel.app/webhook"
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "يرجى إرسال سؤال في حقل 'question'"}), 400
        
        question = data['question'].strip()
        answer = generate_response(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "model": "Dental Assistant AI"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/ask_get', methods=['GET'])
def ask_get():
    question = request.args.get('q', '').strip()
    
    if not question:
        return jsonify({"error": "استخدم ?q=سؤالك"}), 400
    
    answer = generate_response(question)
    
    return jsonify({
        "success": True,
        "question": question,
        "answer": answer
    })

def generate_response(question):
    """توليد رد ذكي"""
    question_lower = question.lower()
    
    responses = {
        'greeting': "مرحباً! 👋 أنا مساعد عيادة الأسنان الذكي. كيف يمكنني مساعدتك اليوم؟",
        'appointment': """📅 **لحجز موعد:**
• الهاتف: 0123456789
• الواتساب: 0123456789
• الأحد-الخميس: 8 صباحاً - 8 مساءً
• سياسة الإلغاء: مجاني قبل 24 ساعة""",
        
        'price': """💰 **أسعار الخدمات:**
• الكشف والتشخيص: 100 ريال
• تنظيف الأسنان: 150 ريال
• حشو الأسنان: 200-350 ريال
• علاج العصب: 500-800 ريال
• تقويم الأسنان: يبدأ من 5000 ريال

*الأسعار قابلة للتغيير حسب الحالة*""",
        
        'location': """📍 **معلومات العيادة:**
• العنوان: شارع الملك فهد، الرياض
• الهاتف: 0123456789
• الواتساب: 0123456789
• البريد: info@dental-clinic.com""",
        
        'hours': """🕒 **أوقات العمل:**
• الأحد ← الخميس: 8:00 ص - 8:00 م
• الجمعة والسبت: إجازة
• 📞 طوارئ 24 ساعة: 0123456789""",
        
        'emergency': """🚨 **للحالات الطارئة:**
• اتصل فوراً على: 0123456789
• يمكنك الحضور مباشرة للعيادة
• فريق الطوارئ متاح 24 ساعة
• لا تحتاج موعد مسبق""",
        
        'default': """مرحباً! 🤖 يمكنني مساعدتك في:
• حجز المواعيد والزيارات
• معلومات الأسعار والخدمات
• العنوان وطرق التواصل
• أوقات العمل والطوارئ
• استفسارات طبية عامة

ماذا تريد أن تعرف؟ 😊"""
    }
    
    # تحليل السؤال
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام', 'صباح', 'مساء']):
        return responses['greeting']
    
    elif any(word in question_lower for word in ['حجز', 'موعد', 'زيارة', 'كيف احجز', 'احجز']):
        return responses['appointment']
    
    elif any(word in question_lower for word in ['سعر', 'تكلفة', 'كم', 'ثمن', 'رسوم', 'دفع']):
        return responses['price']
    
    elif any(word in question_lower for word in ['عنوان', 'اين', 'مكان', 'موقع', 'خريطة']):
        return responses['location']
    
    elif any(word in question_lower for word in ['وقت', 'دوام', 'متى', 'يفتح', 'يغلق', 'ساعات']):
        return responses['hours']
    
    elif any(word in question_lower for word in ['طارئ', 'عاجل', 'ألم', 'وجع', 'اسعاف', 'مستعجل']):
        return responses['emergency']
    
    else:
        return responses['default']

# ===================== فيسبوك Messenger =====================

def verify_fb_signature(payload, signature):
    """التحقق من توقيع فيسبوك (لزيادة الأمان)"""
    if not FB_APP_SECRET or not signature:
        return True  # تخطي إذا لم يتم تعيين App Secret
    
    expected_sig = hmac.new(
        FB_APP_SECRET.encode('utf-8'),
        payload,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest('sha1=' + expected_sig, signature)

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """التحقق من Webhook - Facebook يرسل GET للتحقق"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    print(f"🔍 Facebook verification attempt: mode={mode}, token={token}")
    
    if mode == 'subscribe' and token == FB_VERIFY_TOKEN:
        print(f"✅ Facebook webhook verified successfully! Token: {FB_VERIFY_TOKEN}")
        return challenge, 200
    
    print(f"❌ Verification failed. Expected: {FB_VERIFY_TOKEN}, Got: {token}")
    return 'Verification token mismatch', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال رسائل Messenger"""
    try:
        # التحقق من التوقيع (أمان)
        signature = request.headers.get('X-Hub-Signature', '')
        if not verify_fb_signature(request.data, signature):
            print("❌ Invalid Facebook signature")
            return 'Invalid signature', 403
        
        data = request.get_json()
        
        # تأكد أن البيانات من صفحة فيسبوك
        if data.get('object') != 'page':
            return 'Not a page event', 404
        
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                
                # 1. رسالة نصية من مستخدم
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')
                    
                    if message_text:
                        print(f"📱 Facebook message from {sender_id}: {message_text}")
                        
                        # توليد الرد من المساعد
                        response_text = generate_response(message_text)
                        
                        # إرسال الرد إلى المستخدم
                        send_facebook_message(sender_id, response_text)
                
                # 2. ضغط على زر (Postback)
                elif messaging_event.get('postback'):
                    sender_id = messaging_event['sender']['id']
                    payload = messaging_event['postback']['payload']
                    
                    print(f"📱 Facebook postback from {sender_id}: {payload}")
                    
                    # ردود خاصة للأزرار
                    postback_responses = {
                        'GET_STARTED': "مرحباً! 👋 أنا مساعد عيادة الأسنان. اسألني عن الحجز، الأسعار، العنوان، أوقات العمل، أو الحالات الطارئة!",
                        'BOOK_APPOINTMENT': "📅 لحجز موعد:\n• اتصل بنا: 0123456789\n• الأحد-الخميس: 8 صباحاً - 8 مساءً\n• سياسة الإلغاء: مجاني قبل 24 ساعة",
                        'ASK_PRICE': "💰 الأسعار:\n• الكشف: 100 ريال\n• التنظيف: 150 ريال\n• الحشو: 200-350 ريال\n• علاج العصب: 500-800 ريال",
                        'ASK_LOCATION': "📍 العنوان:\nشارع الملك فهد، الرياض\n📞 الهاتف: 0123456789\n🕒 الأوقات: الأحد-الخميس 8 ص - 8 م"
                    }
                    
                    response_text = postback_responses.get(payload, 
                        "مرحباً! كيف يمكنني مساعدتك؟")
                    
                    send_facebook_message(sender_id, response_text)
                
                # 3. تأكيد تسليم الرسالة
                elif messaging_event.get('delivery'):
                    pass
                
                # 4. قراءة الرسالة
                elif messaging_event.get('read'):
                    pass
        
        return 'EVENT_RECEIVED', 200
        
    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        import traceback
        traceback.print_exc()
        return 'Error processing request', 500

def send_facebook_message(recipient_id, message_text):
    """إرسال رسالة إلى مستخدم فيسبوك"""
    if not FB_PAGE_TOKEN:
        print("⚠️ FB_PAGE_TOKEN not set. Cannot send message.")
        return None
    
    # تقصير الرسالة إذا كانت طويلة جداً
    if len(message_text) > 2000:
        message_text = message_text[:1997] + "..."
    
    url = f"https://graph.facebook.com/v18.0/me/messages"
    
    params = {'access_token': FB_PAGE_TOKEN}
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(
            url, 
            params=params, 
            json=payload, 
            headers=headers, 
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Message sent to {recipient_id}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending Facebook message: {e}")
        return False

@app.route('/fb_test', methods=['GET'])
def facebook_test():
    """اختبار اتصال فيسبوك"""
    return jsonify({
        "facebook_integration": True,
        "verify_token_set": bool(FB_VERIFY_TOKEN),
        "page_token_set": bool(FB_PAGE_TOKEN),
        "webhook_url": "https://astramind-nine.vercel.app/webhook",
        "verify_token": FB_VERIFY_TOKEN,
        "test_url": f"https://astramind-nine.vercel.app/webhook?hub.mode=subscribe&hub.verify_token={FB_VERIFY_TOKEN}&hub.challenge=123456",
        "setup_instructions": [
            "1. Go to Facebook Developers",
            "2. Create App → Add Messenger",
            f"3. Webhook URL: https://astramind-nine.vercel.app/webhook",
            f"4. Verify Token: {FB_VERIFY_TOKEN}",
            "5. Subscribe to: messages, messaging_postbacks",
            "6. Generate Page Access Token",
            "7. Add tokens to Vercel Environment Variables"
        ]
    })

@app.route('/setup_fb', methods=['GET'])
def setup_facebook():
    """إعداد قائمة فيسبوك وأزرار"""
    
    if not FB_PAGE_TOKEN:
        return jsonify({
            "error": "FB_PAGE_TOKEN is not set",
            "solution": "Add FB_PAGE_TOKEN to Vercel Environment Variables"
        }), 400
    
    results = {}
    
    try:
        # 1. إعداد زر Get Started
        get_started_url = "https://graph.facebook.com/v18.0/me/messenger_profile"
        
        get_started_payload = {
            "get_started": {"payload": "GET_STARTED"},
            "whitelisted_domains": ["https://astramind-nine.vercel.app"]
        }
        
        response1 = requests.post(
            get_started_url,
            params={'access_token': FB_PAGE_TOKEN},
            json=get_started_payload
        )
        results['get_started'] = response1.status_code == 200
        
        # 2. إعداد القائمة المستمرة
        menu_payload = {
            "persistent_menu": [
                {
                    "locale": "default",
                    "composer_input_disabled": False,
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "📅 حجز موعد",
                            "payload": "BOOK_APPOINTMENT"
                        },
                        {
                            "type": "postback",
                            "title": "💰 الأسعار",
                            "payload": "ASK_PRICE"
                        },
                        {
                            "type": "postback",
                            "title": "📍 العنوان",
                            "payload": "ASK_LOCATION"
                        }
                    ]
                }
            ]
        }
        
        response2 = requests.post(
            get_started_url,
            params={'access_token': FB_PAGE_TOKEN},
            json=menu_payload
        )
        results['persistent_menu'] = response2.status_code == 200
        
        return jsonify({
            "success": True,
            "results": results,
            "message": "Facebook page setup completed!",
            "next_steps": [
                f"1. Open: https://astramind-nine.vercel.app/fb_test",
                "2. Copy the Verify Token",
                "3. Go to Facebook Developers → Webhook",
                "4. Add the Webhook URL and Verify Token",
                "5. Subscribe your page to events",
                "6. Send a message to your Facebook page!"
            ]
        })
        
    except Exception as e:
        return jsonify({
            "error": str(e),
            "success": False
        }), 500

# ===================== تشغيل التطبيق =====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server running on port {port}")
    print(f"🤖 Dental AI Assistant with Facebook Messenger")
    print(f"🔑 Verify Token: {FB_VERIFY_TOKEN}")
    print(f"🔗 Webhook URL: https://astramind-nine.vercel.app/webhook")
    print(f"📱 Test URL: https://astramind-nine.vercel.app/fb_test")
    app.run(host='0.0.0.0', port=port, debug=False)
