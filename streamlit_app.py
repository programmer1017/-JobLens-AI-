import streamlit as st
import re
from collections import Counter

# ==============================
# إعدادات الصفحة العامة
# ==============================
st.set_page_config(
    page_title="منصة بصيرة الشاملة",
    page_icon="🚀",
    layout="wide"
)

# ==============================
# كلاس تحليل الوظائف JobLens AI
# ==============================
class JobLensAI:
    def __init__(self):
        self.stop_words = {
            'and', 'the', 'in', 'to', 'of', 'for', 'with', 'a', 'is', 'at', 'on',
            'requirements', 'required', 'years', 'experience', 'knowledge', 'skills',
            'ability', 'work', 'job', 'must', 'have', 'be', 'an', 'including', 'plus',
            'preferred', 'qualification', 'from',
            'من', 'في', 'على', 'إلى', 'مع', 'عن', 'أن', 'هل', 'أو', 'تم', 'كان',
            'يكون', 'هذا', 'هذه', 'التي', 'الذي', 'متطلبات', 'خبرة', 'سنوات',
            'العمل', 'مهارات', 'الوظيفة', 'المطلوبة', 'يفضل', 'معرفة', 'قدرة',
            'مجال', 'للمرشح', 'إجادة', 'اللغة', 'تطوير'
        }

    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\w\s\u0600-\u06FF]', ' ', text)
        words = text.split()
        cleaned = [w[2:] if w.startswith('ال') and len(w) > 4 else w for w in words]
        return [w for w in cleaned if w not in self.stop_words and len(w) > 2]

    def analyze(self, job_description, top_n=10):
        return Counter(self.clean_text(job_description)).most_common(top_n)

# ==============================
# واجهة: بوصلة التوظيف
# ==============================
def employment_compass():
    st.title("🎯 بوصلة التوظيف والخريجين")

    col1, col2 = st.columns(2)
    with col1:
        specialty = st.text_input("تخصصك الجامعي:")
        country = st.selectbox("الدولة:", ["السعودية", "الإمارات", "الكويت", "أخرى"])
    with col2:
        job_goal = st.text_input("الوظيفة التي تطمح لها:")

    if st.button("تحليل المسار المهني"):
        st.info(
            f"تحليل ذكي: سوق العمل في {country} يحتاج بشدة لمبرمجين في تخصص {specialty}. "
            f"ننصحك بتطوير مهارات الذكاء الاصطناعي."
        )

# ==============================
# واجهة: المعلم الذكي
# ==============================
def smart_teacher():
    st.title("🔬 المعلم الذكي")

    subject = st.selectbox("اختر المادة:", ["فيزياء", "كيمياء", "فضاء", "رياضيات"])
    level = st.select_slider("حدد مستواك الدراسي:", ["ابتدائي", "متوسط", "ثانوي", "جامعي"])
    question = st.text_input("ماذا تريد أن تتعلم اليوم؟")

    if st.button("اشرح لي"):
        st.success(f"سيقوم الذكاء الاصطناعي بشرح {question} بأسلوب يناسب طالب في المرحلة {level}.")

# ==============================
# واجهة: استعداد (قدرات/موهبة)
# ==============================
def talent_preparation():
    st.title("🌟 قسم موهبة والقدرات")
    st.write("هنا نتدرب على إنجاز حلمك (الدرجة 2000 في موهبة)!")
    st.info("سيتم إضافة بنك أسئلة ذكي قريباً.")

# ==============================
# واجهة: أكاديمية الأمن السيبراني
# ==============================
def cybersecurity_academy():
    st.title("🛡️ أكاديمية الأمن السيبراني")
    st.write("تعلم كيف تحمي الأنظمة وتكتشف الثغرات.")

# ==============================
# واجهة: JobLens AI
# ==============================
def joblens_ai():
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

# ==============================
# القائمة الجانبية للتنقل
# ==============================
st.sidebar.title("📚 أقسام المنصة")

choice = st.sidebar.radio(
    "اختر القسم:",
    [
        "بوصلة التوظيف",
        "المعلم الذكي (علوم/رياضيات)",
        "استعداد (قدرات/موهبة)",
        "أكاديمية الأمن السيبراني",
        "JobLens AI"
    ]
)

# ==============================
# تشغيل القسم المختار
# ==============================
if choice == "بوصلة التوظيف":
    employment_compass()
elif choice == "المعلم الذكي (علوم/رياضيات)":
    smart_teacher()
elif choice == "استعداد (قدرات/موهبة)":
    talent_preparation()
elif choice == "أكاديمية الأمن السيبراني":
    cybersecurity_academy()
elif choice == "JobLens AI":
    joblens_ai()

# ==============================
# قسم الدردشة الذكية (يظهر دائماً)
# ==============================
st.divider()
st.subheader("💬 اسأل مساعد بصيرة العمل الذكي")

user_question = st.chat_input("اكتب سؤالك عن الوظيفة أو المهارات هنا...")

if user_question:
    with st.chat_message("user"):
        st.write(user_question)

    with st.chat_message("assistant"):
        st.write("أنا هنا لمساعدتك! جاري تحليل سؤالك وربطه ببيانات سوق العمل...")
        # لاحقاً يمكن إضافة API للذكاء الاصطناعي
