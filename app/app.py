import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PATH CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


# ============================================================
# RAG ENGINE
# ============================================================

from rag_engine import answer_question


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="TechNova AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* -------------------------------------------------------
       GLOBAL
    ------------------------------------------------------- */

    .stApp {
        background:
            radial-gradient(
                circle at 20% 10%,
                rgba(99, 102, 241, 0.12),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 15%,
                rgba(14, 165, 233, 0.10),
                transparent 30%
            ),
            #0b0d12;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }


    /* -------------------------------------------------------
       SIDEBAR
       ------------------------------------------------------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #151821 0%,
                #101219 100%
            );
        border-right: 1px solid rgba(255,255,255,0.07);
    }

    section[data-testid="stSidebar"] .block-container {
        padding: 2rem 1.25rem;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 1.8rem;
    }

    .brand-icon {
        width: 45px;
        height: 45px;
        border-radius: 13px;

        display: flex;
        align-items: center;
        justify-content: center;

        font-size: 23px;

        background:
            linear-gradient(
                135deg,
                #6366f1,
                #06b6d4
            );

        box-shadow:
            0 10px 30px rgba(99,102,241,0.25);
    }

    .brand-title {
        font-size: 20px;
        font-weight: 750;
        color: #f8fafc;
        line-height: 1.1;
    }

    .brand-subtitle {
        font-size: 11px;
        color: #94a3b8;
        margin-top: 4px;
    }

    .sidebar-heading {
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-top: 1.8rem;
        margin-bottom: 0.8rem;
    }

    .source-item {
        display: flex;
        align-items: center;
        gap: 10px;

        padding: 10px 11px;
        margin: 6px 0;

        border-radius: 10px;

        background: rgba(255,255,255,0.025);
        border: 1px solid rgba(255,255,255,0.045);

        color: #cbd5e1;
        font-size: 13px;
    }

    .source-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #22c55e;
        box-shadow: 0 0 10px rgba(34,197,94,0.6);
    }

    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;

        border-top: 1px solid rgba(255,255,255,0.07);

        font-size: 11px;
        color: #64748b;
        line-height: 1.6;
    }


    /* -------------------------------------------------------
       HERO
       ------------------------------------------------------- */

    .hero {
        padding: 2.5rem 2.5rem 2.2rem 2.5rem;

        border-radius: 24px;

        background:
            linear-gradient(
                135deg,
                rgba(30,41,59,0.92),
                rgba(15,23,42,0.72)
            );

        border: 1px solid rgba(148,163,184,0.12);

        box-shadow:
            0 25px 80px rgba(0,0,0,0.28);

        margin-bottom: 1.6rem;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 7px;

        padding: 6px 11px;

        border-radius: 999px;

        background: rgba(34,197,94,0.09);
        border: 1px solid rgba(34,197,94,0.18);

        color: #86efac;
        font-size: 11px;
        font-weight: 700;

        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    .hero-title {
        font-size: clamp(34px, 5vw, 54px);
        font-weight: 800;

        line-height: 1.05;

        margin: 18px 0 12px 0;

        background:
            linear-gradient(
                90deg,
                #ffffff,
                #c7d2fe,
                #67e8f9
            );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-text {
        color: #94a3b8;
        font-size: 16px;
        line-height: 1.7;
        max-width: 750px;
    }


    /* -------------------------------------------------------
       STATUS CARDS
       ------------------------------------------------------- */

    .status-card {
        padding: 16px;

        border-radius: 16px;

        background: rgba(15,23,42,0.68);
        border: 1px solid rgba(148,163,184,0.10);

        margin-bottom: 1rem;
    }

    .status-label {
        color: #64748b;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        font-weight: 700;
    }

    .status-value {
        color: #e2e8f0;
        font-size: 14px;
        font-weight: 650;
        margin-top: 6px;
    }


    /* -------------------------------------------------------
       SECTION TITLES
       ------------------------------------------------------- */

    .section-title {
        color: #f1f5f9;
        font-size: 17px;
        font-weight: 750;
        margin-top: 1.5rem;
        margin-bottom: 0.7rem;
    }


    /* -------------------------------------------------------
       CHAT
       ------------------------------------------------------- */

    .user-message {
        background:
            linear-gradient(
                135deg,
                rgba(79,70,229,0.18),
                rgba(59,130,246,0.08)
            );

        border: 1px solid rgba(99,102,241,0.18);

        border-radius: 18px 18px 5px 18px;

        padding: 15px 18px;

        margin: 15px 0 10px auto;

        max-width: 88%;

        color: #e2e8f0;
        line-height: 1.6;
    }

    .assistant-message {
        background:
            linear-gradient(
                135deg,
                rgba(30,41,59,0.85),
                rgba(15,23,42,0.78)
            );

        border: 1px solid rgba(148,163,184,0.10);

        border-radius: 5px 18px 18px 18px;

        padding: 18px 20px;

        margin: 8px auto 15px 0;

        max-width: 92%;

        color: #e2e8f0;
        line-height: 1.7;

        box-shadow:
            0 12px 35px rgba(0,0,0,0.15);
    }

    .message-label {
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.08em;

        color: #64748b;

        margin-bottom: 8px;
    }


    /* -------------------------------------------------------
       SOURCE CARDS
       ------------------------------------------------------- */

    .source-card {
        padding: 13px 15px;

        margin: 7px 0;

        border-radius: 12px;

        background: rgba(2,6,23,0.48);

        border: 1px solid rgba(148,163,184,0.08);
    }

    .source-name {
        color: #c7d2fe;
        font-weight: 650;
        font-size: 13px;
    }

    .source-score {
        color: #64748b;
        font-size: 11px;
        margin-top: 4px;
    }


    /* -------------------------------------------------------
       WELCOME CARD
       ------------------------------------------------------- */

    .welcome {
        text-align: center;

        padding: 3rem 1rem 2rem 1rem;

        color: #94a3b8;
    }

    .welcome-icon {
        font-size: 46px;
        margin-bottom: 12px;
    }

    .welcome-title {
        color: #e2e8f0;
        font-size: 22px;
        font-weight: 750;
    }

    .welcome-text {
        max-width: 620px;
        margin: 8px auto;

        color: #64748b;
        line-height: 1.6;
    }


    /* -------------------------------------------------------
       INPUT
       ------------------------------------------------------- */

    div[data-testid="stChatInput"] {
        border-radius: 18px;
    }

    div[data-testid="stChatInput"] textarea {
        border-radius: 18px !important;
    }


    /* -------------------------------------------------------
       BUTTONS
       ------------------------------------------------------- */

    .stButton > button {
        border-radius: 11px;

        border: 1px solid rgba(148,163,184,0.12);

        background: rgba(30,41,59,0.55);

        color: #cbd5e1;

        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        border-color: rgba(129,140,248,0.45);

        background: rgba(79,70,229,0.13);

        color: #ffffff;

        transform: translateY(-1px);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SOURCE RENDERING
# ============================================================

def render_sources(message):
    """Display retrieved document sources below an AI response."""

    sources = message.get("sources", [])
    retrieved_count = message.get("retrieved_count", 0)

    if not sources:
        return

    st.html(
        """
        <div style="
            margin-top: 12px;
            margin-bottom: 8px;
            font-size: 15px;
            font-weight: 700;
        ">
            📚 Sources
        </div>
        """
    )

    for source in sources:

        document = source.get(
            "document",
            "Unknown document"
        )

        chunk_id = source.get(
            "chunk_id",
            "N/A"
        )

        score = float(
            source.get(
                "score",
                0
            )
        )

        st.html(
            f"""
            <div class="source-card">

                <div class="source-item">

                    <div>
                        <strong>📄 {document}</strong>
                    </div>

                    <div style="margin-top: 5px;">
                        <span>Chunk: {chunk_id}</span>
                    </div>

                    <div style="margin-top: 3px;">
                        <span>Relevance: {score:.2f}</span>
                    </div>

                </div>

            </div>
            """
        )

    st.html(
        f"""
        <div style="
            margin-top: 5px;
            margin-bottom: 15px;
            font-size: 12px;
            opacity: 0.65;
        ">
            Retrieved passages: {retrieved_count}
        </div>
        """
    )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_document" not in st.session_state:
    st.session_state.selected_document = None


# ============================================================
# DOCUMENT CONFIGURATION
# ============================================================

DOCUMENTS = {

    "leave": {
        "name": "Leave Policy",
        "file": "Leave_Policy.docx",
        "icon": "📅",
        "description":
            "Guidelines covering employee leave, eligibility, "
            "annual leave entitlement, and leave procedures.",
    },

    "attendance": {
        "name": "Attendance Policy",
        "file": "Attendance_Policy.docx",
        "icon": "🕐",
        "description":
            "Guidelines covering employee attendance, working "
            "hours, punctuality, and absence.",
    },

    "wfh": {
        "name": "Work From Home Policy",
        "file": "Work_From_Home_Policy.docx",
        "icon": "🏠",
        "description":
            "Guidelines for employees working remotely, including "
            "eligibility, approvals, and remote-work expectations.",
    },

    "handbook": {
        "name": "Employee Handbook",
        "file": "Employee_Handbook.docx",
        "icon": "👤",
        "description":
            "General information about TechNova Solutions, "
            "employee responsibilities, workplace practices, "
            "and organizational guidelines.",
    },

    "security": {
        "name": "IT Security Policy",
        "file": "IT_Security_Policy.docx",
        "icon": "🔐",
        "description":
            "Rules for protecting company systems, accounts, "
            "devices, information, and organizational data.",
    },

    "acceptable": {
        "name": "Acceptable Use Policy",
        "file": "Acceptable_Use_Policy.docx",
        "icon": "🛡️",
        "description":
            "Rules governing appropriate use of company systems, "
            "software, internet access, and network resources.",
    },

    "travel": {
        "name": "Travel Policy",
        "file": "Travel_Policy.docx",
        "icon": "✈️",
        "description":
            "Guidelines for official business travel, approvals, "
            "expenses, and travel procedures.",
    },

    "procurement": {
        "name": "Procurement SOP",
        "file": "Procurement_SOP.docx",
        "icon": "🛒",
        "description":
            "Standard operating procedures for organizational "
            "procurement and purchasing activities.",
    },
}


# ============================================================
# DOCUMENT DIRECTORY
# ============================================================

DOCUMENTS_DIR = (
    Path(__file__).resolve().parent.parent
    / "Data"
    / "documents"
)


# ============================================================
# LOAD ACTUAL DOCX CONTENT
# ============================================================

def load_document_content(filename):
    """
    Load the actual content from the selected DOCX document.

    The document page displays real company document content
    instead of manually fabricated information.
    """

    from docx import Document

    file_path = DOCUMENTS_DIR / filename

    if not file_path.exists():
        return []

    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:

        text = paragraph.text.strip()

        if text:
            paragraphs.append(text)

    return paragraphs


# ============================================================
# FIND SELECTED DOCUMENT
# ============================================================

selected_file = st.session_state.selected_document

selected_info = None

for document_id, document in DOCUMENTS.items():

    if document["file"] == selected_file:

        selected_info = document

        break


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    st.html(
        """
        <div style="
            display:flex;
            align-items:center;
            gap:14px;
        ">

            <div style="
                width:55px;
                height:55px;
                border-radius:17px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:27px;
                background:linear-gradient(
                    135deg,
                    #6366f1,
                    #06b6d4
                );
            ">
                🤖
            </div>

            <div>

                <div class="sidebar-title">
                    TechNova AI
                </div>

                <div class="sidebar-subtitle">
                    Enterprise Knowledge Assistant
                </div>

            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # SYSTEM STATUS
    # --------------------------------------------------------

    st.html(
        """
        <div class="status-card">

            <div class="status-label">
                SYSTEM STATUS
            </div>

            <div class="status-value">
                🟢 AI system online
            </div>

        </div>
        """
    )


    # --------------------------------------------------------
    # KNOWLEDGE BASE
    # --------------------------------------------------------

    st.html(
        """
        <div class="sidebar-heading">
            Knowledge Base
        </div>
        """
    )


    # --------------------------------------------------------
    # DOCUMENT BUTTONS
    # --------------------------------------------------------

    for document_id, document in DOCUMENTS.items():

        is_selected = (
            st.session_state.selected_document
            == document["file"]
        )

        if is_selected:

            label = (
                f"{document['icon']}  "
                f"{document['name']}  ✓"
            )

        else:

            label = (
                f"{document['icon']}  "
                f"{document['name']}"
            )

        if st.button(
            label,
            key=f"document_button_{document_id}",
            use_container_width=True,
        ):

            # Store selected document
            st.session_state.selected_document = (
                document["file"]
            )

            # Start fresh conversation
            st.session_state.messages = []

            # Reload application
            st.rerun()


    # --------------------------------------------------------
    # SIDEBAR BACK TO ASSISTANT
    # --------------------------------------------------------

    if selected_info is not None:

        st.markdown("---")

        if st.button(
            "← Back to Assistant",
            key="sidebar_back_to_assistant",
            use_container_width=True,
        ):

            # Remove selected document
            st.session_state.selected_document = None

            # Clear document-specific conversation
            st.session_state.messages = []

            # Return to main assistant
            st.rerun()


    # --------------------------------------------------------
    # ASSISTANT CAPABILITIES
    # --------------------------------------------------------

    st.html(
        """
        <div class="sidebar-heading">
            Assistant Capabilities
        </div>
        """
    )

    st.markdown(
        "🔎 Semantic document search"
    )

    st.markdown(
        "📚 Source attribution"
    )

    st.markdown(
        "🛡️ Grounded responses"
    )

    st.markdown(
        "💬 Conversation history"
    )


    # --------------------------------------------------------
    # CLEAR CONVERSATION
    # --------------------------------------------------------

    st.markdown("---")

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# DOCUMENT INFORMATION PAGE
# ============================================================

if selected_info is not None:

    # ========================================================
    # PAGE-LEVEL BACK BUTTON
    # ========================================================

    if st.button(
        "← Back to Assistant",
        key="page_back_to_assistant",
        use_container_width=False,
    ):

        # Remove selected document
        st.session_state.selected_document = None

        # Clear document-specific chat
        st.session_state.messages = []

        # Return to main assistant
        st.rerun()


    # ========================================================
    # DOCUMENT HERO
    # ========================================================

    st.html(
        f"""
        <div class="hero">

            <div class="hero-badge">
                📚 KNOWLEDGE BASE DOCUMENT
            </div>

            <div class="hero-title">
                {selected_info["icon"]}
                {selected_info["name"]}
            </div>

            <div class="hero-text">
                {selected_info["description"]}
            </div>

        </div>
        """
    )


    # ========================================================
    # DOCUMENT METADATA
    # ========================================================

    st.markdown(
        "### 📄 Document Information"
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            f"""
            **Document**

            `{selected_info["file"]}`
            """
        )

    with col2:

        st.markdown(
            """
            **Organization**

            `TechNova Solutions`
            """
        )


    # ========================================================
    # ACTUAL DOCUMENT CONTENT
    # ========================================================

    st.markdown(
        "### 📖 Detailed Policy Information"
    )

    document_content = load_document_content(
        selected_info["file"]
    )


    if document_content:

        for paragraph in document_content:

            # Detect common section headings
            if (
                paragraph[:2].isdigit()
                or paragraph.startswith(
                    (
                        "Introduction",
                        "Purpose",
                        "Scope",
                        "Eligibility",
                        "Responsibilities",
                        "Procedure",
                        "Policy",
                        "Guidelines",
                        "Exceptions",
                    )
                )
            ):

                st.markdown(
                    f"#### {paragraph}"
                )

            else:

                st.markdown(paragraph)

    else:

        st.warning(
            "⚠️ The document could not be loaded."
        )


    # ========================================================
    # DOCUMENT AI ASSISTANT
    # ========================================================

    st.markdown("---")

    st.markdown(
        f"### 🤖 Ask AI about {selected_info['name']}"
    )

    st.caption(
        "Questions are answered using this document "
        "as the selected knowledge source."
    )


    # ========================================================
    # DOCUMENT CHAT HISTORY
    # ========================================================

    for message in st.session_state.messages:

        role = message["role"]

        content = message["content"]


        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        if role == "user":

            st.html(
                f"""
                <div class="user-message">

                    <div class="message-label">
                        You
                    </div>

                    <div>
                        {content}
                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # ASSISTANT MESSAGE
        # ----------------------------------------------------

        else:

            st.html(
                f"""
                <div class="assistant-message">

                    <div class="message-label">
                        🤖 TechNova AI
                    </div>

                    <div>
                        {content}
                    </div>

                </div>
                """
            )

            # ------------------------------------------------
            # DISPLAY SOURCES FOR THIS AI RESPONSE
            # ------------------------------------------------

            render_sources(message)


    # ========================================================
    # DOCUMENT QUESTION
    # ========================================================

    question = st.chat_input(
        f"Ask anything about {selected_info['name']}..."
    )


    if question:

        # Add user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )


        # ----------------------------------------------------
        # DOCUMENT-SPECIFIC RAG
        # ----------------------------------------------------

        with st.spinner(
            "🔎 Searching this document..."
        ):

            result = answer_question(
                question,
                document_name=selected_info["file"],
            )


        # ----------------------------------------------------
        # GET ANSWER
        # ----------------------------------------------------

        answer = result.get(
            "answer",
            "I couldn't generate an answer.",
        )


        # ----------------------------------------------------
        # GET SOURCES
        # ----------------------------------------------------

        sources = result.get(
            "sources",
            [],
        )


        # ----------------------------------------------------
        # STORE ASSISTANT RESPONSE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "retrieved_count":
                    result.get(
                        "retrieved_count",
                        0,
                    ),
            }
        )


        # Reload page
        st.rerun()


# ============================================================
# MAIN ASSISTANT PAGE
# ============================================================

else:

    # ========================================================
    # MAIN HERO
    # ========================================================

    st.html(
        """
        <div class="hero">

            <div class="hero-badge">
                ● Secure Knowledge Assistant
            </div>

            <div class="hero-title">
                Ask your company knowledge.
            </div>

            <div class="hero-text">
                Search internal policies, employee documentation,
                and organizational knowledge using natural language.
                Answers are grounded in the retrieved company documents.
            </div>

        </div>
        """
    )


    # ========================================================
    # EXAMPLE QUESTIONS
    # ========================================================

    st.markdown(
        '<div class="sidebar-heading">✨ Try asking</div>',
        unsafe_allow_html=True,
    )


    example_questions = [
        "How many annual leave days do employees get?",
        "What are the core working hours?",
        "How many consecutive days can employees work from home?",
    ]


    cols = st.columns(3)


    for i, example in enumerate(example_questions):

        with cols[i]:

            if st.button(
                example,
                key=f"example_question_{i}",
                use_container_width=True,
            ):

                st.session_state.pending_question = example

                st.rerun()


    # ========================================================
    # MAIN CHAT HISTORY
    # ========================================================

    for message in st.session_state.messages:

        role = message["role"]

        content = message["content"]


        # ----------------------------------------------------
        # USER MESSAGE
        # ----------------------------------------------------

        if role == "user":

            st.html(
                f"""
                <div class="user-message">

                    <div class="message-label">
                        You
                    </div>

                    <div>
                        {content}
                    </div>

                </div>
                """
            )


        # ----------------------------------------------------
        # ASSISTANT MESSAGE
        # ----------------------------------------------------

        else:

            st.html(
                f"""
                <div class="assistant-message">

                    <div class="message-label">
                        🤖 TechNova AI
                    </div>

                    <div>
                        {content}
                    </div>

                </div>
                """
            )

            # ------------------------------------------------
            # DISPLAY SOURCES FOR THIS AI RESPONSE
            # ------------------------------------------------

            # IMPORTANT:
            # This is the ONLY source rendering call.
            # The old duplicate source block was removed.

            render_sources(message)


    # ========================================================
    # PENDING EXAMPLE QUESTION
    # ========================================================

    pending_question = st.session_state.pop(
        "pending_question",
        None,
    )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    question = st.chat_input(
        "Ask anything about company policies..."
    )


    if pending_question:

        question = pending_question


    # ========================================================
    # PROCESS QUESTION
    # ========================================================

    if question:

        # Add user question
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question,
            }
        )


        # ----------------------------------------------------
        # GENERAL RAG SEARCH
        # ----------------------------------------------------

        with st.spinner(
            "🔎 Searching company knowledge..."
        ):

            result = answer_question(
                question
            )


        # ----------------------------------------------------
        # GET ANSWER
        # ----------------------------------------------------

        answer = result.get(
            "answer",
            "I couldn't generate an answer.",
        )


        # ----------------------------------------------------
        # GET SOURCES
        # ----------------------------------------------------

        sources = result.get(
            "sources",
            [],
        )


        # ----------------------------------------------------
        # STORE ASSISTANT RESPONSE
        # ----------------------------------------------------

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
                "retrieved_count":
                    result.get(
                        "retrieved_count",
                        0,
                    ),
            }
        )


        # Reload page
        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        margin-top:3rem;
        padding-top:1.2rem;
        border-top:1px solid rgba(255,255,255,0.06);
        color:#475569;
        font-size:11px;
    ">
        TechNova AI • Enterprise Document Intelligence
        • Retrieval-Augmented Generation
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# END OF APPLICATION
# ============================================================