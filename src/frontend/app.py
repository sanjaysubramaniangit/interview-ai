# frontend/app.py
import streamlit as st
import requests

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Interview Prep Assistant", page_icon="🎯", layout="wide")
st.title("🎯 AI Interview Prep Assistant")

with st.sidebar:
    st.header("Settings")
    BACKEND = st.text_input("Backend URL", value=BACKEND)
    st.caption("Run the backend with: uvicorn backend.main:app --reload --port 8000")

st.subheader("Step 1: Upload Job Description (PDF) for context (RAG)")
pdf = st.file_uploader("Pick a PDF", type=["pdf"])
if pdf and st.button("Upload & Index"):
    r = requests.post(f"{BACKEND}/upload_pdf", files={"file": (pdf.name, pdf.getvalue(), "application/pdf")})
    if r.ok:
        st.success(f"Ingested. Chunks: {r.json()['chunks']}")
    else:
        st.error(r.text)

st.subheader("Step 2: Generate Questions")
col1, col2, col3 = st.columns(3)
with col1:
    role = st.text_input("Role", value="Senior Python Developer")
with col2:
    experience = st.text_input("Experience", value="5 years")
with col3:
    n_questions = st.slider("How many?", 3, 10, 5)

topics = st.text_input("Topics (comma separated)", value="data structures, algorithms, system design")
if st.button("Generate Questions"):
    payload = {
        "role": role,
        "experience": experience,
        "topics": [t.strip() for t in topics.split(",") if t.strip()],
        "n_questions": int(n_questions),
    }
    r = requests.post(f"{BACKEND}/generate_questions", json=payload)
    if r.ok:
        st.session_state["questions"] = r.json()["questions"]
        st.success(f"Generated {len(st.session_state['questions'])} questions.")
    else:
        st.error(r.text)

qs = st.session_state.get("questions", [])
if qs:
    st.subheader("Step 3: Answer & Get Feedback")
    for i, q in enumerate(qs, start=1):
        st.markdown(f"**Q{i}. {q}**")
        ans = st.text_area(f"Your answer to Q{i}", key=f"ans_{i}", height=160)
        if st.button(f"Get Feedback for Q{i}", key=f"fb_{i}"):
            r = requests.post(f"{BACKEND}/feedback", json={"question": q, "answer": ans, "role": role, "experience": experience})
            if r.ok:
                fb = r.json()
                st.metric("Score (0–10)", fb.get("score", 0))
                st.write("**Verdict:**", fb.get("verdict", ""))
                st.write("**Strengths:**")
                for s in fb.get("strengths", []):
                    st.write(f"- {s}")
                st.write("**Improvements:**")
                for it in fb.get("improvements", []):
                    st.write(f"- {it}")
                with st.expander("Suggested answer"):
                    st.write(fb.get("suggested_answer", ""))
            else:
                st.error(r.text)
