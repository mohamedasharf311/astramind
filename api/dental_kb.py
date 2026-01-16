"""
📚 قاعدة معرفة عيادة الأسنان
"""

import json
import os
from typing import Dict, List

class DentalKnowledgeBase:
    """قاعدة معرفة ذكية للعيادة"""
    
    def __init__(self):
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """تحميل بيانات العيادة"""
        return {
            "clinic": {
                "name": "عيادة الابتسامة الذهبية لطب وتجميل الأسنان",
                "arabic_name": "عيادة الابتسامة الذهبية",
                "address": "حي العليا، شارع الملك فهد، مقابل مركز العليا التجاري، الرياض",
                "phone": "0112345678",
                "whatsapp": "0551234567",
                "emergency_phone": "0551234567",
                "email": "info@golden-smile.com",
                "website": "www.golden-smile-dental.com",
                "instagram": "@golden_smile_dental",
                "google_maps": "https://maps.app.goo.gl/example"
            },
            "working_hours": {
                "regular": "الأحد إلى الخميس: 8:00 صباحاً - 8:00 مساءً",
                "weekend": "الجمعة والسبت: إجازة",
                "emergency": "24 ساعة على الواتساب (0551234567)"
            },
            "services": [
                {
                    "category": "تشخيص",
                    "items": [
                        {"name": "الكشف والتشخيص الشامل", "price": "100 ريال", "duration": "30 دقيقة"},
                        {"name": "أشعة الأسنان الرقمية", "price": "50-150 ريال", "duration": "15 دقيقة"}
                    ]
                },
                {
                    "category": "علاج وقائي",
                    "items": [
                        {"name": "تنظيف الأسنان الاحترافي", "price": "150 ريال", "duration": "45 دقيقة"},
                        {"name": "علاج اللثة", "price": "200-400 ريال", "duration": "60 دقيقة"}
                    ]
                },
                {
                    "category": "علاج تجميلي",
                    "items": [
                        {"name": "حشو الأسنان التجميلي", "price": "200-350 ريال", "duration": "45-60 دقيقة"},
                        {"name": "تبييض الأسنان بالليزر", "price": "800-1200 ريال", "duration": "60 دقيقة"},
                        {"name": "قشور خزفية (فينير)", "price": "1000-1500 ريال/سن", "duration": "أسبوعين"}
                    ]
                },
                {
                    "category": "علاج متقدم",
                    "items": [
                        {"name": "علاج عصب الأسنان", "price": "500-800 ريال", "duration": "1-2 ساعات"},
                        {"name": "زراعة الأسنان", "price": "3000-5000 ريال/سن", "duration": "3-6 أشهر"},
                        {"name": "تقويم الأسنان", "price": "5000-15000 ريال", "duration": "18-24 شهر"}
                    ]
                }
            ],
            "doctors": [
                {
                    "name": "د. أحمد محمد",
                    "title": "استشاري جراحة الفم والأسنان",
                    "specialty": "الزراعة - جراحة الفم - علاج العصب",
                    "experience": "15 سنة"
                },
                {
                    "name": "د. سارة عبدالله",
                    "title": "أخصائية تقويم الأسنان",
                    "specialty": "تقويم الأطفال والكبار - التقويم الشفاف",
                    "experience": "10 سنوات"
                }
            ],
            "policies": {
                "appointment": {
                    "booking": ["الهاتف", "الواتساب", "الموقع الإلكتروني", "زيارة العيادة"],
                    "confirmation": "يتم تأكيد الحجز قبل 24 ساعة",
                    "reminder": "تذكير قبل الموعد بيوم"
                },
                "cancellation": {
                    "free": "قبل 24 ساعة من الموعد",
                    "late": "50% من قيمة الخدمة",
                    "no_show": "100% من قيمة الخدمة"
                },
                "payment": {
                    "methods": ["نقداً", "بطاقات ائتمان", "مدى", "تحويل بنكي"],
                    "installments": "تقسيط بدون فواصل للعلاجات الكبيرة",
                    "insurance": "نقبل معظم شركات التأمين الطبي"
                }
            },
            "facilities": [
                "أجهزة أشعة رقمية متطورة",
                "مختبر أسنان متكامل",
                "غرف معقمة بأعلى المواصفات",
                "مواقف مجانية للسيارات",
                "إنترنت مجاني",
                "غرفة انتظار مريحة"
            ],
            "offers": [
                {
                    "title": "عرض الكشف الأول",
                    "description": "الكشف والتشخيص مجاناً لأول مرة",
                    "code": "FIRSTFREE"
                },
                {
                    "title": "عرض التنظيف",
                    "description": "تنظيف الأسنان + فحص مجاني بـ 100 ريال فقط",
                    "code": "CLEAN100"
                }
            ]
        }
    
    def get_context_for_question(self, question: str) -> str:
        """الحصول على السياق المناسب للسؤال"""
        
        question_lower = question.lower()
        context_parts = []
        
        # 1. معلومات عامة عن العيادة
        clinic = self.data["clinic"]
        context_parts.append(f"""معلومات العيادة:
- الاسم: {clinic['name']}
- العنوان: {clinic['address']}
- الهاتف: {clinic['phone']}
- الواتساب: {clinic['whatsapp']}
- البريد: {clinic['email']}
- الموقع: {clinic['website']}""")
        
        # 2. معلومات الحجز إذا كان السؤال عن المواعيد
        if any(word in question_lower for word in ['حجز', 'موعد', 'زيارة', 'كشف', 'احجز']):
            policies = self.data["policies"]["appointment"]
            context_parts.append(f"""نظام الحجز:
- طرق الحجز: {', '.join(policies['booking'])}
- تأكيد الحجز: {policies['confirmation']}
- التذكير: {policies['reminder']}
- سياسة الإلغاء: مجاني قبل 24 ساعة""")
        
        # 3. الأسعار إذا كان السؤال عن التكلفة
        if any(word in question_lower for word in ['سعر', 'تكلفة', 'كم', 'ثمن', 'رسوم', 'دفع']):
            context_parts.append("الأسعار التقريبية للخدمات:")
            for category in self.data["services"]:
                context_parts.append(f"\n{category['category']}:")
                for item in category["items"][:2]:  # أول خدمتين من كل قسم
                    context_parts.append(f"- {item['name']}: {item['price']} ({item['duration']})")
        
        # 4. الأوقات
        if any(word in question_lower for word in ['وقت', 'دوام', 'متى', 'يفتح', 'يغلق', 'ساعات']):
            hours = self.data["working_hours"]
            context_parts.append(f"""أوقات العمل:
- {hours['regular']}
- {hours['weekend']}
- الطوارئ: {hours['emergency']}""")
        
        # 5. الأطباء
        if any(word in question_lower for word in ['طبيب', 'دكتور', 'اخصائي', 'من الأفضل']):
            context_parts.append("فريق الأطباء:")
            for doctor in self.data["doctors"]:
                context_parts.append(f"- {doctor['name']}: {doctor['title']} (تخصص: {doctor['specialty']})")
        
        # 6. الخدمات
        if any(word in question_lower for word in ['خدمة', 'علاج', 'تنظيف', 'تقويم', 'حشو', 'تبييض']):
            context_parts.append("الخدمات المتاحة:")
            for category in self.data["services"]:
                context_parts.append(f"\n{category['category']}:")
                for item in category["items"]:
                    context_parts.append(f"- {item['name']}")
        
        return "\n\n".join(context_parts)
    
    def search(self, question: str) -> List[str]:
        """البحث عن معلومات محددة"""
        
        results = []
        question_lower = question.lower()
        
        # بحث في الخدمات
        for category in self.data["services"]:
            for item in category["items"]:
                item_name_lower = item["name"].lower()
                if any(word in item_name_lower for word in question_lower.split()):
                    results.append(f"✅ {item['name']}: {item['price']} ({item['duration']})")
        
        # بحث في العروض
        for offer in self.data["offers"]:
            if any(word in offer["title"].lower() for word in question_lower.split()):
                results.append(f"🎁 {offer['title']}: {offer['description']} (كود: {offer['code']})")
        
        return results[:5]  # أفضل 5 نتائج
