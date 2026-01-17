from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys

app = Flask(__name__)
CORS(app)

# ⚠️ علّق هذا السطر مؤقتاً أو احذفه:
# from fb_webhook import fb  # ⬅️ هذا ما يسبب الخطأ

print("🚀 Starting Dental AI Assistant...")

@app.route('/')
def home():
    return jsonify({
        "service": "مساعد عيادة الأسنان الذكي 🤖",
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
        "service": "dental-ai-assistant",
        "timestamp": "2024-01-17"
    })

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({"error": "يرجى إرسال سؤال في حقل 'question'"}), 400
        
        question = data['question'].strip()
        
        # رد بسيط
        answer = generate_response(question)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer
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
    """توليد رد بسيط"""
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام']):
        return "مرحباً! 👋 أنا مساعد عيادة الأسنان. كيف يمكنني مساعدتك؟"
    
    elif any(word in question_lower for word in ['حجز', 'موعد']):
        return "📅 للحجز: اتصل بنا على 0123456789 من الأحد إلى الخميس 8 صباحاً - 8 مساءً"
    
    elif any(word in question_lower for word in ['سعر', 'تكلفة', 'كم']):
        return "💰 الأسعار: الكشف 100 ريال، التنظيف 150 ريال، الحشو 200-350 ريال"
    
    elif any(word in question_lower for word in ['عنوان', 'اين', 'مكان']):
        return "📍 العيادة: شارع الملك فهد، الرياض. الهاتف: 0123456789"
    
    elif any(word in question_lower for word in ['وقت', 'دوام', 'متى']):
        return "🕒 الأوقات: الأحد-الخميس 8 ص - 8 م، الجمعة والسبت إجازة"
    
    elif any(word in question_lower for word in ['طارئ', 'عاجل', 'ألم']):
        return "🚨 للحالات الطارئة: اتصل على 0123456789 (24 ساعة)"
    
    else:
        return "مرحباً! يمكنني مساعدتك في الحجز، الأسعار، العنوان، الأوقات، والحالات الطارئة. ماذا تريد أن تعرف؟"

# Facebook Webhook بسيط داخل نفس الملف
@app.route('/webhook', methods=['GET'])
def fb_webhook_verify():
    """تحقق من فيسبوك Webhook"""
    verify_token = request.args.get('hub.verify_token', '')
    challenge = request.args.get('hub.challenge', '')
    
    # هذا التوكن ستضعه في Facebook Developers
    expected_token = "astra_dental_bot_2024"
    
    if verify_token == expected_token:
        print("✅ Facebook webhook verified")
        return challenge
    
    return 'Invalid verification token', 403

@app.route('/webhook', methods=['POST'])
def fb_webhook_receive():
    """استقبال رسائل فيسبوك"""
    try:
        data = request.get_json()
        
        # رد بسيط لاختبار
        return jsonify({
            "status": "received",
            "message": "Facebook webhook is working!",
            "next_step": "Connect to Facebook Developers"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 Server running on port {port}")
    app.run(host='0.0.0.0', port=port)
