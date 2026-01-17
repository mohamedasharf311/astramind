"""
🤖 مساعد عيادة الأسنان - النسخة المستقرة
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
# في الأعلى بعد imports
from fb_webhook import fb
app.register_blueprint(fb)
app = Flask(__name__)
CORS(app)

# إضافة مسار api للمكاتب المخصصة
sys.path.append(os.path.dirname(__file__))

# محاولة استيراد المكونات الأساسية
try:
    # حاول استيراد QwenClient إذا كان موجوداً
    from qwen_client import QwenClient
    qwen_client = QwenClient()
    print("✅ QwenClient loaded successfully")
except ImportError:
    print("⚠️ QwenClient not found, using simple mode")
    qwen_client = None

try:
    # حاول استيراد قاعدة المعرفة
    from dental_kb import DentalKnowledgeBase
    knowledge_base = DentalKnowledgeBase()
    print("✅ Knowledge base loaded")
except ImportError:
    print("⚠️ Knowledge base not found, using basic data")
    # بيانات أساسية بديلة
    class SimpleKB:
        def get_context_for_question(self, question):
            return "معلومات العيادة: الهاتف 0123456789، العنوان: الرياض"
    knowledge_base = SimpleKB()

print("🚀 Dental AI Assistant is ready!")

@app.route('/')
def home():
    return jsonify({
        "service": "مساعد عيادة الأسنان",
        "status": "🟢 جاهز",
        "version": "1.0.0",
        "endpoints": {
            "/health": "GET - حالة النظام",
            "/ask": "POST - طرح الأسئلة",
            "/ask_get": "GET - طرح الأسئلة (بسيط)"
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "dental-ai",
        "qwen_available": qwen_client is not None
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' field"}), 400
        
        question = data['question'].strip()
        
        # توليد رد بسيط
        if qwen_client and hasattr(qwen_client, 'generate'):
            # استخدام Qwen إذا كان متاحاً
            context = knowledge_base.get_context_for_question(question)
            answer = qwen_client.generate(context, question)
        else:
            # رد بسيط
            answer = generate_simple_response(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "model": "Qwen2.5-7B" if qwen_client else "Simple"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "حدث خطأ، حاول مرة أخرى"
        }), 500

@app.route('/ask_get', methods=['GET'])
def ask_get():
    question = request.args.get('q', '').strip()
    
    if not question:
        return jsonify({"error": "Use ?q=سؤالك"}), 400
    
    # رد بسيط
    answer = generate_simple_response(question)
    
    return jsonify({
        "success": True,
        "question": question,
        "answer": answer
    })

def generate_simple_response(question):
    """رد بسيط مؤقت"""
    question_lower = question.lower()
    
    responses = {
        'greeting': "مرحباً! 👋 أنا مساعد عيادة الأسنان. كيف يمكنني مساعدتك؟",
        'appointment': "📅 للحجز: اتصل بنا على 0123456788 من الأحد للخميس 8 صباحاً - 8 مساءً",
        'price': "💰 الأسعار: الكشف 100 ريال، التنظيف 150 ريال، الحشو 200-350 ريال",
        'location': "📍 العنوان: شارع الملك فهد، الرياض. الهاتف: 0123456788",
        'hours': "🕒 الأوقات: الأحد-الخميس 8 ص - 8 م، الجمعة والسبت إجازة",
        'emergency': "🚨 للحالات الطارئة: اتصل على 0123456788 (24 ساعة)"
    }
    
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام']):
        return responses['greeting']
    elif any(word in question_lower for word in ['حجز', 'موعد']):
        return responses['appointment']
    elif any(word in question_lower for word in ['سعر', 'تكلفة', 'كم']):
        return responses['price']
    elif any(word in question_lower for word in ['عنوان', 'اين', 'مكان']):
        return responses['location']
    elif any(word in question_lower for word in ['وقت', 'دوام', 'متى']):
        return responses['hours']
    elif any(word in question_lower for word in ['طارئ', 'عاجل', 'ألم']):
        return responses['emergency']
    else:
        return "مرحباً! يمكنني مساعدتك في الحجز، الأسعار، العنوان، والأوقات. ماذا تريد أن تعرف؟"

# Facebook Webhook البسيط (اختياري)
@app.route('/webhook', methods=['GET'])
def fb_verify():
    token = request.args.get('hub.verify_token', '')
    challenge = request.args.get('hub.challenge', '')
    
    if token == 'astra_test_123':
        return challenge
    return 'Invalid token', 403

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
