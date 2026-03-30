import streamlit as st

# إعدادات الصفحة
st.set_page_config(page_title="بصيرة AI", page_icon="🤖")

# تصميم الواجهة لإخفاء القوائم الجانبية الزائدة
st.markdown("""
    <style>
    [data-testid="stSidebar"] {display: none;}
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 مساعد بصيرة الذكي")
st.markdown("اسألني عن أي شيء (برمجية، فضاء، علوم، أو نصيحة مهنية) وسأجيبك فوراً.")

# إعداد حاوية المحادثة (Chat Container)
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل السابقة
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# استقبال سؤال المستخدم
if prompt := st.chat_input("اكتب سؤالك هنا..."):
    # إضافة رسالة المستخدم للمحفوظات
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # رد الذكاء الاصطناعي (منطقي ومباشر)
    with st.chat_message("assistant"):
        # هنا نضع منطق الرد بناءً على الكلمات المفتاحية في سؤال الطالب
        if "فضاء" in prompt or "نجوم" in prompt:
            response = "الفضاء عالم مذهل! هل تعلم أن الضوء يحتاج لسنوات ليصل إلينا من النجوم البعيدة؟ سأكون معك في رحلتك لاستكشاف الكون."
        elif "برمجة" in prompt or "python" in prompt.lower():
            response = "البرمجة هي لغة المستقبل. أنت مبرمج واعد، تذكر دائماً أن الخطأ في الكود هو أول خطوة للتعلم!"
        elif "موهبة" in prompt or "قدرات" in prompt:
            response = "حلمك بالدرجة 2000 قريب جداً. ركز على المنطق الرياضي والقدرة التحليلية، وأنا هنا لأدربك."
        else:
            response = "سؤال ذكي جداً! كذكاء اصطناعي، أرى أن بحثك عن المعرفة هو ما سيجعلك متميزاً. كيف يمكنني مساعدتك أكثر في هذا الموضوع؟"
            
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
