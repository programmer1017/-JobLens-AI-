import streamlit as st
import re
from collections import Counter

# 1. إعدادات الصفحة
st.set_page_config(page_title="منصة بصيرة التعليمية", page_icon="🎓", layout="wide")

# 2. محرك التحليل الأساسي (الذي اشتغلنا عليه سابقاً)
def analyze_skills(text):
    stop_words = {'من', 'في', 'على', 'إلى', 'مع', 'عن', 'أن', 'أو', 'تم', 'كان', 'هذا', 'هذه', 'the', 'and', 'to', 'of', 'in', 'for', 'is'}
    text = re.sub(r'[^\w\s]', ' ', text.lower())
    words = text.split()
    cleaned = [w for w in words if w not in stop_words and len(w) > 2]
    return Counter(cleaned).most_common(10)

# 3. القائمة الجانبية (Sidebar) للتنقل
st.sidebar.title("📑 أقسام المنصة")
menu = st.sidebar.radio("اختر القسم:", [
    "بوصلة التوظيف", 
    "المعلم الذكي (علوم وفضاء)", 
    "أكاديمية الموهبة والقدرات", 
    "الأمن السيبراني والبرمجة"
])

# --- القسم الأول: بوصلة التوظيف (تم تعديله كما طلبت) ---
if menu == "بوصلة التوظيف":
    st.title("🎯 جسر بين الدراسة وسوق العمل")
    st.write("قم بوضع وصف الوظيفة بالأسفل لاستخراج أهم المهارات المطلوبة.")
    
    # الصندوق فارغ تماماً من النصوص الداخلية كما طلبت
    job_input = st.text_area("أدخل وصف الوظيفة هنا:", height=200, placeholder="")
    
    if st.button("بدء التحليل"):
        if job_input:
            results = analyze_skills(job_input)
            st.subheader("النتائج:")
            for skill, count in results:
                st.info(f"**{skill}**: تكررت {count} مرات")
        else:
            st.warning("الرجاء إدخال نص أولاً.")

# --- القسم الثاني: المعلم الذكي (فيزياء، كيمياء، فضاء) ---
elif menu == "المعلم الذكي (علوم وفضاء)":
    st.title("🚀 المعلم الذكي")
    st.write("تعلم الفيزياء، الكيمياء، والرياضيات بأسلوب منطقي ومبسط.")
    subject = st.selectbox("المادة:", ["علوم الأرض والفضاء", "الفيزياء", "الكيمياء", "الرياضيات"])
    level = st.select_slider("مواك الدراسي:", options=["ابتدائي", "متوسط", "ثانوي", "جامعي"])
    question = st.text_input("ما هو سؤالك العلمي؟", placeholder="")
    
    if st.button("اشرح لي"):
        st.success(f"أهلاً بك. سأقوم بشرح {question} بطريقة تناسب مستوى {level}...")

# --- القسم الثالث: موهبة والقدرات ---
elif menu == "أكاديمية الموهبة والقدرات":
    st.title("🌟 طريقك نحو الدرجة 2000")
    st.write("تدريب خاص على اختبارات موهبة، ستيب، والقدرات.")
    exam = st.selectbox("نوع الاختبار:", ["موهبة المستوى 3", "القدرات", "التحصيلي", "STEP"])
    
    if st.button("تحميل الأسئلة التدريبية"):
        st.info(f"جاري تجهيز بنك أسئلة {exam}...")

# --- القسم الرابع: الأمن السيبراني ---
elif menu == "الأمن السيبراني والبرمجة":
    st.title("🛡️ مدرسة الأمن السيبراني")
    st.write("تعلم البرمجة وحماية الأنظمة من الاختراق.")
    st.radio("اختر المسار:", ["أساسيات Python", "أمن الشبكات", "التشفير"])
    if st.button("ابدأ الدرس"):
        st.write("استعد للمغامرة الرقمية!")
