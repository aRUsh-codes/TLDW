import os
import requests
from youtube_transcript_api import YouTubeTranscriptApi,TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from urllib.parse import urlparse, parse_qs
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
from bs4 import BeautifulSoup


load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

prompt = """You are a professional youtube video summarizer with 5+ years of experience in 
analyzing videos, type of content, transcripts, captions, context clues from the title and the transcript. 
Your task will be to take the entire transcript text and summarize the entire video and provide
the important summary in points within 250 words. Here is the transcript text:"""

def extract_videoid(url):
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ('www.youtube.com','youtube.com'):
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
    return None


def extract_transcript_details(video_url):
    try:
        video_id = extract_videoid(video_url)
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id, languages = ("en", "es", "fr", "de", "it", "pt", "nl", "ru", "zh-Hans", "zh-Hant", "ar", "hi", "ja", "ko", "tr", "bn", "ur", "pa", "el", "sv", "pl", "fi", "da", "no", "hu", "cs", "ro", "he", "th", "vi", "id", "ms", "tl", "ta", "te", "mr", "gu"
 ))
        transcript = " ".join([item['text'] for item in transcript_text])
        return transcript
    except Exception as e:
        st.error(e)
        

def generate_gemini(transcript_text,prompt):
    model = genai.GenerativeModel("gemini-1.5-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

st.markdown("""
    <style>
        .title {
            font-size: 96px;
            font-weight: bold;
            text-align: center;
        }
        .subtitle {
            font-size: 20px;
            text-align: center;
            color: gray;
        }
    </style>

    <div class="title">📹 T L D W</div>
    <div class="subtitle">         Too long didn't watch: A Youtube Video Summarizer</div>
""", unsafe_allow_html=True)
youtube_link = st.text_input("Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=VIDEO_ID")

if youtube_link:
    video_id = extract_videoid(youtube_link)
    if video_id:
        response = requests.get(youtube_link)
        soup = BeautifulSoup(response.text,"html.parser")
        title_page = soup.find('meta',{"name":'title'})
        title = title_page['content']
        st.subheader(title)
        st.image(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg", use_container_width=True)
    else:
        st.error("Invalid YouTube URL. Please enter a valid URL.")    

if st.button("Generate Summary"):
    transcript_text = extract_transcript_details(youtube_link)
    if transcript_text:
        with st.spinner("Generating summary..."):
            summary = generate_gemini(transcript_text, prompt)
            st.markdown("📃 Here you go! 🎉")
            st.subheader("Summary")
            st.write(summary)
            st.success("Done!")