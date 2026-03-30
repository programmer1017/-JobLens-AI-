# --- إضافة قسم الدردشة الذكية ---
st.divider() # خط فاصل
st.subheader("💬 اسأل مساعد بصيرة العمل الذكي")

# لوحة الكتابة
user_question = st.chat_input("اكتب سؤالك عن الوظيفة أو المهارات هنا...")

if user_question:
    with st.chat_message("user"):
        st.write(user_question)
    
    with st.chat_message("assistant"):
        st.write("أنا هنا لمساعدتك! جاري تحليل سؤالك وربطه ببيانات سوق العمل...")
        # هنا سنضع لاحقاً الكود الذي يربطني بالتطبيق للرد مباشرة
