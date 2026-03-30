import os
import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import streamlit as st

# =========================
#  إعداد مفاتيح الـ API
# =========================

# يمكنك استخدام متغيرات البيئة بدلًا من وضع المفتاح مباشرة
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")

# إذا كنت تستخدم مكتبة openai الرسمية الجديدة:
try:
    from openai import OpenAI
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
except ImportError:
    # في حال استخدام النسخة القديمة:
    import openai
    openai.api_key = OPENAI_API_KEY
    openai_client = None


# =========================
#  تعريف الفئات الأساسية
# =========================

@dataclass
class JobLensConfig:
    """إعدادات عامة للنظام."""
    llm_router_model: str = "gpt-3.5-turbo"
    llm_coding_model: str = "gpt-4"
    llm_general_model: str = "gpt-4"
    llm_career_model: str = "gpt-4"
    max_history_messages: int = 10
    enable_memory: bool = True
    enable_skill_filter: bool = True


@dataclass
class UserMessage:
    role: str  # "user" أو "assistant" أو "system"
    content: str


@dataclass
class ConversationState:
    """حالة المحادثة لكل مستخدم (جلسة Streamlit)."""
    history: List[UserMessage] = field(default_factory=list)
    career_profile: Dict[str, Any] = field(default_factory=dict)
    last_category: Optional[str] = None
    last_expert: Optional[str] = None
    last_skills: List[str] = field(default_factory=list)


# =========================
#  مدير الذاكرة البسيط
# =========================

class MemoryManager:
    """
    مدير ذاكرة بسيط يعتمد على st.session_state.
    يبني "مسار مهني" للمستخدم مع الوقت.
    """

    SESSION_KEY = "joblens_state"

    @staticmethod
    def get_state() -> ConversationState:
        if MemoryManager.SESSION_KEY not in st.session_state:
            st.session_state[MemoryManager.SESSION_KEY] = ConversationState()
        return st.session_state[MemoryManager.SESSION_KEY]

    @staticmethod
    def add_message(role: str, content: str):
        state = MemoryManager.get_state()
        state.history.append(UserMessage(role=role, content=content))
        # تقليص التاريخ إذا زاد عن الحد
        if len(state.history) > JobLensConfig().max_history_messages:
            state.history = state.history[-JobLensConfig().max_history_messages:]

    @staticmethod
    def update_career_profile(new_info: Dict[str, Any]):
        state = MemoryManager.get_state()
        state.career_profile.update(new_info)

    @staticmethod
    def set_last_routing(category: str, expert: str):
        state = MemoryManager.get_state()
        state.last_category = category
        state.last_expert = expert

    @staticmethod
    def set_last_skills(skills: List[str]):
        state = MemoryManager.get_state()
        state.last_skills = skills


# =========================
#  فلتر المهارات (Skill Filter)
# =========================

class SkillFilter:
    """
    فلتر بسيط يضمن أن الإجابة تحتوي على كلمات مفتاحية
    مطلوبة في سوق العمل (مثلاً من LinkedIn أو تحليلك السابق).
    هنا سنضع قائمة ثابتة كمثال، ويمكنك لاحقًا ربطها بقاعدة بيانات أو API.
    """

    # مثال لقائمة مهارات مطلوبة (يمكنك تعديلها أو تحميلها من ملف خارجي)
    DEMANDED_SKILLS = [
        "Python",
        "SQL",
        "Machine Learning",
        "Data Analysis",
        "Docker",
        "Kubernetes",
        "Cloud",
        "AWS",
        "Azure",
        "GCP",
        "REST API",
        "Microservices",
        "Pandas",
        "NumPy",
        "TensorFlow",
        "PyTorch",
        "FastAPI",
        "Django",
        "React",
        "TypeScript",
        "CI/CD",
        "Git",
        "Linux",
        "Prompt Engineering",
        "LLM",
        "LangChain",
        "CrewAI",
    ]

    @staticmethod
    def extract_skills_from_text(text: str) -> List[str]:
        """
        يبحث عن المهارات الموجودة في النص بناءً على القائمة أعلاه.
        """
        found = []
        for skill in SkillFilter.DEMANDED_SKILLS:
            pattern = r"\b" + re.escape(skill) + r"\b"
            if re.search(pattern, text, flags=re.IGNORECASE):
                found.append(skill)
        return sorted(list(set(found)))

    @staticmethod
    def ensure_skill_keywords(answer: str, min_skills: int = 3) -> str:
        """
        يتأكد أن الإجابة تحتوي على عدد معين من المهارات.
        إذا كانت قليلة، يضيف فقرة في النهاية تقترح مهارات إضافية.
        """
        found = SkillFilter.extract_skills_from_text(answer)
        if len(found) >= min_skills:
            return answer, found

        # اختيار مهارات إضافية غير موجودة
        missing = [s for s in SkillFilter.DEMANDED_SKILLS if s not in found][: (min_skills - len(found))]
        if missing:
            extra = "\n\n🔑 مهارات إضافية موصى بها لسوق العمل:\n- " + "\n- ".join(missing)
            answer = answer + extra
            found.extend(missing)

        return answer, found


