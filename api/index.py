from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import requests
import json
import hashlib
import hmac
from datetime import datetime

app = Flask(__name__)
CORS(app)

print("🚀 Starting Training Center Enrollment Assistant...")

# ===================== إعدادات فيسبوك =====================
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "training_bot_2024")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAKqctOyqecBQRvAeGXRkb11K2AzRMelttUC2zVL7FdS7VFAVhVT1anKKV9ACkfZCXr2UzpAaILw6rN65BUqmDjaZC0tM81wiOtQ5ZCZBtHMwe0qm678azp1PC6bXxsYYOHfLLZCJS5ShMKsgRZAxjbk6ZAT8uS275lWrYP7s3ST6faoseYCwMzmxsZBeDOZBplnn3ZAa6ygZDZD")
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== بيانات مركز التدريب =====================
TRAINING_COURSES = {
    "python": {
        "name": "برمجة بايثون للمبتدئين",
        "description": "تعلم أساسيات برمجة Python من الصفر",
        "price": "500 ريال",
        "duration": "4 أسابيع",
        "schedule": ["الاثنين والأربعاء 6-8 مساءً", "السبت 10 صباحًا - 2 ظهرًا"]
    },
    "web": {
        "name": "تطوير الويب الشامل",
        "description": "HTML, CSS, JavaScript و React",
        "price": "800 ريال",
        "duration": "6 أسابيع",
        "schedule": ["الثلاثاء والخميس 7-9 مساءً"]
    },
    "data": {
        "name": "تحليل البيانات",
        "description": "تعلم Python، Pandas، وتصور البيانات",
        "price": "700 ريال",
        "duration": "5 أسابيع",
        "schedule": ["الأحد والثلاثاء 5-7 مساءً"]
    },
    "design": {
        "name": "تصميم الجرافيك",
        "description": "Photoshop، Illustrator وتصميم الشعارات",
        "price": "600 ريال",
        "duration": "4 أسابيع",
        "schedule": ["الاثنين والأربعاء 4-6 مساءً"]
    }
}

# ===================== تخزين بيانات المستخدمين =====================
user_sessions = {}

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد تسجيل مراكز التدريب 🤖",
        "status": "🟢 جاهز مع فيسبوك",
        "version": "1.0.0",
        "courses_available": list(TRAINING_COURSES.keys()),
        "endpoints": {
            "/": "GET - معلومات التطبيق",
            "/health": "GET - حالة النظام",
            "/webhook": "GET/POST - فيسبوك Messenger",
            "/courses": "GET - عرض الكورسات",
            "/enrollments": "GET - عرض التسجيلات"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "facebook_ready": bool(FB_PAGE_TOKEN),
        "courses_count": len(TRAINING_COURSES)
    })

@app.route('/courses', methods=['GET'])
def get_courses():
    """عرض جميع الكورسات المتاحة"""
    return jsonify({
        "courses": TRAINING_COURSES,
        "count": len(TRAINING_COURSES)
    })

@app.route('/enrollments', methods=['GET'])
def get_enrollments():
    """عرض التسجيلات النشطة"""
    active_sessions = {
        user_id: data 
        for user_id, data in user_sessions.items() 
        if data.get('phone') and data.get('course')
    }
    return jsonify({
        "enrollments": active_sessions,
        "count": len(active_sessions)
    })

