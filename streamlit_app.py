import streamlit as st
import re
from collections import Counter

# --- 1. إعدادات الصفحة والواجهة ---
st.set_page_config(page_title="JobLens AI | بصيرة العمل", page_icon="🚀", layout="centered")

# --- 2. منطق تحليل البيانات ---
class JobLensAI:
    def __init__(self):
        # قائمة الكلمات التي سنتجاهلها في التحليل (عربي وإنجليزي)
        self.stop_words = {
            'and', 'the', 'in', 'to', 'of', 'for', 'with', 'a', 'is', 'at', 'on', 
            'requirements', 'required', 'years', 'experience', 'knowledge', 'skills', 
            'ability', 'work', 'job', 'must', 'have', 'be', 'an', 'including', 'plus', 
            'preferred', 'qualification', 'from', 'من', 'في', 'على', 'إلى', 'مع', 'عن', 
            'أن', 'هل', 'أو', 'تم', 'كان', 'يكون', 'هذا', 'هذه', 'التي', 'الذي', 'متطلبات', 
            'خبرة', 'سنوات', 'العمل', 'مهارات', 'الوظيفة', 'المطلوبة', 'يفضل', 'معرفة', 
            'قدرة', 'مجال', 'للمرشح', 'إجادة', 'اللغة', 'تطوير'
        }

    def clean_text(self, text):
        # تنظيف النص وتحويله لسمات برمجية
        text = text.lower()
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        words = text.split()
        # إزالة "الـ" التعريفية البسيطة والكلمات غير المهمة
        cleaned = [w[2:] if w.startswith('ال') and len(w) > 4 else w for w in words]
        return [w for w in cleaned if w not in self.stop_words and len(w) > 2]

    def analyze(self, job_description, top_n=10):
        return Counter(self.clean_text(job_description)).most_common(top_n)

# --- 3. تصميم واجهة المستخدم ---
st.title("🚀 JobLens AI | بصيرة العمل")
st.markdown("### جسر بين الدراسة وسوق العمل")
st.info("قم بلصق وصف الوظيفة بالأسفل لاستخراج أهم المهارات المطلوبة.")

# مدخلات وصف الوظيفة
job_input = st.text_area("أدخل وصف الوظيفة هنا:", height=200, placeholder="مثال: مطلوب مبرمج بايثون لديه خبرة في تطوير المواقع...")

if st.button("بدء التحليل"):
    if job_input:
        analyzer = JobLensAI()
        results = analyzer.analyze(job_input)
        st.write("### 📊 أهم المهارات المستخرجة:")
        
        # عرض النتائج بشكل أنيق
        cols = st.columns(2)
        for i, (skill, count) in enumerate(results):
            with cols[i % 2]:
                st.success(f"**{skill}** (تكررت {count} مرات)")
    else:
        st.warning("⚠️ فضلاً، أدخل وصف الوظيفة أولاً للبدء.")

# --- 4. إضافة قسم الدردشة الذكية (إضافتك المميزة) ---
st.divider() # خط فاصل مرئي
st.subheader("💬 اسأل مساعد بصيرة العمل الذكي")
st.caption("أنا هنا لمساعدتك في فهم متطلبات السوق وتقديم نصائح مهنية.")

# لوحة الكتابة (Chat Input)
user_question = st.chat_input("اكتب سؤالك عن الوظيفة أو المهارات هنا...")

if user_question:
    # عرض سؤال المستخدم
    with st.chat_message("user"):
        st.write(user_question)
    
    # استجابة المساعد (أنا)
    with st.chat_message("assistant"):
        st.write("أنا هنا لمساعدتك! بصفتي مساعدك الذكي في **بصيرة العمل**، جاري تحليل سؤالك بعمق وربطه ببيانات سوق العمل...")
        # ملاحظة للمنفذ البطل: في التحديث القادم سنقوم بربط الـ API هنا لجعله يرد فعلياً
        st.write("نصيحة سريعة: المهارات التقنية مهمة، لكن لا تنسَ المهارات الناعمة (Soft Skills) مثل التواصل وحل المشكلات!")
