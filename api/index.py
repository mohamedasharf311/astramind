# ============================================
# 📱 FACEBOOK MESSENGER INTEGRATION
# ============================================
from fb_simple import fb
app.register_blueprint(fb)
FACEBOOK_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "dental_clinic_123")
FACEBOOK_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """تحقق من Webhook - مطلوب من فيسبوك"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == FACEBOOK_VERIFY_TOKEN:
            print("✅ تم التحقق من Webhook بنجاح!")
            return challenge
        else:
            return 'Verification token mismatch', 403
    
    return 'Invalid request', 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """معالجة رسائل Messenger"""
    data = request.get_json()
    
    # تأكيد الاشتراك من فيسبوك
    if data.get('object') == 'page':
        for entry in data.get('entry', []):
            for messaging_event in entry.get('messaging', []):
                
                # رسالة جديدة
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')
                    
                    if message_text:
                        print(f"📱 رسالة من {sender_id}: {message_text}")
                        
                        # الحصول على الرد من المساعد
                        answer = get_assistant_response(message_text)
                        
                        # إرسال الرد
                        send_facebook_message(sender_id, answer)
                
                # رسالة مثل (Like, Share)
                elif messaging_event.get('postback'):
                    sender_id = messaging_event['sender']['id']
                    payload = messaging_event['postback']['payload']
                    print(f"📱 تفاعل من {sender_id}: {payload}")
        
        return 'EVENT_RECEIVED', 200
    
    return 'Not Found', 404

def get_assistant_response(question):
    """الحصول على رد من المساعد"""
    try:
        # استخدام نفس منطق الرد
        context = knowledge_base.get_context_for_question(question)
        answer = qwen_client.generate(context, question)
        
        # تقصير الرد إذا كان طويلاً
        if len(answer) > 600:
            sentences = answer.split('.')
            answer = '. '.join(sentences[:3]) + '.'
        
        return answer
    
    except Exception as e:
        print(f"❌ خطأ في توليد الرد: {e}")
        return "مرحباً! أنا مساعد عيادة الأسنان. للأسعار والحجز: 0112345678"

def send_facebook_message(recipient_id, message_text):
    """إرسال رسالة إلى مستخدم فيسبوك"""
    if not FACEBOOK_PAGE_TOKEN:
        print("⚠️ FB_PAGE_TOKEN غير مضبوط")
        return
    
    url = f"https://graph.facebook.com/v18.0/me/messages?access_token={FACEBOOK_PAGE_TOKEN}"
    
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
        "messaging_type": "RESPONSE"
    }
    
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"✅ تم إرسال الرد إلى {recipient_id}")
        else:
            print(f"❌ خطأ في إرسال الرسالة: {response.status_code}")
            print(response.json())
    
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {e}")

# إضافة زر ابدأ للفيسبوك
@app.route('/setup_fb_profile', methods=['GET'])
def setup_facebook_profile():
    """إعداد صفحة فيسبوك مع زر ابدأ"""
    
    page_token = os.environ.get("FB_PAGE_TOKEN", "")
    
    if not page_token:
        return jsonify({"error": "FB_PAGE_TOKEN غير مضبوط"}), 400
    
    # 1. إعداد زر "Get Started"
    get_started_url = f"https://graph.facebook.com/v18.0/me/messenger_profile?access_token={page_token}"
    
    get_started_payload = {
        "get_started": {"payload": "GET_STARTED"}
    }
    
    # 2. إعداد القائمة المستمرة
    persistent_menu_url = f"https://graph.facebook.com/v18.0/me/messenger_profile?access_token={page_token}"
    
    persistent_menu_payload = {
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
                        "payload": "PRICES"
                    },
                    {
                        "type": "postback",
                        "title": "📍 العنوان",
                        "payload": "LOCATION"
                    },
                    {
                        "type": "web_url",
                        "title": "🌐 الموقع الإلكتروني",
                        "url": "https://www.dental-clinic.com"
                    }
                ]
            }
        ]
    }
    
    try:
        # إرسال طلبات الإعداد
        response1 = requests.post(get_started_url, json=get_started_payload)
        response2 = requests.post(persistent_menu_url, json=persistent_menu_payload)
        
        return jsonify({
            "success": True,
            "get_started": response1.status_code == 200,
            "persistent_menu": response2.status_code == 200,
            "message": "تم إعداد صفحة فيسبوك بنجاح!"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
