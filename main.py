import streamlit as st
import PyPDF2, io, requests, json

OLLAMA_URL = "http://localhost:11434/api/generate"  # Ollama REST API

st.set_page_config(page_title="AI Resume Critiquer", page_icon="📝")
st.title("AI Resume Critiquer")
st.markdown("Upload your resume and get AI-powered feedback tailored to your needs!")

# Sidebar settings with improved explanations
st.sidebar.title("Analysis Settings")

# Add explanatory text at the top
st.sidebar.markdown("""
## Guide
Adjust these parameters to customize your resume analysis.
""")

# Temperature with better explanation
st.sidebar.markdown("### Creativity Level")
st.sidebar.markdown("""
Controls how creative vs. predictable the feedback will be:
- **0.1-0.3**: Very focused, consistent feedback
- **0.4-0.7**: Balanced creativity and consistency
- **0.8-1.0**: More varied and creative suggestions
""")
temperature = st.sidebar.slider("", 0.1, 1.0, 0.7)

# Response length with explanation
st.sidebar.markdown("### Response Length")
st.sidebar.markdown("""
How detailed should the analysis be? Longer responses take more time.
- **200-500**: Brief overview
- **500-1000**: Standard detailed analysis
- **1000+**: Comprehensive breakdown
""")
max_new_tokens = st.sidebar.slider("", 200, 1500, 800)

# Analysis depth with explanation
st.sidebar.markdown("### Analysis Depth")
st.sidebar.markdown("""
Choose how thorough the AI should be in its analysis:
- **Standard**: Quick overview of key points  
- **Detailed**: In-depth feedback with concrete examples
- **Comprehensive**: Exhaustive analysis with rewrites and specific improvements""")
analysis_depth = st.sidebar.selectbox("", 
    ["Standard", "Detailed", "Comprehensive"])

# Safe mode with explanation
st.sidebar.markdown("### Safe Mode")
st.sidebar.markdown("""
Enable this if you're experiencing errors or unstable results.
Uses more conservative settings for improved reliability.
""")
safe_mode = st.sidebar.checkbox("Enable Safe Mode", value=False)

uploaded_file = st.file_uploader("Upload file (PDF or TXT)", type=["pdf", "txt"])

# Replace single-line text input with a text area for job descriptions
st.markdown("### Job Description (Optional)")
job_role = st.text_area("Paste the job description or target role details for more tailored feedback:", 
                       placeholder="Paste job description here...", 
                       height=150)

analyze = st.button("Analyze Resume")

def extract_text_from_pdf(pdf_file):
    text = []
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        t = page.extract_text() or ""
        text.append(t)
    return "\n".join(text)

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        return extract_text_from_pdf(io.BytesIO(uploaded_file.read()))
    return uploaded_file.read().decode("utf-8", errors="ignore")

def build_prompt(resume_text: str, role: str, depth: str) -> str:
    detail = {
        "Standard": "Provide a concise analysis highlighting key strengths and weaknesses.",
        "Detailed": "Provide a thorough analysis with examples from the resume and concrete improvements.",
        "Comprehensive": "Provide an in-depth analysis with examples, rewrites, metrics to add, and prioritization."
    }[depth]

    return f"""You are an expert technical recruiter and career coach.
Analyze the resume below and provide {depth.lower()} feedback.

Focus on:
1) Content clarity and impact
2) Skills presentation and relevance
3) Experience descriptions and achievements (quantify where possible)
4) Formatting and structure
5) Specific improvements for {role if role else "a general job application"}

{detail}

Return a clear, structured critique with bullet points and short actionable examples.

[RESUME]
{resume_text}
"""

def generate_with_ollama(prompt: str, temperature: float, max_tokens: int):
    # Stream tokens so the user sees progress
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "options": {
            "temperature": max(0.2, float(temperature)) if not safe_mode else 0.2,
            "num_predict": int(max_tokens),
            "top_p": 0.95,
            "top_k": 50,
            "repeat_penalty": 1.1
        },
        "stream": True
    }
    with requests.post(OLLAMA_URL, json=payload, stream=True, timeout=600) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if not line:
                continue
            data = json.loads(line)
            if "response" in data:
                yield data["response"]
            if data.get("done"):
                break

if analyze and uploaded_file:
    try:
        resume_text = extract_text_from_file(uploaded_file)
        if not resume_text.strip():
            st.error("The uploaded file is empty or unreadable.")
            st.stop()

        prompt = build_prompt(resume_text, job_role, analysis_depth)

        st.subheader("Analysis:")
        out = st.empty()
        buf = []
        with st.spinner("Thinking…"):
            for token in generate_with_ollama(prompt, temperature, max_new_tokens):
                buf.append(token)
                out.markdown("".join(buf))

        final_text = "".join(buf)
        st.download_button("Download Analysis", data=final_text,
                           file_name="resume_analysis.txt", mime="text/plain")
        st.info("💡 Tip: Highlight impact with metrics (%, $, time saved).")

    except requests.exceptions.ConnectionError:
        st.error("Couldn't connect to Ollama. Is it running? Try `ollama serve` or open the app.")
    except Exception as e:
        st.exception(e)