# =========================
#  مصنف النية (Router / Classifier)
# =========================

class IntentRouter:
    """
    مسؤول عن تصنيف السؤال إلى:
    [CODE, IMAGE, CAREER_ADVICE, GENERAL]
    """

    def __init__(self, config: JobLensConfig):
        self.config = config

    def _call_llm_router(self, user_query: str) -> str:
        prompt = (
            "You are an intent classifier for a Saudi career assistant called JobLens AI.\n"
            "Categorize the following query into exactly ONE of these categories:\n"
            "[CODE, IMAGE, CAREER_ADVICE, GENERAL]\n\n"
            f"Query: {user_query}\n\n"
            "Answer with only the category name."
        )

        if openai_client is not None:
            completion = openai_client.chat.completions.create(
                model=self.config.llm_router_model,
                messages=[{"role": "user", "content": prompt}],
            )
            category = completion.choices[0].message.content.strip()
        else:
            completion = openai.ChatCompletion.create(
                model=self.config.llm_router_model,
                messages=[{"role": "user", "content": prompt}],
            )
            category = completion.choices[0].message["content"].strip()

        return category

    def route(self, user_query: str) -> str:
        try:
            category = self._call_llm_router(user_query)
        except Exception:
            # في حال حدوث خطأ، نرجع GENERAL كخيار آمن
            category = "GENERAL"

        # تنظيف النتيجة
        category = category.upper()
        if "CODE" in category:
            return "CODE"
        if "IMAGE" in category:
            return "IMAGE"
        if "CAREER" in category:
            return "CAREER_ADVICE"
        return "GENERAL"


# =========================
#  الوكلاء المتخصصون (Agents)
# =========================

class BaseAgent:
    """فئة أساسية للوكلاء."""

    def __init__(self, config: JobLensConfig):
        self.config = config

    def call_llm(self, model: str, system_prompt: str, user_prompt: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        try:
            if openai_client is not None:
                completion = openai_client.chat.completions.create(
                    model=model,
                    messages=messages,
                )
                return completion.choices[0].message.content
            else:
                completion = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                )
                return completion.choices[0].message["content"]
        except Exception as e:
            return f"حدث خطأ أثناء الاتصال بنموذج الذكاء الاصطناعي: {e}"


class CodingAgent(BaseAgent):
    """وكيل متخصص في البرمجة."""

    def answer(self, query: str, history: List[UserMessage]) -> str:
        # يمكننا استخدام التاريخ لتحسين الإجابة
        history_text = "\n".join(
            [f"{m.role}: {m.content}" for m in history[-5:]]
        )

        system_prompt = (
            "You are a Senior Software Engineer and coding mentor.\n"
            "You answer in Arabic when the user writes in Arabic, and in English otherwise.\n"
            "Provide clean, production-level code, with clear explanations.\n"
        )

        user_prompt = (
            f"السياق السابق للمحادثة:\n{history_text}\n\n"
            f"سؤال المستخدم الحالي:\n{query}\n\n"
            "أجب بشكل منظم، مع أمثلة عملية إن أمكن."
        )

        return self.call_llm(self.config.llm_coding_model, system_prompt, user_prompt)


class ImageAgent(BaseAgent):
    """وكيل مسؤول عن طلبات الصور (توليد/وصف)."""

    def answer(self, query: str) -> str:
        # هنا يمكنك ربط DALL-E أو Stable Diffusion أو Diffusers
        # سنضع ردًا توضيحيًا فقط.
        explanation = (
            "تم تصنيف سؤالك كطلب متعلق بالصور.\n"
            "في النسخة الكاملة من JobLens AI، سيتم هنا استدعاء نموذج توليد الصور "
            "مثل DALL-E 3 أو Stable Diffusion عبر API.\n\n"
            f"وصف الطلب:\n{query}\n\n"
            "يمكنك مثلاً توليد صورة توضح مهارة مهنية، أو إنفوجرافيك لمسار وظيفي."
        )
        return explanation


