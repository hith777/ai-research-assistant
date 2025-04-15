import streamlit as st
import os
from domain.paper import Paper
from services.summarizer import SummarizerService

st.set_page_config(page_title="AI Research Assistant", layout="wide")
st.title("🧠 AI Research Assistant (GPT-3.5)")

st.sidebar.header("Choose Task")
task = st.sidebar.selectbox("Select a mode", ["Summarize Paper", "Compare Papers"])

st.sidebar.markdown("---")
style = st.sidebar.selectbox("Summary Style", ["layman", "technical", "default"])

# --- Summarize Single Paper ---
if task == "Summarize Paper":
    uploaded_file = st.file_uploader("Upload a research paper (PDF)", type=["pdf"])

    if uploaded_file:
        file_path = os.path.join("tmp", uploaded_file.name)
        os.makedirs("tmp", exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success("📄 File uploaded successfully.")

        if st.button("Summarize"):
            with st.spinner("Generating summary..."):
                paper = Paper.from_pdf(file_path)
                chunks = paper.chunk_text()
                result = SummarizerService.summarize_paper(chunks, style=style)

                st.subheader("📑 Summary")
                st.write(result["final_summary"])

                st.subheader("📊 Token Usage")
                st.json(result["total_usage"])

                st.metric("💰 Estimated Cost", f"${result['cost']:.6f}")

# --- Compare Two Papers ---
elif task == "Compare Papers":
    file1 = st.file_uploader("Upload Paper 1", type=["pdf"], key="file1")
    file2 = st.file_uploader("Upload Paper 2", type=["pdf"], key="file2")

    if file1 and file2:
        path1 = os.path.join("tmp", file1.name)
        path2 = os.path.join("tmp", file2.name)

        os.makedirs("tmp", exist_ok=True)

        with open(path1, "wb") as f1, open(path2, "wb") as f2:
            f1.write(file1.read())
            f2.write(file2.read())

        st.success("✅ Both files uploaded.")

        if st.button("Compare Papers"):
            with st.spinner("Analyzing and comparing..."):
                result = SummarizerService.compare_papers(path1, path2, style=style)

                st.subheader("📊 Comparison Summary")
                st.write(result["comparison"])

                st.subheader("📊 Token Usage")
                st.json(result["total_usage"])

                st.metric("💰 Estimated Cost", f"${result['cost']:.6f}")
