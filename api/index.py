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

print("🚀 Starting The King Store AI Assistant with Facebook Messenger...")

# ===================== إعدادات فيسبوك =====================
# 1. Verify Token (تختاره أنت)
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "the_king_store_bot_2024")

# 2. Page Access Token (ستأخذه من Facebook Developers)
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "")

# 3. App Secret (للتحقق من التوقيع - أمان إضافي)
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== المعلومات الأساسية للمحل =====================
STORE_INFO = {
    "name": "محل The King 👑",
    "address": "وسط البلد - شارع طلعت حرب - بجانب سينما مترو",
    "phone_numbers": ["01553082672", "01017788206", "01159110136"],
    "working_hours": {
        "daily": "10:00 صباحاً - 12:00 منتصف الليل",
        "weekend": "10:00 صباحاً - 2:00 صباحاً"
    },
    "categories": [
        "ملابس رجالية 👔",
        "ملابس حريمي 👗", 
        "أحذية 👟",
        "إكسسوارات 💍",
        "عطور 💎"
    ]
}

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد محل The King الذكي 🤖",
        "status": "🟢 جاهز مع فيسبوك",
        "version": "2.0.0",
        "messenger": "✅ متصل" if FB_PAGE_TOKEN else "❌ يحتاج إعداد",
        "store_info": STORE_INFO,
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
        "service": "the-king-store-messenger",
        "facebook_ready": bool(FB_PAGE_TOKEN),
        "store_name": STORE_INFO["name"],
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
            "model": "The King Store AI Assistant"
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
    """توليد رد ذكي - معدّل لمحل The King"""
    question_lower = question.lower()

    # توليد ردود ذكية بناءً على السؤال
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام', 'صباح', 'مساء', 'بداية', 'هلا', 'اهلين']):
        return f"""مرحباً! 👋 أنا مساعد محل **{STORE_INFO['name']}**

🎉 كيف يمكنني خدمتك اليوم؟

يمكنك معرفة:
• المنتجات المتوفرة 🛍️
• الأسعار والعروض 💰
• عنوان المحل 📍
• أوامر الشراء والتوصيل 🚚
• مواعيد العمل 🕒

ماذا تحتاج؟ 😊"""

    elif any(word in question_lower for word in ['منتج', 'منتجات', 'عندكم', 'أقسام', 'أشياء', 'البضاعه', 'البضاعة', 'category']):
        return f"""🛍️ **الأقسام المتوفرة في {STORE_INFO['name']}:**

{chr(10).join(['• ' + cat for cat in STORE_INFO['categories']])}

🎯 **أفضل المنتجات:**
• جواكيت رجالي ماركات عالمية
• فساتين سهرة بتصميمات مميزة
• أحذية رياضية وعادية
• إكسسوارات ذهب ومجوهرات
• عطور فرنسية وإيطالية

أي قسم يهمك؟"""

    elif any(word in question_lower for word in ['سعر', 'ثمن', 'كم', 'تكلفة', 'غالي', 'رخيص', 'price', 'عرض', 'خصم']):
        return """💰 **الأسعار والعروض:**

👔 **ملابس رجالية:**
• قمصان: 150 - 300 جنيه
• بناطيل: 200 - 400 جنيه
• جواكيت: 500 - 1200 جنيه

👗 **ملابس حريمي:**
• بلوزات: 100 - 250 جنيه
• فساتين: 300 - 800 جنيه
• تنانير: 150 - 350 جنيه

👟 **أحذية:**
• رجالي: 250 - 600 جنيه
• حريمي: 200 - 500 جنيه

💎 **عطور:**
• عطور محلية: 100 - 300 جنيه
• عطور عالمية: 500 - 2000 جنيه

🎁 **عروض خاصة:**
• خصم 20% على شراء قطعتين أو أكثر
• توصيل مجاني للطلبات فوق 500 جنيه
• هدايا مع كل عملية شراء

💡 *الأسعار قد تختلف حسب الموديل والماركة*"""

    elif any(word in question_lower for word in ['عنوان', 'مكان', 'الفرع', 'المحل', 'اين', 'موقع', 'address', 'location']):
        return f"""📍 **عنوان {STORE_INFO['name']}:**

{STORE_INFO['address']}

🗺️ **كيف تصل إلينا:**
• قريب من محطة مترو وسط البلد
• بجوار سينما مترو
• أمام بنك مصر

🚗 **مواقف سيارات:**
• موقف مجاني أمام المحل
• مواقف عامة بجوار السينما

🕒 **مواعيد العمل:**
يومياً: {STORE_INFO['working_hours']['daily']}
الجمعة والسبت: {STORE_INFO['working_hours']['weekend']}"""

    elif any(word in question_lower for word in ['تليفون', 'هاتف', 'اتصل', 'رقم', 'contact', 'ارقام', 'كلم']):
        phones_formatted = chr(10).join([f"• {phone}" for phone in STORE_INFO['phone_numbers']])
        return f"""📞 **ارتباط تواصل {STORE_INFO['name']}:**

{phones_formatted}

📱 **الواتساب متوفر على جميع الأرقام**
💬 **تليجرام: @thekingstore**
📧 **البريد الإلكتروني: info@thekingstore.com**

⏰ **أوقات الرد:**
يومياً من 10 صباحاً حتى 12 مساءً
نرد على الاستفسارات خلال 15 دقيقة"""

    elif any(word in question_lower for word in ['مواعيد', 'يفتح', 'يغلق', 'متاح', 'اوقات', 'open', 'close', 'time']):
        return f"""🕒 **مواعيد عمل {STORE_INFO['name']}:**

⏰ **يومياً (الأحد - الخميس):**
{STORE_INFO['working_hours']['daily']}

🎉 **الجمعة والسبت والعطلات:**
{STORE_INFO['working_hours']['weekend']}

✨ **أوقات الذروة:**
• 6:00 مساءً - 10:00 مساءً (منتصف الأسبوع)
• 8:00 مساءً - 1:00 صباحاً (نهاية الأسبوع)

💡 *ننصح بالحضور في غير أوقات الذروة لتجربة تسوق أفضل*"""

    elif any(word in question_lower for word in ['شراء', 'اطلب', 'طلب', 'اوردر', 'عايز', 'أريد', 'اشتري', 'order', 'buy']):
        return """🛒 **طريقة الشراء من The King:**

**الشراء من المحل:**
1. تفضل بزيارتنا في العنوان المذكور
2. اختر المنتجات التي تناسبك
3. جرب المنتج قبل الشراء
4. الدفع نقداً أو ببطاقة الائتمان

**الشراء أونلاين:**
1. اختر المنتج المطلوب
2. أرسل لنا الصورة على الواتساب
3. حدد المقاس واللون
4. نحدد السعر والتكلفة الإجمالية
5. نأكد الطلب ونحدد موعد التوصيل

**التوصيل:**
• مجاني للطلبات فوق 500 جنيه داخل القاهرة
• تكلفة 30 جنيه للطلبات الأقل
• التوصيل خلال 24-48 ساعة

**الإرجاع والاستبدال:**
• استبدال خلال 7 أيام من الشراء
• يشترط وجود الفاتورة
• المنتج بحالته الأصلية

ماذا تريد أن تشتري؟ 😊"""

    elif any(word in question_lower for word in ['توصيل', 'شحن', 'delivery', 'ship', 'وصل', 'ميعاد']):
        return """🚚 **خدمة التوصيل:**

**نطاق التوصيل:**
• القاهرة: جميع المناطق
• الجيزة: المناطق الرئيسية
• القليوبية: بعض المناطق

**تكلفة التوصيل:**
• مجاني للطلبات فوق 500 جنيه
• 30 جنيه للطلبات من 200-500 جنيه
• 50 جنيه للطلبات أقل من 200 جنيه

**مدة التوصيل:**
• داخل القاهرة: 24-48 ساعة
• خارج القاهرة: 2-4 أيام عمل

**طريقة التوصيل:**
1. تأكيد الطلب والدفع
2. تجهيز المنتج والتغليف
3. إرسال رقم التتبع
4. التوصيل للمنزل

**ملاحظات هامة:**
• الدفع عند الاستلام متاح
• فحص المنتج قبل الدفع
• إمكانية الإرجاع خلال 7 أيام"""

    elif any(word in question_lower for word in ['ماركات', 'brands', 'اصلي', 'جودة', 'quality', 'نوعية']):
        return """🏆 **الماركات المتوفرة:**

**ملابس رجالية:**
• Zara • H&M • LC Waikiki
• Tommy Hilfiger • Calvin Klein
• ماركات تركية وإيطالية

**ملابس حريمي:**
• Mango • Stradivarius • Bershka
• ماركات فرنسية وإسبانية
• تصميمات حصرية للمحل

**أحذية:**
• Nike • Adidas • Puma
• ماركات محلية عالية الجودة
• أحذية جلد طبيعي

**عطور:**
• French Pride • Italian Style
• Arabian Oud • Swiss Arabian
• عطور تركية وفرنسية

**ضمان الجودة:**
• جميع المنتجات أصلية
• فحص الجودة قبل البيع
• ضمان ضد عيوب الصنعة
• خدمة ما بعد البيع"""

    elif any(word in question_lower for word in ['مقاس', 'size', 'قاس', 'كبير', 'صغير', 'وسط']):
        return """📏 **دليل المقاسات:**

**ملابس رجالية:**
• Small (S): صدر 90-95 سم
• Medium (M): صدر 96-101 سم
• Large (L): صدر 102-107 سم
• XL: صدر 108-113 سم
• XXL: صدر 114-119 سم

**ملابس حريمي:**
• 36: صدر 80 سم
• 38: صدر 84 سم
• 40: صدر 88 سم
• 42: صدر 92 سم
• 44: صدر 96 سم

**أحذية رجالية:**
• من 40 إلى 46

**أحذية حريمي:**
• من 35 إلى 41

**نصائح:**
• يمكنك تجربة المقاس في المحل
• مقاساتنا مطابقة للمقاسات العالمية
• لدينا خدمة تبديل المقاسات"""

    elif any(word in question_lower for word in ['شكرا', 'ممتاز', 'حلو', 'تمام', 'thanks', 'thank']):
        return """🙏 **شكراً لثقتك في {STORE_INFO['name']}!**

يسعدنا خدمتك دائماً 👑

🎁 **تذكير:**
• لا تنسى تسجيل رقم هاتفك للحصول على عروض حصرية
• تابعنا على وسائل التواصل الاجتماعي
• تقييمك يهمنا كثيراً

نتمنى لك يوماً سعيداً! 😊""".format(STORE_INFO=STORE_INFO)

    else:
        return f"""👑 **مرحباً في {STORE_INFO['name']}!**

أنا المساعد الذكي للمحل، يمكنني مساعدتك في:

🛍️ **معلومات المنتجات والأقسام**
💰 **الأسعار والعروض الحالية**
📍 **عنوان المحل ومواعيد العمل**
📞 **أرقام التواصل والاستفسارات**
🚚 **خدمة التوصيل وطرق الشراء**
📏 **المقاسات والماركات المتوفرة**

ماذا تحتاج مني اليوم؟ 😊"""

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

                    # ردود خاصة للأزرار - معدّلة لمحل The King
                    postback_responses = {
                        'GET_STARTED': f"""مرحباً بك في {STORE_INFO['name']}! 👑

أنا المساعد الذكي، اسألني عن:
• المنتجات المتوفرة 🛍️
• الأسعار والعروض 💰
• عنوان المحل 📍
• مواعيد العمل 🕒
• التوصيل والشراء 🚚

كيف يمكنني خدمتك؟ 😊""",
                        'PRODUCTS': "🛍️ **الأقسام المتوفرة:**\n\n" + "\n".join([f"• {cat}" for cat in STORE_INFO['categories']]) + "\n\nأي قسم يهمك؟",
                        'PRICES': "💰 **نطاق الأسعار:**\n\n• ملابس: من 100 إلى 1200 جنيه\n• أحذية: من 200 إلى 600 جنيه\n• عطور: من 100 إلى 2000 جنيه\n\n🎁 خصم 20% على شراء قطعتين أو أكثر!",
                        'LOCATION': f"📍 **{STORE_INFO['name']}:**\n{STORE_INFO['address']}\n\n🕒 **مواعيد العمل:**\n{STORE_INFO['working_hours']['daily']}\n{STORE_INFO['working_hours']['weekend']}",
                        'CONTACT': "📞 **للتواصل:**\n" + "\n".join([f"• {phone}" for phone in STORE_INFO['phone_numbers']]) + "\n\n📱 الواتساب متوفر على جميع الأرقام"
                    }

                    response_text = postback_responses.get(payload, 
                        f"مرحباً! كيف يمكنني مساعدتك في {STORE_INFO['name']}؟")

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
        "store": STORE_INFO["name"],
        "facebook_integration": True,
        "verify_token_set": bool(FB_VERIFY_TOKEN),
        "page_token_set": bool(FB_PAGE_TOKEN),
        "webhook_url": "https://astramind-nine.vercel.app/webhook",
        "verify_token": FB_VERIFY_TOKEN,
        "store_contact": STORE_INFO["phone_numbers"],
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
                            "title": "🛍️ المنتجات",
                            "payload": "PRODUCTS"
                        },
                        {
                            "type": "postback",
                            "title": "💰 الأسعار",
                            "payload": "PRICES"
                        },
                        {
                            "type": "postback",
                            "title": f"📍 {STORE_INFO['name']}",
                            "payload": "LOCATION"
                        },
                        {
                            "type": "postback",
                            "title": "📞 اتصل بنا",
                            "payload": "CONTACT"
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
            "store": STORE_INFO["name"],
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
    print(f"👑 The King Store AI Assistant with Facebook Messenger")
    print(f"🔑 Verify Token: {FB_VERIFY_TOKEN}")
    print(f"🏪 Store: {STORE_INFO['name']}")
    print(f"📞 Phone: {', '.join(STORE_INFO['phone_numbers'])}")
    print(f"📍 Address: {STORE_INFO['address']}")
    print(f"🔗 Webhook URL: https://astramind-nine.vercel.app/webhook")
    print(f"📱 Test URL: https://astramind-nine.vercel.app/fb_test")
    app.run(host='0.0.0.0', port=port, debug=False)