class CareerAgent(BaseAgent):
    """وكيل متخصص في الاستشارات المهنية وتحليل الوظائف."""

    def analyze_job_text(self, text: str) -> Dict[str, Any]:
        """
        مثال مبسط لتحليل وصف وظيفة باستخدام Regex و NLTK (هنا سنستخدم Regex فقط كمثال).
        يمكنك لاحقًا دمج NLTK أو spaCy لتحليل أعمق.
        """
        # استخراج كلمات مثل: Python, SQL, Machine Learning...
        skills = SkillFilter.extract_skills_from_text(text)

        # استخراج سنوات الخبرة بشكل تقريبي
        exp_pattern = r"(\d+)\s*(?:years|year|سنوات|سنة)"
        exp_matches = re.findall(exp_pattern, text, flags=re.IGNORECASE)
        years_of_experience = max([int(x) for x in exp_matches], default=0) if exp_matches else 0

        return {
            "skills": skills,
            "years_of_experience": years_of_experience,
            "raw_text": text,
        }

    def answer(self, query: str, history: List[UserMessage]) -> str:
        """
        يدمج بين منطق JobLens (تحليل سوق العمل) وبين LLM.
        """
        analysis = self.analyze_job_text(query)

        system_prompt = (
            "You are a Saudi career advisor called JobLens AI.\n"
            "You understand the Saudi job market and global tech trends.\n"
            "You answer in Arabic, with structured, practical advice.\n"
        )

        analysis_text = json.dumps(analysis, ensure_ascii=False, indent=2)

        user_prompt = (
            "المستخدم طلب استشارة مهنية أو تحليل وظيفة.\n\n"
            f"نص الوظيفة أو السؤال:\n{query}\n\n"
            f"تحليل أولي (Regex/Skills):\n{analysis_text}\n\n"
            "بناءً على ذلك، قدّم:\n"
            "1) ملخصًا لما تطلبه هذه الوظيفة أو المسار.\n"
            "2) المهارات الأساسية والفرعية المطلوبة.\n"
            "3) خطة عملية من 3–6 خطوات لتجهيز نفسه لسوق العمل.\n"
            "4) اقتراح كلمات مفتاحية يمكنه إضافتها في السيرة الذاتية أو LinkedIn."
        )

        return self.call_llm(self.config.llm_career_model, system_prompt, user_prompt)


class GeneralAgent(BaseAgent):
    """وكيل للأسئلة العامة (تعلم، شرح، إلخ)."""

    def answer(self, query: str, history: List[UserMessage]) -> str:
        history_text = "\n".join(
            [f"{m.role}: {m.content}" for m in history[-5:]]
        )

        system_prompt = (
            "You are a helpful educational assistant inside JobLens AI.\n"
            "You always try to connect your answers to skills that matter in the job market.\n"
            "Answer in Arabic when the user writes in Arabic.\n"
        )

        user_prompt = (
            f"السياق السابق للمحادثة:\n{history_text}\n\n"
            f"سؤال المستخدم الحالي:\n{query}\n\n"
            "أجب بشكل تعليمي، مع أمثلة، وحاول ربط الإجابة بمهارات قابلة للإضافة في السيرة الذاتية."
        )

        return self.call_llm(self.config.llm_general_model, system_prompt, user_prompt)


# =========================
#  الـ Orchestrator
# =========================

class JobLensOrchestrator:
    """
    هذا هو "العقل المدبر" الذي:
    - يستقبل سؤال المستخدم
    - يمرره إلى الـ Router
    - يختار الوكيل المناسب
    - يطبق فلتر المهارات
    - يحدّث الذاكرة
    """

    def __init__(self, config: JobLensConfig):
        self.config = config
        self.router = IntentRouter(config)
        self.coding_agent = CodingAgent(config)
        self.image_agent = ImageAgent(config)
        self.career_agent = CareerAgent(config)
        self.general_agent = GeneralAgent(config)

    def handle_query(self, user_query: str) -> str:
        # 1) تحديث الذاكرة برسالة المستخدم
        if self.config.enable_memory:
            MemoryManager.add_message("user", user_query)

        # 2) تصنيف السؤال
        category = self.router.route(user_query)

        # 3) اختيار الوكيل المناسب
        state = MemoryManager.get_state()
        history = state.history

        if category == "CODE":
            expert_name = "CodingAgent (Senior Developer)"
            raw_answer = self.coding_agent.answer(user_query, history)
        elif category == "IMAGE":
            expert_name = "ImageAgent (Image Generation/Design)"
            raw_answer = self.image_agent.answer(user_query)
        elif category == "CAREER_ADVICE":
            expert_name = "CareerAgent (Job & Market Analysis)"
            raw_answer = self.career_agent.answer(user_query, history)
        else:
            expert_name = "GeneralAgent (General Learning & Guidance)"
            raw_answer = self.general_agent.answer(user_query, history)

        # 4) فلتر المهارات
        if self.config.enable_skill_filter:
            filtered_answer, skills = SkillFilter.ensure_skill_keywords(raw_answer)
        else:
            filtered_answer, skills = raw_answer, []

        # 5) تحديث الذاكرة بالنتائج
        if self.config.enable_memory:
            MemoryManager.add_message("assistant", filtered_answer)
            MemoryManager.set_last_routing(category, expert_name)
            MemoryManager.set_last_skills(skills)

        return filtered_answer


