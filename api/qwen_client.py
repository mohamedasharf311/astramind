"""
🌐 عميل اتصال بـ Qwen2.5-7B عبر API خارجي
لا يحمل النموذج محلياً (يبقى تحت 50MB لـ Vercel)
"""

import os
import requests
import json
from typing import Dict, List, Optional
import time

class QwenClient:
    """عميل للاتصال بـ Qwen2.5-7B عبر Hugging Face أو خدمة خارجية"""
    
    def __init__(self):
        # استخدام Hugging Face Inference API (مجاني محدود)
        self.api_url = "https://api-inference.huggingface.co/models"
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        
        # أو استخدام خدمة Ollama إذا كان عندك سيرفر
        self.ollama_url = os.environ.get("OLLAMA_URL", "")
        
        # مفتاح Hugging Face (سجّل واحصل على token مجاني)
        self.hf_token = os.environ.get("HF_TOKEN", "")
        
        # نسخة احتياطية محلية بسيطة
        self.use_backup = False
        
    def query_huggingface(self, prompt: str, max_tokens: int = 300) -> str:
        """استخدام Hugging Face Inference API"""
        
        if not self.hf_token:
            print("⚠️ HF_TOKEN غير مضبوط، استخدام النسخة الاحتياطية")
            return self._backup_response(prompt)
        
        headers = {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/{self.model_name}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list):
                    return result[0].get('generated_text', '').strip()
                return result.get('generated_text', '').strip()
            else:
                print(f"⚠️ خطأ HuggingFace API: {response.status_code}")
                return self._backup_response(prompt)
                
        except Exception as e:
            print(f"⚠️ فشل الاتصال بـ HuggingFace: {e}")
            return self._backup_response(prompt)
    
    def query_ollama(self, prompt: str) -> str:
        """استخدام Ollama إذا كان عندك سيرفر"""
        
        if not self.ollama_url:
            return self.query_huggingface(prompt)
        
        payload = {
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 300
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            return self.query_huggingface(prompt)
            
        except:
            return self.query_huggingface(prompt)
    
    def generate(self, context: str, question: str) -> str:
        """توليد رد ذكي باستخدام Qwen"""
        
        # بناء prompt محسن لـ Qwen2.5-Instruct
        prompt = self._build_prompt(context, question)
        
        # المحاولة مع Hugging Face أولاً
        response = self.query_huggingface(prompt)
        
        # إذا فشل، جرب Ollama
        if not response or len(response) < 10:
            response = self.query_ollama(prompt)
        
        # إذا فشل كل شيء، استخدم النسخة الاحتياطية
        if not response or len(response) < 10:
            response = self._backup_response(question)
        
        return response
    
    def _build_prompt(self, context: str, question: str) -> str:
        """بناء prompt محسن لـ Qwen2.5-Instruct"""
        
        system_prompt = """أنت مساعد عيادة أسنان ذكي ومتخصص. 
مهمتك مساعدة المرضى بالإجابة على استفساراتهم بطريقة مهنية ومفيدة.

توجيهات مهمة:
1. أجب بلغة عربية فصيحة وواضحة
2. استخدم المعلومات المقدمة فقط - لا تختلق معلومات
3. كن دقيقاً في ذكر التفاصيل
4. إذا كان السؤال يحتاج معلومات غير متوفرة، قل بصراحة "لا أعرف" ونصح بالاتصال بالعيادة
5. كن مهنياً ومتعاطفاً مع المرضى

المعلومات المتاحة:"""
        
        prompt = f"""{system_prompt}

{context}

سؤال المريض: {question}

أجب بطريقة مفيدة ومهنية، مع التركيز على تقديم المعلومات الأكثر أهمية للمريض.
تذكر أن تكون دقيقاً في ذكر الأرقام والعناوين إذا كانت متوفرة.

الإجابة:"""
        
        return prompt
    
    def _backup_response(self, question: str) -> str:
        """رد احتياطي إذا فشل الاتصال"""
        
        question_lower = question.lower()
        
        if any(word in question_lower for word in ['مرحبا', 'اهلا', 'السلام']):
            return "مرحباً! 👋 أنا مساعد عيادة الأسنان الذكي. كيف يمكنني مساعدتك اليوم؟"
        
        elif any(word in question_lower for word in ['حجز', 'موعد']):
            return """📅 لحجز موعد في عيادة الأسنان:
• اتصل بنا على: 0112345678
• أو عبر الواتساب: 0551234567
• من الأحد إلى الخميس: 8 صباحاً - 8 مساءً
• سياسة الإلغاء: مجاني قبل 24 ساعة"""
        
        elif any(word in question_lower for word in ['سعر', 'تكلفة', 'كم']):
            return """💰 الأسعار التقريبية:
• الكشف والتشخيص: 100 ريال
• تنظيف الأسنان: 150 ريال
• حشو الأسنان: 200-350 ريال
• علاج العصب: 500-800 ريال
• تقويم الأسنان: يبدأ من 5000 ريال

ملاحظة: الأسعار قد تختلف حسب الحالة."""
        
        elif any(word in question_lower for word in ['عنوان', 'اين', 'مكان']):
            return """📍 عيادة الأسنان:
• العنوان: شارع الملك فهد، حي العليا، الرياض
• الهاتف: 0112345678
• الواتساب: 0551234567
• البريد: info@dental-smile.com"""
        
        elif any(word in question_lower for word in ['وقت', 'دوام', 'متى']):
            return """🕒 أوقات العمل:
• الأحد إلى الخميس: 8:00 صباحاً - 8:00 مساءً
• الجمعة والسبت: إجازة
• 📞 طوارئ 24 ساعة: 0551234567"""
        
        elif any(word in question_lower for word in ['طارئ', 'عاجل', 'ألم']):
            return """🚨 للحالات الطارئة:
• اتصل فوراً على: 0551234567
• يمكنك الحضور مباشرة للعيادة
• فريق الطوارئ متاح 24 ساعة
• لا تحتاج موعد مسبق للحالات الحرجة"""
        
        else:
            return """مرحباً! يمكنني مساعدتك في:
• حجز المواعيد والزيارات
• معلومات الأسعار والخدمات
• العنوان وطرق التواصل
• أوقات العمل والطوارئ
• استفسارات طبية عامة

ماذا تريد أن تعرف؟ 😊"""
