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
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "the_king_store_bot_2024")
FB_PAGE_TOKEN = os.environ.get("FB_PAGE_TOKEN", "EAAKqctOyqecBQRvAeGXRkb11K2AzRMelttUC2zVL7FdS7VFAVhVT1anKKV9ACkfZCXr2UzpAaILw6rN65BUqmDjaZC0tM81wiOtQ5ZCZBtHMwe0qm678azp1PC6bXxsYYOHfLLZCJS5ShMKsgRZAxjbk6ZAT8uS275lWrYP7s3ST6faoseYCwMzmxsZBeDOZBplnn3ZAa6ygZDZD")
FB_APP_SECRET = os.environ.get("FB_APP_SECRET", "")

# ===================== المعلومات الأساسية للمحل =====================
STORE_INFO = {
    "name": "x 👑",
    "description": "محل سوتيس (ملابس جاهزة) - The x",
    "address": "وسط البلد - شارع طلعت حرب - بجانب سينما مترو",
    "phone_numbers": ["x", "x", "x"],
    "whatsapp_numbers": ["x", "x"],
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

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد محل x (سوتيس) الذكي 🤖",
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
        "store": STORE_INFO["name"]
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({"error": "يرجى إرسال سؤال"}), 400
            
        answer = generate_response(question)
        
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
        
    answer = generate_response(question)
    
    return jsonify({
        "success": True,
        "question": question,
        "answer": answer
    })

def generate_response(question):
    """توليد رد ذكي مع تحسين حساسية الكلمات"""
    question_lower = question.lower().strip()
    
    # ============ تحسين البحث عن الكلمات ============
    
    # 1. البحث عن العنوان/المكان (كلمات أكثر حساسية)
    address_keywords = [
        'عنوان', 'مكان', 'الفرع', 'المحل', 'اين', 'موقع', 'address', 'location',
        'وين', 'فين', 'مكانك', 'عنوانك', 'المكان', 'العنوان', 'الموقع', 'الفرع',
        'أقدر أجيلك', 'جاي', 'زيارة', 'توجيه', 'الخرائط', 'خريطة', 'map', 'maps'
    ]
    
    if any(keyword in question_lower for keyword in address_keywords):
        return f"""📍 **عنوان {STORE_INFO['name']}:**

{STORE_INFO['address']}

🗺️ **كيف تصل إلينا:**
• قريب جداً من محطة مترو وسط البلد
• بجوار سينما مترو الشهيرة
• أمام بنك مصر - فرع طلعت حرب

🚗 **مواقف سيارات:**
• موقف مجاني خاص بالعملاء أمام المحل

🕒 **مواعيد العمل:**
يومياً: {STORE_INFO['working_hours']['daily']}
الجمعة والسبت: {STORE_INFO['working_hours']['weekend']}"""

    # 2. البحث عن التواصل/التليفونات (كلمات أكثر حساسية)
    contact_keywords = [
        'تليفون', 'هاتف', 'اتصل', 'رقم', 'contact', 'ارقام', 'كلم', 'واتساب',
        'whatsapp', 'اتصال', 'تواصل', 'الرقم', 'الهاتف', 'التليفون', 'التواصل',
        'رقمك', 'تليفونك', 'اتصالك', 'تواصلك', 'الواتساب', 'اتصل بيك', 'اتواصل',
        'عايز رقم', 'عاوز رقم', 'بدي رقم', 'أريد رقم', 'أحتاج رقم', 'نمرة', 'نمبر'
    ]
    
    if any(keyword in question_lower for keyword in contact_keywords):
        phones_formatted = "\n".join([f"• 📞 {phone}" for phone in STORE_INFO['phone_numbers']])
        whatsapp_formatted = "\n".join([f"• 📱 واتساب: {phone}" for phone in STORE_INFO['whatsapp_numbers']])
        
        return f"""📞 **ارقام تواصل {STORE_INFO['name']}:**

{phones_formatted}

{whatsapp_formatted}

📧 **البريد الإلكتروني:** info@thekingstore.com
📍 **العنوان:** {STORE_INFO['address']}

⏰ **أوقات الرد على المكالمات:**
يومياً من 10 صباحاً حتى 12 مساءً"""

    # 3. البحث عن الأسعار (كلمات أكثر حساسية)
    price_keywords = [
        'سعر', 'ثمن', 'كم', 'تكلفة', 'غالي', 'رخيص', 'price', 'عرض', 'خصم',
        'السعر', 'الثمن', 'التكلفة', 'بكام', 'بكام', 'تكام', 'تكلف', 'تكلفته',
        'اسعار', 'الاسعار', 'الأسعار', 'اسعاركم', 'أسعاركم', 'بكام السوتيس',
        'سعر السوتيس', 'ثمن البدلة', 'كم السعر', 'كم التكلفة', 'الأسعار كام',
        'سعر الجاكيت', 'سعر الكوت', 'سعر البدلة', 'الأسعار عامة', 'عايز اعرف السعر'
    ]
    
    if any(keyword in question_lower for keyword in price_keywords):
        return """💰 **أسعار السوتيس في The King 👑:**

👔 **سوتيس كاملة (3 قطع):**
• اقتصادية: 800 - 1200 جنيه  
• متوسطة: 1200 - 1800 جنيه  
• فاخرة: 1800 - 2500 جنيه  
• VIP: 2500 - 4000 جنيه

🧥 **جواكيت منفردة:**
• من 500 إلى 1500 جنيه

👖 **بناطيل رسمية:**
• من 200 إلى 500 جنيه

👕 **قمصان:**
• من 150 إلى 350 جنيه

🎀 **إكسسوارات:**
• ربطات عنق: 50 - 150 جنيه
• أحزمة جلد: 100 - 250 جنيه

🎁 **عروض خاصة:**
• خصم 20% على شراء سوتيس كاملة
• هدية رابطة عنق مع كل سوتيس
• خدمة تعديل مجانية"""

    # 4. البحث عن المنتجات/السوتيس
    product_keywords = [
        'سوتيس', 'بدلة', 'جاكيت', 'كوت', 'كاستم', 'suit', 'suti', 'بدل', 'ترزي',
        'ملابس', 'ملبس', 'ازياء', 'أزياء', 'بدل رجالي', 'سوت رجالي', 'جواكيت',
        'كوتش', 'كوتشة', 'بدلة رسمية', 'سوتيس رسمي', 'سوت عمل', 'سوت فرح',
        'عايز سوتيس', 'عاوز بدلة', 'بدي سوت', 'أريد بدلة', 'أحتاج جاكيت',
        'عندكم سوتيس', 'فيكم سوتيس', 'السوتيس', 'البدلة', 'الجواكيت'
    ]
    
    if any(keyword in question_lower for keyword in product_keywords):
        return f"""👔 **أنواع السوتيس المتوفرة في {STORE_INFO['name']}:**

{chr(10).join(['• ' + cat for cat in STORE_INFO['categories']])}

🎯 **تفاصيل السوتيس:**
1. **سوتيس كاملة (3 قطع):** جاكيت + بنطلون + سترة/قميص
2. **جواكيت منفردة:** بتصميمات إيطالية وتركية
3. **بناطيل رسمية:** ألوان مختلفة ومقاسات متنوعة
4. **قمصان رجالية:** قطن ومجلات عالية الجودة

🌟 **المميزات:**
• جودة عالية وأنسجة ممتازة
• تصميمات حديثة وعصرية
• تناسب جميع المناسبات
• خدمة تعديل مجانية"""

    # 5. البحث عن المواعيد
    hours_keywords = [
        'مواعيد', 'يفتح', 'يغلق', 'متاح', 'اوقات', 'open', 'close', 'time',
        'المواعيد', 'الأوقات', 'مواعيدكم', 'أوقاتكم', 'بتفتح امتى', 'بتقفل امتى',
        'يفتح الساعة', 'يغلق الساعة', 'مفتوح', 'مقفول', 'العمل', 'دوام',
        'ساعات العمل', 'ساعة الفتح', 'ساعة الإغلاق', 'عايز اجي', 'متى اقدر اجي',
        'يوم كام', 'من كام لكام', 'اوقات الدوام', 'اوقات العمل'
    ]
    
    if any(keyword in question_lower for keyword in hours_keywords):
        return f"""🕒 **مواعيد عمل {STORE_INFO['name']}:**

⏰ **يومياً (الأحد - الخميس):**
{STORE_INFO['working_hours']['daily']}

🎉 **الجمعة والسبت والعطلات الرسمية:**
{STORE_INFO['working_hours']['weekend']}

✨ **أفضل أوقات للزيارة:**
• 10:00 صباحاً - 12:00 ظهراً
• 3:00 عصراً - 5:00 مساءً

💡 *نوفر خدمة حجز مواعيد مسبقة لتجربة تسوق أفضل*"""

    # 6. البحث عن المقاسات
    size_keywords = [
        'مقاس', 'size', 'قاس', 'كبير', 'صغير', 'وسط', 'طول', 'عرض',
        'المقاس', 'السايز', 'المقاسات', 'المقاسات', 'عندكم مقاس كبير',
        'عندكم مقاس صغير', 'مقاساتكم', 'السايزات', 'عندكم 6xl',
        'مقاس ٤٨', 'مقاس ٥٠', 'مقاس ٥٢', 'عايز مقاس كبير', 'بدي مقاس',
        'أحتاج مقاس', 'مقاسات السوتيس', 'مقاس البدلة', 'مقاس الجاكيت'
    ]
    
    if any(keyword in question_lower for keyword in size_keywords):
        return """📏 **المقاسات المتاحة:**

• جواكيت: من Small (S) إلى 6XL
• بنطلون: من 28 إلى 42
• قمصان: من 15 إلى 17

✨ **خدماتنا:**
• قياس مجاني في المحل
• تعديلات مجانية حسب الطلب
• استشارة مجانية لاختيار المقاس المناسب"""

    # 7. البحث عن التوصيل
    delivery_keywords = [
        'توصيل', 'شحن', 'delivery', 'ship', 'وصل', 'ميعاد',
        'التوصيل', 'الشحن', 'التوصيلات', 'الشحنات', 'عايز اطلب اونلاين',
        'عاوز اطلب اونلاين', 'بدي اطلب اونلاين', 'التوصيل للمنزل',
        'بيوصلو لبلك', 'بيوصلك', 'بيوصل', 'يوصل', 'شحنة', 'شحنات',
        'طلب اونلاين', 'الطلب اونلاين', 'الاوردر', 'الأوردر'
    ]
    
    if any(keyword in question_lower for keyword in delivery_keywords):
        return """🚚 **خدمة التوصيل:**

• مجاني للطلبات فوق 1500 جنيه داخل القاهرة
• داخل القاهرة: 24-48 ساعة
• يمكنك التجربة قبل الدفع النهائي
• إرجاع واستبدال مجاني خلال 7 أيام"""

    # 8. التحية
    greeting_keywords = [
        'مرحبا', 'اهلا', 'السلام', 'صباح', 'مساء', 'مساكم', 'صباحك',
        'hello', 'hi', 'hey', 'السلام عليكم', 'وعليكم السلام',
        'مرحب', 'أهلاً', 'أهلين', 'مرحبتين', 'هاي', 'هلا', 'هلو',
        'صباح الخير', 'مساء الخير', 'مساء النور'
    ]
    
    if any(keyword in question_lower for keyword in greeting_keywords):
        return f"""مرحباً! 👋 أنا مساعد محل **{STORE_INFO['name']}** - متخصص في السوتيس الجاهزة 👔

🎉 كيف يمكنني خدمتك اليوم؟

يمكنني مساعدتك في:
• أنواع السوتيس والأسعار 🧥
• العنوان ومواعيد العمل 📍
• أرقام التواصل 📞
• خدمة التوصيل 🚚
• المقاسات المتاحة 📏

ماذا تحتاج؟ 😊"""

    # 9. الشكر
    thanks_keywords = [
        'شكرا', 'ممتاز', 'حلو', 'تمام', 'thanks', 'thank', 'جزاك',
        'شكراً', 'متشكر', 'تسلم', 'تسلمي', 'تسلم ايدك', 'مشكور',
        'الله يخليك', 'يعطيك العافية', 'بارك الله فيك', 'ألف شكر'
    ]
    
    if any(keyword in question_lower for keyword in thanks_keywords):
        return f"""🙏 **شكراً لثقتك في {STORE_INFO['name']}!** 👑

يسعدنا خدمتك دائماً ونتمنى أن نراك قريباً في محلتنا.

🎁 **نصيحة:**
• احتفظ برقم تليفوننا للاستفسارات المستقبلية
• تابعنا على وسائل التواصل الاجتماعي للعروض الجديدة

نتمنى لك يوماً سعيداً وأنيقاً! 😊"""

    # 10. الرد الافتراضي
    return f"""👑 **مرحباً في {STORE_INFO['name']}!** - متخصصون في السوتيس الجاهزة 👔

أنا المساعد الذكي للمحل، يمكنني مساعدتك في:

• **العنوان:** {STORE_INFO['address']}
• **التليفونات:** {', '.join(STORE_INFO['phone_numbers'])}
• **الأسعار:** سوتيس كاملة من 800 إلى 4000 جنيه
• **المقاسات:** من Small إلى 6XL
• **المواعيد:** {STORE_INFO['working_hours']['daily']}

💬 **مثال على الأسئلة:**
• "عندكم مقاس كبير؟"
• "سعر السوتيس الكامل"
• "عنوان المحل إزاي"
• "عايز أطلب أونلاين"

ماذا تحتاج مني اليوم؟ 😊"""

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

                # رسالة نصية من مستخدم
                if messaging_event.get('message'):
                    sender_id = messaging_event['sender']['id']
                    message_text = messaging_event['message'].get('text', '')

                    if message_text:
                        print(f"📱 Facebook message from {sender_id}: {message_text}")

                        response_text = generate_response(message_text)

                        send_facebook_message(sender_id, response_text)

                # ضغط على زر
                elif messaging_event.get('postback'):
                    sender_id = messaging_event['sender']['id']
                    payload = messaging_event['postback']['payload']

                    print(f"📱 Facebook postback from {sender_id}: {payload}")

                    postback_responses = {
                        'GET_STARTED': f"مرحباً بك في {STORE_INFO['name']}! 👑\n\nكيف يمكنني خدمتك اليوم؟",
                        'PRODUCTS': "👔 **أنواع السوتيس:**\n\n" + "\n".join([f"• {cat}" for cat in STORE_INFO['categories']]),
                        'PRICES': "💰 **أسعار السوتيس:**\n\n• سوتيس كاملة: 800-4000 جنيه\n• خصم 20% على السوتيس الكاملة!",
                        'LOCATION': f"📍 **العنوان:**\n{STORE_INFO['address']}",
                        'CONTACT': "📞 **التليفونات:**\n" + "\n".join([f"• {phone}" for phone in STORE_INFO['phone_numbers']]),
                        'HOURS': f"🕒 **مواعيد العمل:**\n{STORE_INFO['working_hours']['daily']}"
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
    if not FB_PAGE_TOKEN:
        print("⚠️ FB_PAGE_TOKEN not set.")
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
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print(f"✅ Message sent to {recipient_id}")
            return True
        else:
            print(f"❌ Failed to send message: {response.status_code}")
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
        "webhook_url": "https://astramind-nine.vercel.app/webhook",
        "verify_token": FB_VERIFY_TOKEN,
        "test_endpoints": {
            "address_test": "https://astramind-nine.vercel.app/ask_get?q=العنوان",
            "contact_test": "https://astramind-nine.vercel.app/ask_get?q=التواصل",
            "price_test": "https://astramind-nine.vercel.app/ask_get?q=الاسعار"
        }
    })

# ===================== تشغيل التطبيق =====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server running on port {port}")
    print(f"👑 Store: {STORE_INFO['name']}")
    print(f"📍 Address: {STORE_INFO['address']}")
    print(f"📞 Phones: {', '.join(STORE_INFO['phone_numbers'])}")
    print(f"🔗 Webhook: https://astramind-nine.vercel.app/webhook")
    print(f"🔐 Verify Token: {FB_VERIFY_TOKEN}")
    app.run(host='0.0.0.0', port=port, debug=False)