# =========================
#  واجهة Streamlit
# =========================

def init_page():
    st.set_page_config(
        page_title="بصيرة العمل | JobLens AI",
        page_icon="💼",
        layout="wide",
    )

    # الشعار في الأعلى
    st.sidebar.image("logo.png", width=200)
    st.sidebar.markdown("### بصيرة العمل | JobLens AI")
    st.sidebar.markdown("Saudi-led Digital Guidance")

    st.title("بصيرة العمل | JobLens AI")
    st.caption("منصة سعودية ذكية لتوجيهك مهنيًا وتقنيًا، مبنية على نمط Orchestrator و Multi-Agent System.")


def render_sidebar_controls(config: JobLensConfig):
    st.sidebar.markdown("---")
    st.sidebar.subheader("إعدادات الجلسة")

    enable_memory = st.sidebar.checkbox("تفعيل الذاكرة (مسار مهني مستمر)", value=config.enable_memory)
    enable_skill_filter = st.sidebar.checkbox("تفعيل فلتر المهارات (LinkedIn Keywords)", value=config.enable_skill_filter)

    # يمكن لاحقًا جعل اختيار النماذج ديناميكيًا
    st.sidebar.markdown("**نموذج التوجيه (Router):**")
    st.sidebar.code(config.llm_router_model, language="text")

    st.sidebar.markdown("**نموذج البرمجة (Coding):**")
    st.sidebar.code(config.llm_coding_model, language="text")

    st.sidebar.markdown("**نموذج الاستشارات المهنية (Career):**")
    st.sidebar.code(config.llm_career_model, language="text")

    st.sidebar.markdown("**نموذج الأسئلة العامة (General):**")
    st.sidebar.code(config.llm_general_model, language="text")

    # تحديث القيم في الكائن
    config.enable_memory = enable_memory
    config.enable_skill_filter = enable_skill_filter


def render_conversation_history():
    st.markdown("### سجل المحادثة")
    state = MemoryManager.get_state()
    if not state.history:
        st.info("لم تبدأ المحادثة بعد. اكتب سؤالك في الأسفل.")
        return

    for msg in state.history:
        if msg.role == "user":
            st.markdown(f"**👤 المستخدم:** {msg.content}")
        elif msg.role == "assistant":
            st.markdown(f"**🤖 بصيرة العمل:** {msg.content}")
        else:
            st.markdown(f"**{msg.role}:** {msg.content}")


def render_routing_debug():
    st.markdown("### معلومات التوجيه (Routing Debug)")
    state = MemoryManager.get_state()
    if state.last_category is None:
        st.info("لم يتم التوجيه بعد.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.metric("التصنيف الأخير", state.last_category)
    with col2:
        st.metric("الخبير المستخدم", state.last_expert or "غير محدد")

    if state.last_skills:
        st.markdown("#### المهارات التي تم رصدها/اقتراحها في الإجابة الأخيرة:")
        st.write(", ".join(state.last_skills))


def render_career_profile():
    st.markdown("### المسار المهني (Profile)")
    state = MemoryManager.get_state()
    if not state.career_profile:
        st.info("لم يتم بناء ملف مهني بعد. مع تكرار الأسئلة، يمكن للنظام أن يبني لك مسارًا مهنيًا.")
        return

    st.json(state.career_profile, expanded=True)


def main():
    init_page()

    # إنشاء إعدادات النظام
    config = JobLensConfig()
    render_sidebar_controls(config)

    # إنشاء الـ Orchestrator
    orchestrator = JobLensOrchestrator(config)

    # تقسيم الصفحة إلى أعمدة
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.markdown("## اسأل بصيرة العمل")
        user_query = st.text_area(
            "اكتب سؤالك هنا (برمجة، تحليل وظيفة، استشارة مهنية، أو أي شيء عام):",
            height=150,
            placeholder="مثال: كيف أكتب كود بلغة بايثون لتنظيف البيانات؟\nأو: حلل لي هذا الوصف الوظيفي..."
        )

        if st.button("إرسال السؤال", type="primary"):
            if not user_query.strip():
                st.warning("من فضلك اكتب سؤالًا أولًا.")
            else:
                with st.spinner("جاري التفكير والتوجيه بين الخبراء..."):
                    answer = orchestrator.handle_query(user_query.strip())
                st.success("تم توليد الإجابة من JobLens AI:")
                st.markdown(answer)

        st.markdown("---")
        render_conversation_history()

    with col_right:
        render_routing_debug()
        st.markdown("---")
        render_career_profile()

    st.markdown("---")
    st.caption("تم تصميم هذا النموذج كنظام Multi-Agent Orchestrator لربط المستخدم بأفضل خبير رقمي ممكن.")


if __name__ == "__main__":
    main()
