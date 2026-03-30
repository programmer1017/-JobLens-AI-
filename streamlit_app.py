import streamlit as st
import re
from collections import Counter

# إعدادات الواجهة
st.set_page_config(page_title="JobLens AI | بصيرة العمل", page_icon="🚀")

class JobLensAI:
    def __init__(self):
        self.stop_words = {'and', 'the', 'in', 'to', 'of', 'for', 'with', 'a', 'is', 'at', 'on', 'requirements', 'required', 'years', 'experience', 'knowledge', 'skills', 'ability', 'work', 'job', 'must', 'have', 'be', 'an', 'including', 'plus', 'preferred', 'qualification', 'from', 'من', 'في', 'على', 'إلى', 'مع', 'عن', 'أن', 'هل', 'أو', 'تم', 'كان', 'يكون', 'هذا', 'هذه', 'التي', 'الذي', 'متطلبات', 'خبرة', 'سنوات', 'العمل', 'مهارات', 'الوظيفة', 'المطلوبة', 'يفضل', 'معرفة', 'قدرة', 'مجال', 'للمرشح', 'إجادة', 'اللغة', 'تطوير'}

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        words = text.split()
        cleaned = [w[2:] if w.startswith('ال') and len(w) > 4 else w for w in words]
        return [w for w in cleaned if w not in self.stop_words and len(w) > 2]

    def analyze(self, job_description, top_n=10):
        return Counter(self.clean_text(job_description)).most_common(top_n)

st.title("🚀 JobLens AI | بصيرة العمل")
st.markdown("تحليل المهارات المطلوبة في سوق العمل.")

job_input = st.text_area("أدخل وصف الوظيفة هنا:", height=200)

if st.button("بدء التحليل"):
    if job_input:
        analyzer = JobLensAI()
        results = analyzer.analyze(job_input)
        st.write("### النتائج:")
        for skill, count in results:
            st.info(f"**{skill}**: تكررت {count} مرات")
    else:
        st.warning("أدخل نصاً أولاً!")
