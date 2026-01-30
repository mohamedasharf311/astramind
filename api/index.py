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
    "name": "The King 👑",
    "description": "محل سوتيس (ملابس جاهزة) - The King",
    "address": "وسط البلد - شارع طلعت حرب - بجانب سينما مترو",
    "phone_numbers": ["01553082672", "01017788206", "01159110136"],
    "whatsapp_numbers": ["01553082672", "01017788206"],
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
    "specialties": [
        "سوتيس بتصميمات إيطالية وتركية",
        "مقاسات مختلفة (سمول - 6XL)",
        "تعديلات مجانية في المحل",
        "خدمة توصيل سريعة",
        "أسعار تنافسية وجودة عالية"
    ]
}

# ===================== المساعد الأساسي =====================
@app.route('/')
def home():
    return jsonify({
        "service": "مساعد محل The King (سوتيس) الذكي 🤖",
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
        "service": "the-king-suits-messenger",
        "facebook_ready": bool(FB_PAGE_TOKEN),
        "store_name": STORE_INFO["name"],
        "store_type": "سوتيس جاهزة",
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
            "model": "The King Suits AI Assistant"
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
    """توليد رد ذكي - معدّل لمحل The King (سوتيس)"""
    question_lower = question.lower()

    # توليد ردود ذكية بناءً على السؤال
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام', 'صباح', 'مساء', 'بداية', 'هلا', 'اهلين']):
        return f"""مرحباً! 👋 أنا مساعد محل **{STORE_INFO['name']}** - متخصص في السوتيس الجاهزة 👔

🎉 كيف يمكنني خدمتك اليوم؟

يمكنك معرفة:
• أنواع السوتيس المتوفرة 🧥
• الأسعار والعروض الخاصة 💰
• المقاسات المتاحة 📏
• عنوان المحل 📍
• خدمة التوصيل 🚚
• مواعيد العمل 🕒

ماذا تحتاج؟ 😊"""

    elif any(word in question_lower for word in ['سوتيس', 'بدلة', 'جاكيت', 'كوت', 'كاستم', 'suit', 'suti', 'بدل', 'ترزي']):
        return f"""👔 **أنواع السوتيس المتوفرة في {STORE_INFO['name']}:**

{chr(10).join(['• ' + cat for cat in STORE_INFO['categories']])}

🎯 **تفاصيل السوتيس:**
1. **سوتيس كاملة (3 قطع):** جاكيت + بنطلون + سترة/قميص
2. **جواكيت منفردة:** بتصميمات إيطالية وتركية
3. **بناطيل رسمية:** ألوان مختلفة ومقاسات متنوعة
4. **قمصان رجالية:** قطن ومجلات عالية الجودة
5. **ربطات عنق:** موديلات كلاسيكية وعصرية

🌟 **المميزات:**
• جودة عالية وأنسجة ممتازة
• تصميمات حديثة وعصرية
• تناسب جميع المناسبات
• خدمة تعديل مجانية"""

    elif any(word in question_lower for word in ['سعر', 'ثمن', 'كم', 'تكلفة', 'غالي', 'رخيص', 'price', 'عرض', 'خصم']):
        return """💰 **أسعار السوتيس والعروض:**

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
• خصم 15% على الجواكيت المنفردة
• هدية رابطة عنق مع كل سوتيس
• خدمة تعديل مجانية للعملاء الجدد

💳 **طرق الدفع:**
• كاش
• بطاقات ائتمان
• تحويل بنكي
• أقساط (بفائدة رمزية)"""

    elif any(word in question_lower for word in ['مقاس', 'size', 'قاس', 'كبير', 'صغير', 'وسط', 'طول', 'عرض']):
        return """📏 **دليل المقاسات في The King:**

**مقاسات الجواكيت:**
• Small (S): 44-46
• Medium (M): 48-50
• Large (L): 52-54
• XL: 56-58
• XXL: 60-62
• 3XL: 64-66
• 4XL: 68-70
• 5XL: 72-74
• 6XL: 76-78 (متوفر)

**مقاسات البنطلون:**
• 28: محيط خصر 71 سم
• 30: محيط خصر 76 سم
• 32: محيط خصر 81 سم
• 34: محيط خصر 86 سم
• 36: محيط خصر 91 سم
• 38: محيط خصر 96 سم
• 40: محيط خصر 101 سم
• 42: محيط خصر 106 سم

**مقاسات القمصان:**
• 15: محيط رقبة 38 سم
• 15.5: محيط رقبة 39 سم
• 16: محيط رقبة 41 سم
• 16.5: محيط رقبة 42 سم
• 17: محيط رقبة 43 سم

✨ **خدماتنا:**
• قياس مجاني في المحل
• تعديلات مجانية حسب الطلب
• استشارة مجانية لاختيار المقاس المناسب"""

    elif any(word in question_lower for word in ['عنوان', 'مكان', 'الفرع', 'المحل', 'اين', 'موقع', 'address', 'location']):
        return f"""📍 **عنوان {STORE_INFO['name']}:**

{STORE_INFO['address']}

🗺️ **كيف تصل إلينا:**
• قريب جداً من محطة مترو وسط البلد
• بجوار سينما مترو الشهيرة
• أمام بنك مصر - فرع طلعت حرب

🚗 **مواقف سيارات:**
• موقف مجاني خاص بالعملاء أمام المحل
• مواقف عامة بجوار السينما

🚇 **بالمواصلات العامة:**
• مترو: محطة وسط البلد (5 دقائق سيراً)
• أتوبيس: موقف طلعت حرب
• ميكروباص: خطوط متجهة لوسط البلد

🕒 **مواعيد العمل:**
يومياً: {STORE_INFO['working_hours']['daily']}
الجمعة والسبت: {STORE_INFO['working_hours']['weekend']}"""

    elif any(word in question_lower for word in ['تليفون', 'هاتف', 'اتصل', 'رقم', 'contact', 'ارقام', 'كلم', 'واتساب', 'whatsapp']):
        phones_formatted = chr(10).join([f"• 📞 {phone}" for phone in STORE_INFO['phone_numbers']])
        whatsapp_formatted = chr(10).join([f"• 📱 واتساب: {phone}" for phone in STORE_INFO['whatsapp_numbers']])
        return f"""📞 **ارقام تواصل {STORE_INFO['name']}:**

{phones_formatted}

{whatsapp_formatted}

📧 **البريد الإلكتروني:** info@thekingstore.com
📱 **تليجرام:** @thekingstore
📍 **العنوان:** {STORE_INFO['address']}

⏰ **أوقات الرد على المكالمات:**
يومياً من 10 صباحاً حتى 12 مساءً
نرد على الاستفسارات خلال 10 دقائق

💬 **عبر الواتساب:**
• أرسل صورة السوتيس المطلوب
• أرسل مقاسك للاستشارة
• احصل على عرض سعر فوري"""

    elif any(word in question_lower for word in ['مواعيد', 'يفتح', 'يغلق', 'متاح', 'اوقات', 'open', 'close', 'time']):
        return f"""🕒 **مواعيد عمل {STORE_INFO['name']}:**

⏰ **يومياً (الأحد - الخميس):**
{STORE_INFO['working_hours']['daily']}

🎉 **الجمعة والسبت والعطلات الرسمية:**
{STORE_INFO['working_hours']['weekend']}

✨ **أوقات الذروة (ننصح بتجنبها):**
• 7:00 مساءً - 10:00 مساءً (منتصف الأسبوع)
• 9:00 مساءً - 1:00 صباحاً (نهاية الأسبوع)

🎩 **أفضل أوقات للزيارة:**
• 10:00 صباحاً - 12:00 ظهراً
• 3:00 عصراً - 5:00 مساءً

💡 *نوفر خدمة حجز مواعيد مسبقة لتجربة تسوق أفضل*"""

    elif any(word in question_lower for word in ['شراء', 'اطلب', 'طلب', 'اوردر', 'عايز', 'أريد', 'اشتري', 'order', 'buy']):
        return """🛒 **طريقة الشراء من The King:**

**الشراء من المحل:**
1. تفضل بزيارتنا في العنوان المذكور
2. اختبر جودة الأقمشة والتصميمات
3. قم بتجربة السوتيس المناسب لك
4. اختر المقاس واللون المفضل
5. استمتع بخدمة التعديل المجانية
6. الدفع نقداً أو ببطاقة الائتمان

**الشراء أونلاين (عن بعد):**
1. اختر السوتيس المناسب من الكتالوج
2. أرسل لنا صورة السوتيس على الواتساب
3. حدد المقاس واللون المطلوب
4. أرسل مقاساتك للتحقق من المناسبة
5. نحدد السعر النهائي والتكلفة
6. نأكد الطلب ونحدد موعد التوصيل

**خدمات مجانية مع الشراء:**
• تعديلات مجانية في المحل
• كي وتنظيف أولي
• تخزين السوتيس في المحل (اختياري)
• استشارة أزياء مجانية"""

    elif any(word in question_lower for word in ['توصيل', 'شحن', 'delivery', 'ship', 'وصل', 'ميعاد']):
        return """🚚 **خدمة التوصيل من The King:**

**نطاق التوصيل:**
• القاهرة: جميع الأحياء والمناطق
• الجيزة: المناطق الرئيسية
• القليوبية: بعض المناطق المحددة

**تكلفة التوصيل:**
• مجاني للطلبات فوق 1500 جنيه داخل القاهرة
• 50 جنيه للطلبات من 1000-1500 جنيه
• 80 جنيه للطلبات أقل من 1000 جنيه

**مدة التوصيل:**
• داخل القاهرة: 24-48 ساعة
• خارج القاهرة: 2-5 أيام عمل

**خطوات التوصيل:**
1. تأكيد الطلب والدفع المسبق (50%)
2. تجهيز السوتيس والتعديلات اللازمة
3. تغليف خاص للحفاظ على الجودة
4. إرسال رقم تتبع الشحنة
5. التوصيل للمنزل والتجربة
6. الدفع المتبقي واستلام المنتج

**ضماناتنا:**
• يمكنك تجربة السوتيس قبل الدفع النهائي
• إرجاع واستبدال مجاني خلال 7 أيام
• صيانة مجانية لمدة 3 أشهر"""

    elif any(word in question_lower for word in ['جودة', 'نوعية', 'quality', 'اقمشة', 'مصنع', 'ماركة', 'brand', 'خامة']):
        return """🏆 **جودة سوتيس The King:**

**الأقمشة المستخدمة:**
• صوف مصري عالي الجودة
• كشمير مستورد من إيطاليا
• قطن مصري 100%
• أقمشة تركية مقاومة للتجاعيد

**التصميمات:**
• تصميمات كلاسيكية وعصرية
• ألوان تناسب جميع الأذواق
• تفصيل دقيق وأناقة في التصميم
• تناسب جميع المناسبات (عمل - حفلات - زفاف)

**المميزات الفنية:**
• طبقات مزدوجة في الأكتاف
• أزرار مصنوعة من العظم الطبيعي
• بطانة داخلية من الحرير الصناعي
• جيوب داخلية وخارجية عملية

**ضمان الجودة:**
• جميع المنتجات أصلية 100%
• فحص الجودة قبل البيع
• ضمان ضد عيوب الصنعة لمدة 6 أشهر
• خدمة ما بعد البيع وصيانة دورية"""

    elif any(word in question_lower for word in ['مناسبة', 'فرح', 'خطوبة', 'عمل', 'مقابلة', 'حفلة', 'زفاف', 'مناسبات']):
        return """🎭 **سوتيس لكل المناسبات:**

**للأعمال والمقابلات:**
• ألوان كلاسيكية (أسود، رمادي، كحلي)
• تصميمات محافظة وأنيقة
• أقمشة عملية ومرنة

**للحفلات والزفاف:**
• ألوان فاتحة وجريئة
• تصميمات عصرية ومتميزة
• تفاصيل راقية وزينة خاصة

**للخطوبة والمناسبات الخاصة:**
• سوتيس مطرزة بخيوط ذهبية
• تصميمات فريدة وحصرية
• ألوان تناسب فصل الصيف والشتاء

**نصائح اختيار السوتيس:**
• للرسميات: ألوان داكنة، قماش ثقيل
• للصيف: ألوان فاتحة، قماش خفيف
• للشتاء: ألوان دافئة، صوف أو كشمير
• للحفلات: تصميمات مميزة، تفاصيل خاصة"""

    elif any(word in question_lower for word in ['عروض', 'تخفيضات', 'خصومات', 'عرض', 'تخفيض', 'خصم', 'سعر خاص']):
        return """🎯 **العروض الحالية في The King:**

🔥 **عرض الموسم:**
• خصم 25% على جميع السوتيس الكاملة
• شراء 2 سوتيس تحصل على الثالث هدية

🎩 **عروض المناسبات:**
• خصم 30% على سوتيس الزفاف
• تخفيض 20% على السوتيس الرسمية للعمل

🎓 **عروض الخريجين:**
• سوتيس كاملة + قميص + رابطة عنق = 1500 جنيه فقط
• خصم 15% لطلبة الجامعات

👨‍👨‍👦 **عروض العائلة:**
• خصم إضافي 10% للعائلة (3 أشخاص فأكثر)
• هدايا مجانية مع كل عملية شراء عائلية

💝 **عرض الولاء:**
• كرت عملاء دائم: خصم 5% على كل عملية شراء
• تجميع نقاط: كل 1000 جنيه = 100 نقطة = خصم 50 جنيه

📅 **العروض سارية حتى نهاية الشهر!**"""

    elif any(word in question_lower for word in ['شكرا', 'ممتاز', 'حلو', 'تمام', 'thanks', 'thank', 'جزاك']):
        return f"""🙏 **شكراً لثقتك في {STORE_INFO['name']}!** 👑

يسعدنا خدمتك دائماً ونتمنى أن نراك قريباً في محلتنا.

🎁 **نصيحة:**
• احتفظ برقم تليفوننا للاستفسارات المستقبلية
• تابعنا على وسائل التواصل الاجتماعي للعروض الجديدة
• شاركنا تجربتك وتقييمك، فهو يهمنا كثيراً

✨ **وعدنا لك:**
• جودة لا تضاهى
• أسعار تنافسية
• خدمة عملاء ممتازة
• تجربة تسوق فريدة

نتمنى لك يوماً سعيداً وأنيقاً! 😊"""

    else:
        return f"""👑 **مرحباً في {STORE_INFO['name']}!** - متخصصون في السوتيس الجاهزة 👔

أنا المساعد الذكي للمحل، يمكنني مساعدتك في:

🧥 **معرفة أنواع السوتيس والمقاسات**
💰 **الأسعار والعروض الحالية**
📏 **دليل المقاسات والاستشارة**
📍 **عنوان المحل ومواعيد العمل**
📞 **أرقام التواصل والاستفسارات**
🚚 **خدمة التوصيل وطرق الشراء**
🎭 **اختيار السوتيس المناسب لكل مناسبة**

💬 **مثال على الأسئلة:**
• "عايز سوتيس لفرح"
• "عندكم مقاس كبير؟"
• "سعر السوتيس الكامل"
• "عنوان المحل إزاي"
• "عايز أطلب أونلاين"

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

أنا المساعد الذكي لمحل السوتيس الجاهزة، اسألني عن:
• أنواع السوتيس المتوفرة 🧥
• الأسعار والعروض الخاصة 💰
• المقاسات (حتى 6XL) 📏
• عنوان المحل 📍
• خدمة التوصيل 🚚
• مواعيد العمل 🕒

كيف يمكنني خدمتك؟ 😊""",
                        'PRODUCTS': "👔 **أنواع السوتيس:**\n\n" + "\n".join([f"• {cat}" for cat in STORE_INFO['categories']]) + "\n\nأي نوع يهمك؟",
                        'PRICES': "💰 **نطاق الأسعار:**\n\n• سوتيس كاملة: 800-4000 جنيه\n• جواكيت: 500-1500 جنيه\n• بناطيل: 200-500 جنيه\n• قمصان: 150-350 جنيه\n\n🎁 خصم 20% على السوتيس الكاملة!",
                        'SIZES': "📏 **المقاسات المتاحة:**\n\n• جواكيت: من S إلى 6XL\n• بنطلون: من 28 إلى 42\n• قمصان: من 15 إلى 17\n\n✨ خدمة تعديل مجانية!",
                        'LOCATION': f"📍 **{STORE_INFO['name']}:**\n{STORE_INFO['address']}\n\n🕒 **مواعيد العمل:**\n{STORE_INFO['working_hours']['daily']}\n{STORE_INFO['working_hours']['weekend']}",
                        'CONTACT': "📞 **للتواصل:**\n" + "\n".join([f"• {phone}" for phone in STORE_INFO['phone_numbers']]) + "\n\n📱 **واتساب:**\n" + "\n".join([f"• {phone}" for phone in STORE_INFO['whatsapp_numbers']]),
                        'DELIVERY': "🚚 **التوصيل:**\n\n• مجاني للطلبات فوق 1500 جنيه\n• داخل القاهرة: 24-48 ساعة\n• يمكنك التجربة قبل الدفع النهائي"
                    }

                    response_text = postback_responses.get(payload, 
                        f"مرحباً! كيف يمكنني مساعدتك في اختيار السوتيس المناسب من {STORE_INFO['name']}؟")

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
        "store_type": STORE_INFO["description"],
        "facebook_integration": True,
        "verify_token_set": bool(FB_VERIFY_TOKEN),
        "page_token_set": bool(FB_PAGE_TOKEN),
        "webhook_url": "https://astramind-nine.vercel.app/webhook",
        "verify_token": FB_VERIFY_TOKEN,
        "store_contact": STORE_INFO["phone_numbers"],
        "whatsapp_numbers": STORE_INFO["whatsapp_numbers"],
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
                            "title": "👔 السوتيس",
                            "payload": "PRODUCTS"
                        },
                        {
                            "type": "postback",
                            "title": "💰 الأسعار",
                            "payload": "PRICES"
                        },
                        {
                            "type": "postback",
                            "title": "📏 المقاسات",
                            "payload": "SIZES"
                        },
                        {
                            "type": "web_url",
                            "title": "📍 العنوان",
                            "url": f"https://www.google.com/maps/search/{STORE_INFO['address'].replace(' ', '+')}",
                            "webview_height_ratio": "full"
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
            "store_description": STORE_INFO["description"],
            "message": "Facebook page setup completed for The King Suits Store!",
            "next_steps": [
                f"1. Open: https://astramind-nine.vercel.app/fb_test",
                "2. Copy the Verify Token",
                "3. Go to Facebook Developers → Webhook",
                "4. Add the Webhook URL and Verify Token",
                "5. Subscribe your page to events",
                "6. Send a message to your Facebook page!",
                "7. Share: https://m.me/YourPageUsername"
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
    print(f"👑 The King Suits Store AI Assistant with Facebook Messenger")
    print(f"🎯 Specialization: {STORE_INFO['description']}")
    print(f"🔑 Verify Token: {FB_VERIFY_TOKEN}")
    print(f"🏪 Store: {STORE_INFO['name']}")
    print(f"📍 Address: {STORE_INFO['address']}")
    print(f"📞 Phone: {', '.join(STORE_INFO['phone_numbers'])}")
    print(f"📱 WhatsApp: {', '.join(STORE_INFO['whatsapp_numbers'])}")
    print(f"🔗 Webhook URL: https://astramind-nine.vercel.app/webhook")
    print(f"📱 Test URL: https://astramind-nine.vercel.app/fb_test")
    app.run(host='0.0.0.0', port=port, debug=False)