def generate_response(user_id, message_text):
    """توليد رد ذكي بناءً على حالة المحادثة"""
    user_session = user_sessions.get(user_id, {})
    
    # تحويل الرسالة إلى صغيرة
    message_lower = message_text.lower().strip()
    
    # 1. إذا كان المستخدم يبدأ محادثة جديدة
    if any(word in message_lower for word in ['مرحبا', 'اهلا', 'السلام', 'اهلين', 'بداية']):
        user_sessions[user_id] = {"step": "welcome"}
        return "مرحباً بك في مركز التدريب! 👋\n\nماذا تريد معرفته؟\n\n• الكورسات المتاحة 🎯\n• الجداول الزمنية 📅\n• الأسعار 💰\n\nأو يمكنك التسجيل مباشرة في كورس! 💼"
    
    # 2. إذا سأل عن الكورسات المتاحة
    elif any(word in message_lower for word in ['كورسات', 'دورات', 'متاح', 'عرض', 'courses', 'available']):
        return get_courses_list()
    
    # 3. إذا سأل عن الجداول
    elif any(word in message_lower for word in ['جدول', 'مواعيد', 'اوقات', 'schedule', 'موعد']):
        return get_schedules_list()
    
    # 4. إذا سأل عن الأسعار
    elif any(word in message_lower for word in ['سعر', 'ثمن', 'رسوم', 'تكلفة', 'price', 'كم']):
        return get_prices_list()
    
    # 5. إذا كان يريد التسجيل
    elif any(word in message_lower for word in ['تسجيل', 'سجل', 'انضم', 'اريد', 'أريد', 'سجلني', 'enroll']):
        user_sessions[user_id] = {"step": "ask_course"}
        return "ممتاز! أي كورس تريد التسجيل فيه؟\n\n" + get_courses_list()
    
    # 6. إذا كان في مرحلة اختيار الكورس
    elif user_session.get('step') == 'ask_course':
        course_key = get_course_key(message_text)
        if course_key:
            user_sessions[user_id] = {
                "step": "ask_phone",
                "course": course_key,
                "course_name": TRAINING_COURSES[course_key]['name']
            }
            return f"رائع! اخترت '{TRAINING_COURSES[course_key]['name']}' 🌟\n\nالآن، ما هو رقم هاتفك للتواصل؟ 📱"
        else:
            return "الكورس غير معروف. يرجى اختيار كورس من القائمة:\n\n" + get_courses_list()
    
    # 7. إذا كان في مرحلة طلب رقم الهاتف
    elif user_session.get('step') == 'ask_phone':
        phone = extract_phone_number(message_text)
        if phone:
            course_key = user_session.get('course')
            course_name = TRAINING_COURSES[course_key]['name']
            
            user_sessions[user_id] = {
                **user_session,
                "phone": phone,
                "step": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
            # إرسال تأكيد للمسؤول
            notify_admin(user_id, course_name, phone)
            
            return "✅ تم استلام بياناتك!\n\n📞 فريقنا سيتواصل معك خلال 24 ساعة على الرقم: " + phone + "\n\nبخصوص كورس: " + course_name + "\n\nشكراً لثقتك بنا! 🙏"
        else:
            return "⚠️ يرجى إدخال رقم هاتف صحيح (مثال: 05XXXXXXXX أو 5XXXXXXXX)"
    
    # 8. البحث عن كورس محدد
    elif any(word in message_lower for word in ['بايثون', 'python', 'ويب', 'web', 'بيانات', 'data', 'تصميم', 'design']):
        course_key = get_course_key(message_text)
        if course_key:
            course = TRAINING_COURSES[course_key]
            return format_course_details(course_key, course)
        else:
            return "الكورس غير معروف. هذه الكورسات المتاحة:\n\n" + get_courses_list()
    
    # 9. رد افتراضي
    else:
        return "مرحباً! 👋 أنا مساعد التسجيل في مركز التدريب.\n\nأستطيع مساعدتك في:\n• عرض الكورسات المتاحة 🎓\n• الجداول الزمنية 📅\n• معرفة الأسعار 💰\n• التسجيل في الكورس 💼\n\nماذا تريد أن تعرف؟ 😊"

def get_courses_list():
    """تنسيق قائمة الكورسات"""
    courses_text = "📚 **الكورسات المتاحة:**\n\n"
    for key, course in TRAINING_COURSES.items():
        courses_text += f"🎯 **{course['name']}**\n"
        courses_text += f"   📝 {course['description']}\n"
        courses_text += f"   ⏰ {course['duration']}\n"
        courses_text += f"   💰 {course['price']}\n\n"
    
    courses_text += "للتسجيل، اكتب 'اريد التسجيل' أو 'سجلني'"
    return courses_text

def get_schedules_list():
    """تنسيق قائمة الجداول"""
    schedules_text = "📅 **الجداول الزمنية:**\n\n"
    for key, course in TRAINING_COURSES.items():
        schedules_text += f"🎯 **{course['name']}:**\n"
        for schedule in course['schedule']:
            schedules_text += f"   ⏰ {schedule}\n"
        schedules_text += "\n"
    return schedules_text

def get_prices_list():
    """تنسيق قائمة الأسعار"""
    prices_text = "💰 **الأسعار:**\n\n"
    for key, course in TRAINING_COURSES.items():
        prices_text += f"🎯 **{course['name']}:** {course['price']}\n"
        prices_text += f"   ⏰ {course['duration']}\n\n"
    
    prices_text += "🔹 خصم 10% للتسجيل المبكر\n🔹 خصم 15% للمجموعات (3 أشخاص فأكثر)"
    return prices_text

def format_course_details(key, course):
    """تنسيق تفاصيل كورس معين"""
    text = f"🎯 **{course['name']}**\n\n"
    text += f"📝 **الوصف:** {course['description']}\n\n"
    text += f"💰 **السعر:** {course['price']}\n"
    text += f"⏰ **المدة:** {course['duration']}\n\n"
    text += "📅 **الجداول المتاحة:**\n"
    for schedule in course['schedule']:
        text += f"• {schedule}\n"
    text += f"\nللتسجيل في هذا الكورس، اكتب 'اريد التسجيل في {key}'"
    return text

def get_course_key(message):
    """استخراج مفتاح الكورس من الرسالة"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['بايثون', 'python']):
        return 'python'
    elif any(word in message_lower for word in ['ويب', 'web', 'تطوير']):
        return 'web'
    elif any(word in message_lower for word in ['بيانات', 'data', 'تحليل']):
        return 'data'
    elif any(word in message_lower for word in ['تصميم', 'design', 'جرافيك']):
        return 'design'
    
    # تحقق من الكلمات المفتاحية المباشرة
    for key in TRAINING_COURSES.keys():
        if key in message_lower:
            return key
    
    return None

def extract_phone_number(text):
    """استخراج رقم الهاتف من النص"""
    import re
    
    # إزالة جميع غير الأرقام
    numbers = re.findall(r'\d+', text)
    phone = ''.join(numbers)
    
    # تحقق من طول الرقم (عادة 9-10 أرقام للسعودية)
    if 9 <= len(phone) <= 10:
        # إذا بدأ بـ 0، أزله
        if phone.startswith('0'):
            phone = phone[1:]
        return phone
    elif len(phone) > 10:
        # خذ أول 10 أرقام
        return phone[:10]
    
    return None

def notify_admin(user_id, course_name, phone):
    """إرسال إشعار للمسؤول"""
    print(f"📝 تسجيل جديد:")
    print(f"   👤 المستخدم: {user_id}")
    print(f"   🎯 الكورس: {course_name}")
    print(f"   📞 الهاتف: {phone}")
    print(f"   ⏰ الوقت: {datetime.now()}")
    
    # يمكنك إضافة إرسال بريد إلكتروني أو إشعار هنا
    # أو حفظ في قاعدة بيانات

# ===================== فيسبوك Messenger =====================

def verify_fb_signature(payload, signature):
    """التحقق من توقيع فيسبوك"""
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
    """التحقق من Webhook"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    print(f"🔍 Facebook verification attempt: mode={mode}, token={token}")

    if mode == 'subscribe' and token == FB_VERIFY_TOKEN:
        print(f"✅ Facebook webhook verified successfully!")
        return challenge, 200

    print(f"❌ Verification failed. Expected: {FB_VERIFY_TOKEN}, Got: {token}")
    return 'Verification token mismatch', 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """استقبال رسائل Messenger"""
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

                # رسالة نصية
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')

                    if message_text:
                        print(f"📱 Message from {sender_id}: {message_text}")
                        
                        # توليد الرد
                        response_text = generate_response(sender_id, message_text)
                        
                        # إرسال الرد
                        send_facebook_message(sender_id, response_text)

                # ضغط على زر
                elif messaging_event.get('postback'):
                    sender_id = messaging_event['sender']['id']
                    payload = messaging_event['postback']['payload']

                    print(f"📱 Postback from {sender_id}: {payload}")

                    postback_responses = {
                        'GET_STARTED': "مرحباً بك في مركز التدريب! 🎓\n\nأنا مساعد التسجيل. كيف يمكنني مساعدتك اليوم؟\n\n• الكورسات المتاحة 🎯\n• الجداول الزمنية 📅\n• الأسعار 💰\n• التسجيل في كورس 💼",
                        'COURSES': get_courses_list(),
                        'SCHEDULES': get_schedules_list(),
                        'PRICES': get_prices_list(),
                        'ENROLL': "ممتاز! للتسجيل، اكتب اسم الكورس الذي تريده:\n\n" + get_courses_list()
                    }

                    response_text = postback_responses.get(payload, 
                        "مرحباً! كيف يمكنني مساعدتك؟")

                    send_facebook_message(sender_id, response_text)

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
            return False

    except Exception as e:
        print(f"❌ Error sending Facebook message: {e}")
        return False

@app.route('/setup_fb', methods=['GET'])
def setup_facebook():
    """إعداد قائمة فيسبوك وأزرار"""

    if not FB_PAGE_TOKEN:
        return jsonify({
            "error": "FB_PAGE_TOKEN is not set"
        }), 400

    results = {}

    try:
        # إعداد زر Get Started
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

        # إعداد القائمة المستمرة
        menu_payload = {
            "persistent_menu": [
                {
                    "locale": "default",
                    "composer_input_disabled": False,
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "🎯 الكورسات المتاحة",
                            "payload": "COURSES"
                        },
                        {
                            "type": "postback",
                            "title": "📅 الجداول الزمنية",
                            "payload": "SCHEDULES"
                        },
                        {
                            "type": "postback",
                            "title": "💰 الأسعار",
                            "payload": "PRICES"
                        },
                        {
                            "type": "postback",
                            "title": "💼 التسجيل في كورس",
                            "payload": "ENROLL"
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
            "instructions": [
                "1. اذهب إلى Facebook Developers",
                "2. أنشئ App وأضف Messenger",
                "3. أضف Webhook URL: https://astramind-nine.vercel.app/webhook",
                f"4. أدخل Verify Token: {FB_VERIFY_TOKEN}",
                "5. اشترك في الأحداث: messages, messaging_postbacks",
                "6. أرسل رسالة للصفحة للاختبار"
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
    print(f"🎓 Training Center Enrollment Assistant")
    print(f"📚 Courses available: {list(TRAINING_COURSES.keys())}")
    print(f"🔗 Webhook URL: https://astramind-nine.vercel.app/webhook")
    app.run(host='0.0.0.0', port=port, debug=False)