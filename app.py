import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import time

st.set_page_config(page_title="🌟 Sentiment Buddy", page_icon="🧠", layout="wide")

@st.cache_resource
def load_analyzer():
    return SentimentIntensityAnalyzer()

analyzer = load_analyzer()

st.markdown("""
<style>
    .positive { color: #2ecc71; font-size: 22px; font-weight: bold; }
    .negative { color: #e74c3c; font-size: 22px; font-weight: bold; }
    .neutral { color: #95a5a6; font-size: 22px; font-weight: bold; }

    .main-header {
        font-size: 36px;
        color: #3498db;
        text-align: center;
        margin-bottom: 20px;
    }

    .stButton>button {
        background-color: #3498db;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 8px;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        background-color: #2980b9;
        transform: scale(1.02);
    }

    .stTextArea>textarea {
        border-radius: 8px;
        padding: 12px !important;
    }

    .card {
        background-color: black;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

if 'input_text' not in st.session_state:
    st.session_state.input_text = ""
if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

st.markdown('<div class="main-header">🌟 Meet Your Sentiment Buddy</div>', unsafe_allow_html=True)
st.caption("Let’s figure out how your text *feels*!")

def analyze_sentiment(text):
    vader_scores = analyzer.polarity_scores(text)
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    compound = vader_scores['compound']
    adjusted_score = (compound + polarity) / 2

    pos = vader_scores['pos']
    neg = vader_scores['neg']
    neu = vader_scores['neu']

    if pos > 0.4 and neg > 0.4:
        mood = "😵 Mixed Emotions"
        sentiment_class = "neutral"
    elif adjusted_score >= 0.6:
        mood = "🤩 Extremely Positive"
        sentiment_class = "positive"
    elif adjusted_score >= 0.3:
        mood = "😍 Very Positive"
        sentiment_class = "positive"
    elif adjusted_score >= 0.1:
        mood = "🙂 Slightly Positive"
        sentiment_class = "positive"
    elif adjusted_score <= -0.6:
        mood = "💢 Extremely Negative"
        sentiment_class = "negative"
    elif adjusted_score <= -0.3:
        mood = "😡 Very Negative"
        sentiment_class = "negative"
    elif adjusted_score <= -0.1:
        mood = "😕 Slightly Negative"
        sentiment_class = "negative"
    else:
        mood = "😐 Neutral"
        sentiment_class = "neutral"


    keywords = [word for word in text.split() if analyzer.polarity_scores(word)['compound'] > 0.3 or analyzer.polarity_scores(word)['compound'] < -0.3]
    return mood, adjusted_score, sentiment_class, vader_scores, keywords

with st.form("sentiment_form"):
    user_input = st.text_area(
        "What's on your mind?",
        height=150,
        value=st.session_state.input_text,
        placeholder="Tell me something like 'I'm pumped about this!' or 'Ugh, that sucked.'"
    )
    analyze_btn = st.form_submit_button("Analyze it 🚀")

st.sidebar.title("Try These 👇")
examples = [
    "I'm absolutely thrilled with the results!",
    "This is the worst experience I've ever had.",
    "The product is okay, nothing special.",
    "I'm slightly disappointed but it's not terrible.",
    "The weather is neither good nor bad today.",
    "It's an average day, nothing exciting."
]

for example in examples:
    if st.sidebar.button(example, use_container_width=True):
        st.session_state.input_text = example
        st.rerun()


if analyze_btn or st.session_state.input_text:
    if user_input.strip():
        with st.spinner("Crunching the emotional vibes..."):
            time.sleep(0.5)
            mood, score, sentiment_class, vader_scores, keywords = analyze_sentiment(user_input)
            st.session_state.last_analysis = {
                "text": user_input,
                "mood": mood,
                "score": score,
                "class": sentiment_class,
                "keywords": keywords
            }

            st.markdown(f"""
            <div class="card">
                <h3>Sentiment Breakdown</h3>
                <p>Your vibe: <span class="{sentiment_class}">{mood}</span></p>
                <p>Confidence Score: <strong>{score:.3f}</strong> (from -1 to +1)</p>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Score Details & Emotion Words"):
                cols = st.columns(3)
                with cols[0]:
                    st.metric("Positive 💚", f"{vader_scores['pos']:.3f}")
                with cols[1]:
                    st.metric("Neutral 😐", f"{vader_scores['neu']:.3f}")
                with cols[2]:
                    st.metric("Negative ❤️‍🔥", f"{vader_scores['neg']:.3f}")
                st.progress((score + 1) / 2)
                if keywords:
                    st.markdown("**Words impacting sentiment:**")
                    st.code(", ".join(keywords))
                else:
                    st.write("No standout sentiment words detected.")

            if sentiment_class == "positive":
                st.balloons()
                st.success("Woo! That was some positive energy. Keep it up! 💪")
            elif sentiment_class == "negative":
                st.snow()
                st.error("Yikes, sounds rough. Want to talk about it? 🫂")
            else:
                st.info("Totally balanced vibe. Not good, not bad. Just neutral 🧘‍♂️")
    else:
        st.warning("Give me some words first!")

st.divider()
