"""
🏥 مساعد عيادة الأسنان مع Qwen2.5-7B
الإصدار الخفيف الذي يعمل على Vercel
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from datetime import datetime

# إضافة المسار
sys.path.append(os.path.dirname(__file__))

app = Flask(__name__)
CORS(app)

# استيراد المكونات
try:
    from qwen_client import QwenClient
    from dental_kb import DentalKnowledgeBase
    print("✅ تم تحميل المكونات بنجاح")
except ImportError as e:
    print(f"⚠️ خطأ في استيراد المكونات: {e}")
    # نسخ احتياطية
    class QwenClient:
        def generate(self, context, question):
            return f"مرحباً! أنا مساعد العيادة. سؤالك: {question}"
    
    class DentalKnowledgeBase:
        def get_context_for_question(self, question):
            return "معلومات العيادة: الهاتف 0112345678"

# تهيئة المكونات
qwen_client = QwenClient()
knowledge_base = DentalKnowledgeBase()

print("🚀 مساعد عيادة الأسنان مع Qwen2.5-7B جاهز!")

@app.route('/')
def home():
    """الصفحة الرئيسية"""
    return jsonify({
        "service": "مساعد عيادة الأسنان الذكي 🤖",
        "version": "2.5.0",
        "model": "Qwen2.5-7B-Instruct (عبر API)",
        "status": "🟢 جاهز",
        "features": [
            "ردود ذكية باستخدام Qwen2.5-7B",
            "معرفة كاملة بالعيادة",
            "لا حاجة لتحميل النموذج محلياً",
            "مجاني 100%",
            "يدعم جميع استفسارات المرضى"
        ],
        "endpoints": {
            "/ask": "POST - طرح الأسئلة (مفضل)",
            "/ask_get": "GET - طرح الأسئلة (بسيط)",
            "/health": "GET - حالة النظام",
            "/test": "GET - اختبار النظام",
            "/info": "GET - معلومات عن العيادة"
        },
        "example_post": 'curl -X POST https://your-app.vercel.app/ask -H "Content-Type: application/json" -d \'{"question": "كيف أحجز موعد؟"}\'',
        "example_get": 'curl "https://your-app.vercel.app/ask_get?q=كم سعر تنظيف الأسنان؟"'
    })

@app.route('/health', methods=['GET'])
def health():
    """فحص حالة النظام"""
    return jsonify({
        "status": "healthy",
        "service": "dental-ai-qwen",
        "model": "Qwen2.5-7B-Instruct",
        "api_mode": "external",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/ask', methods=['POST'])
def ask_question():
    """طرح سؤال ذكي"""
    
    try:
        # الحصول على البيانات
        data = request.get_json()
        
        if not data or 'question' not in data:
            return jsonify({
                "success": False,
                "error": "يرجى إرسال سؤال في حقل 'question'",
                "example": '{"question": "كيف أحجز موعد؟"}'
            }), 400
        
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                "success": False,
                "error": "السؤال فارغ"
            }), 400
        
        print(f"📥 سؤال: {question}")
        
        # 1. الحصول على السياق من قاعدة المعرفة
        context = knowledge_base.get_context_for_question(question)
        
        # 2. البحث عن معلومات محددة
        search_results = knowledge_base.search(question)
        if search_results:
            context += "\n\nمعلومات إضافية:\n" + "\n".join(search_results)
        
        # 3. توليد الرد باستخدام Qwen
        print("🧠 جارٍ توليد الرد باستخدام Qwen2.5...")
        start_time = datetime.now()
        
        answer = qwen_client.generate(context, question)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        print(f"✅ تم الرد في {processing_time:.2f} ثانية")
        
        # 4. إرجاع النتيجة
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "context_length": len(context),
            "processing_time": round(processing_time, 2),
            "model": "Qwen2.5-7B-Instruct",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "حدث خطأ في المعالجة. يرجى المحاولة مرة أخرى."
        }), 500

@app.route('/ask_get', methods=['GET'])
def ask_question_get():
    """طرح سؤال عبر GET"""
    
    question = request.args.get('q', '').strip()
    
    if not question:
        return jsonify({
            "success": False,
            "error": "يرجى إضافة السؤال في المعلمة q",
            "example": "/ask_get?q=كيف أحجز موعد؟"
        })
    
    try:
        # الحصول على السياق
        context = knowledge_base.get_context_for_question(question)
        
        # توليد الرد
        answer = qwen_client.generate(context, question)
        
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "model": "Qwen2.5-7B-Instruct"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/test', methods=['GET'])
def test():
    """اختبار النظام"""
    
    test_cases = [
        "مرحبا",
        "كيف أحجز موعد في العيادة؟",
        "كم تكلفة تنظيف الأسنان؟",
        "أين تقع عيادتكم؟",
        "ما هي أوقات الدوام؟",
        "عندي ألم شديد في الضرس",
        "هل تقدمون خدمة تقويم الأسنان؟",
        "ماذا أفعل في حالة كسر السن؟",
        "هل تعالجون الأطفال؟",
        "ما هي طرق الدفع المتاحة؟"
    ]
    
    results = []
    
    for question in test_cases:
        try:
            context = knowledge_base.get_context_for_question(question)
            answer = qwen_client.generate(context, question)
            
            results.append({
                "question": question,
                "answer_preview": answer[:100] + ("..." if len(answer) > 100 else ""),
                "answer_length": len(answer),
                "success": True
            })
        except Exception as e:
            results.append({
                "question": question,
                "error": str(e),
                "success": False
            })
    
    return jsonify({
        "system": "Dental AI Assistant with Qwen2.5",
        "total_tests": len(test_cases),
        "passed": sum(1 for r in results if r['success']),
        "results": results
    })

@app.route('/info', methods=['GET'])
def clinic_info():
    """معلومات عن العيادة"""
    
    clinic = knowledge_base.data["clinic"]
    hours = knowledge_base.data["working_hours"]
    
    return jsonify({
        "success": True,
        "clinic": {
            "name": clinic["name"],
            "address": clinic["address"],
            "contact": {
                "phone": clinic["phone"],
                "whatsapp": clinic["whatsapp"],
                "email": clinic["email"],
                "website": clinic["website"]
            }
        },
        "working_hours": hours,
        "emergency": clinic["emergency_phone"]
    })

# نقطة الدخول لـ Vercel
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🌐 التشغيل على المنفذ {port}")
    print(f"🤖 النموذج: Qwen2.5-7B-Instruct")
    print(f"🔧 الوضع: API External")
    app.run(host='0.0.0.0', port=port, debug=False)
