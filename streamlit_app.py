import streamlit as st
import google.generativeai as genai

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="بصيرة AI", page_icon="🤖")

# إخفاء العناصر غير الضرورية للتركيز على الشات
st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)

# 2. إعداد "عقل" الذكاء الاصطناعي (تحتاج وضع مفتاح الـ API الخاص بك هنا)
# يمكنك الحصول عليه مجاناً من Google AI Studio
API_KEY = "ضغ_هنا_مفتاح_الـ_API_الخاص_بك" 
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

st.title("🤖 مساعد بصيرة الذكي")
st.caption("ذكاء اصطناعي حقيقي للإجابة على أسئلتك التعليمية والمهنية مباشرة")

# 3. إدارة ذاكرة المحادثة
if "messages" not in st.session_state:
    st.session_state.messages = []

# عرض الرسائل
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. استقبال السؤال والرد المباشر
if prompt := st.chat_input("اكتب سؤالك هنا (مثلاً: اشرح لي الثقوب السوداء، أو حل مسألة كيمياء)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        try:
            # طلب الإجابة المباشرة من Gemini
            # أضفنا تعليمات برمجية لكي يجيب بذكاء ومنطق يناسب الطلاب
            full_prompt = f"أجب كمعلم خبير وذكي بأسلوب مباشر ومنطقي على هذا السؤال: {prompt}"
            response = model.generate_content(full_prompt)
            
            answer = response.text
            message_placeholder.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except Exception as e:
            st.error("تأكد من إدخال مفتاح API صحيح لتفعيل الذكاء الحقيقي.")
