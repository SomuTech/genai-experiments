import streamlit as st
import tweepy
import requests
from bs4 import BeautifulSoup
import re
import random
import time
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# CONFIGURATION - Using python-dotenv
# =============================================================================

TWITTER_CONFIG = {
    'consumer_key': os.getenv('CONSUMER_KEY', 'YOUR_CONSUMER_KEY'),
    'consumer_secret': os.getenv('CONSUMER_SECRET', 'YOUR_CONSUMER_SECRET'),
    'access_token': os.getenv('ACCESS_TOKEN', 'YOUR_ACCESS_TOKEN'),
    'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET', 'YOUR_ACCESS_TOKEN_SECRET')
}

PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY', 'YOUR_PERPLEXITY_API_KEY')
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'

# =============================================================================
# CORE FUNCTIONS (unchanged)
# =============================================================================

@st.cache_resource
def setup_twitter_api():
    """Initialize Twitter API client"""
    try:
        if any(key.startswith('YOUR_') for key in TWITTER_CONFIG.values()):
            return None
            
        client = tweepy.Client(
            consumer_key=TWITTER_CONFIG['consumer_key'],
            consumer_secret=TWITTER_CONFIG['consumer_secret'],
            access_token=TWITTER_CONFIG['access_token'],
            access_token_secret=TWITTER_CONFIG['access_token_secret'],
            wait_on_rate_limit=True
        )
        
        # Test authentication
        me = client.get_me()
        return client
    except Exception as e:
        st.error(f"❌ Twitter API authentication failed: {e}")
        return None

def get_focused_news_for_topic(topic):
    """Get news headlines for a topic"""
    try:
        all_headlines = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        search_queries = [
            f"{topic} India latest news today",
            f"{topic} breaking news India", 
            f"{topic} update India 2025"
        ]
        
        progress_bar = st.progress(0)
        for i, query in enumerate(search_queries):
            try:
                url = f"https://news.google.com/search?q={quote_plus(query)}&hl=en-IN&gl=IN&ceid=IN:en"
                response = requests.get(url, headers=headers, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                articles = soup.find_all('article')[:3]
                for article in articles:
                    headline_elem = article.find(['h3', 'h4'])
                    if headline_elem:
                        headline = headline_elem.get_text().strip()
                        if headline and len(headline) > 20 and headline not in all_headlines:
                            all_headlines.append(headline)
                
                progress_bar.progress((i + 1) / len(search_queries))
                time.sleep(1)
                
            except Exception as e:
                st.warning(f"Error with query '{query}': {e}")
                continue
        
        progress_bar.empty()
        return all_headlines[:5]
        
    except Exception as e:
        st.error(f"❌ Error collecting news: {e}")
        return []

def generate_natural_human_tweet(topic, headlines, user_pov=None):
    """Generate natural human-like tweet"""
    try:
        if PERPLEXITY_API_KEY.startswith('YOUR_'):
            st.error("❌ Please set your Perplexity API key in the .env file")
            return None
            
        # Create news context
        news_context = ""
        if headlines:
            news_context = "Recent news:\n" + "\n".join([f"• {h}" for h in headlines[:3]])
        else:
            news_context = "No specific news context available"
        
        # Enhanced prompt for natural tweets
        prompt = f"""You are an actual human Twitter user from India who tweets naturally about current events. Write a single, authentic tweet about this topic.

TOPIC: {topic}

{news_context}

{f"YOUR PERSPECTIVE: {user_pov}" if user_pov else ""}

CRITICAL REQUIREMENTS - Make it sound COMPLETELY natural:
• Write exactly how a real person would tweet - spontaneous, casual, with natural reactions
• Use everyday language, not formal or corporate tone
• Include genuine human emotions and reactions (excitement, skepticism, curiosity, etc.)
• Maximum 280 characters
• Include 1-2 relevant hashtags ONLY if they flow naturally
• Avoid forced metaphors or trying too hard to be clever
• Sound like you're genuinely reacting to this news

EXAMPLES OF NATURAL HUMAN TWEETS:
"Wait, this is actually happening? About time tbh 🙌"
"Okay but who else thinks this sounds too good to be true? 🤔"
"Finally some good news today. Let's see if it actually works out"
"This is either genius or complete chaos. No in between lol"

Write ONE natural human tweet now:"""

        headers = {
            'Authorization': f'Bearer {PERPLEXITY_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "model": "sonar",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
            "temperature": 0.9
        }
        
        with st.spinner("🤖 Generating natural human tweet..."):
            response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=30)
            
        if response.status_code == 200:
            result = response.json()
            tweet = result['choices'][0]['message']['content'].strip()
            
            # Clean up the tweet
            tweet = re.sub(r'^(Tweet:|Here\'s a tweet:|Here\'s|Natural tweet:)', '', tweet, flags=re.IGNORECASE).strip()
            tweet = tweet.strip('"\'')
            
            # Ensure character limit
            if len(tweet) > 280:
                if '.' in tweet:
                    sentences = tweet.split('.')
                    tweet = sentences[0].strip()
                    if not tweet.endswith(('.', '!', '?')):
                        tweet += '.'
                else:
                    tweet = tweet[:277] + "..."
            
            return tweet
        else:
            st.error(f"❌ Perplexity API error: {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error generating tweet: {e}")
        return None

def post_tweet_to_twitter(client, tweet_content):
    """Post tweet to Twitter/X"""
    try:
        response = client.create_tweet(text=tweet_content)
        return True, response.data['id']
    except Exception as e:
        return False, str(e)

# =============================================================================
# MOBILE-FRIENDLY STREAMLIT UI WITH BUG FIXES
# =============================================================================

def main():
    st.set_page_config(
        page_title="GenAI Tweet Bot",
        page_icon="🐦",
        layout="wide",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': 'https://github.com/your-repo',
            'Report a bug': 'https://github.com/your-repo/issues',
            'About': "Generate natural, human-like tweets with AI!"
        }
    )
    
    # Custom CSS for mobile optimization
    st.markdown("""
    <style>
    /* Mobile-first responsive design */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    /* Make text inputs and buttons more mobile-friendly */
    .stTextInput input, .stTextArea textarea {
        font-size: 16px !important;
    }
    
    .stButton button {
        height: 3rem;
        font-size: 16px !important;
        border-radius: 8px;
    }
    
    /* Responsive columns for mobile */
    @media (max-width: 768px) {
        .stColumns {
            flex-direction: column;
        }
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
    
    /* Make metrics more compact on mobile */
    [data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #e1e5eb;
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
    }
    
    /* Improve chat bubble appearance */
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 12px;
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Compact header for mobile
    st.markdown("""
    <div style='text-align: center; padding: 1rem 0;'>
        <h1 style='margin: 0; font-size: 2rem;'>🐦 Tweet Bot</h1>
        <p style='margin: 0.5rem 0; color: #666; font-size: 0.9rem;'>Generate natural tweets with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API setup
    twitter_client = setup_twitter_api()
    

    # Initialize session state with proper null checks - BUG FIX
    if 'generated_tweet' not in st.session_state:
        st.session_state.generated_tweet = None
    if 'editable_tweet' not in st.session_state:
        st.session_state.editable_tweet = ""  # Initialize as empty string, not None
    if 'original_tweet' not in st.session_state:
        st.session_state.original_tweet = ""  # Initialize as empty string, not None
    if 'headlines' not in st.session_state:
        st.session_state.headlines = []
    if 'current_topic' not in st.session_state:
        st.session_state.current_topic = ""
    if 'tweet_posted' not in st.session_state:
        st.session_state.tweet_posted = False
    
    # Mobile-optimized input section
    st.markdown("### 💬 What's Trending?")
    
    # Chat-like interface with better mobile UX
    with st.container():
        st.markdown("""
        <div class='chat-message'>
            <strong>🤖 Bot:</strong> Hi! What topic would you like me to create a tweet about?
        </div>
        """, unsafe_allow_html=True)
        
        # Single column layout for mobile
        topic = st.text_input(
            "Enter topic or hashtag:",
            placeholder="AI Revolution, Stock Market, Python...",
            help="Enter any trending topic",
            key="topic_input",
            label_visibility="collapsed"
        )
        
        # Show follow-up only if topic is entered
        if topic:
            st.markdown(f"""
            <div class='chat-message'>
                <strong>🤖 Bot:</strong> Great topic: "<em>{topic}</em>"! Any personal thoughts?
            </div>
            """, unsafe_allow_html=True)
            
            user_pov = st.text_area(
                "Your viewpoint (optional):",
                placeholder="e.g., 'Finally!', 'Not sure about this', 'This reminds me...'",
                height=80,
                key="pov_input",
                label_visibility="collapsed"
            )
    
    # Large, mobile-friendly generate button
    if st.button("🚀 Generate Tweet", type="primary", use_container_width=True):
        if not topic.strip():
            st.warning("⚠️ Please enter a topic!")
        else:
            # Reset posting status when generating new tweet
            st.session_state.tweet_posted = False
            
            clean_topic = re.sub(r'^#', '', topic.strip())
            st.session_state.current_topic = clean_topic
            
            st.markdown(f"""
            <div class='chat-message'>
                <strong>🤖 Bot:</strong> Creating a natural tweet about "<em>{clean_topic}</em>"...
            </div>
            """, unsafe_allow_html=True)
            
            # Get news and generate tweet
            with st.status("📰 Working on your tweet...", expanded=True) as status:
                st.write("🔍 Finding latest news...")
                headlines = get_focused_news_for_topic(clean_topic)
                st.session_state.headlines = headlines
                
                if headlines:
                    st.write(f"✅ Found {len(headlines)} headlines")
                else:
                    st.write("⚠️ Using topic-based generation")
                
                st.write("🤖 Crafting natural tweet...")
                tweet = generate_natural_human_tweet(clean_topic, headlines, user_pov.strip() or None)
                
                if tweet:
                    # Store both original and editable versions - BUG FIX
                    st.session_state.generated_tweet = tweet
                    st.session_state.editable_tweet = tweet
                    st.session_state.original_tweet = tweet
                    status.update(label="✅ Tweet ready!", state="complete")
                else:
                    status.update(label="❌ Failed to generate", state="error")
    
    # Display and edit tweet section - BUG FIX: Check for both generated_tweet and editable_tweet
    if st.session_state.generated_tweet and st.session_state.editable_tweet:
        st.markdown("---")
        st.markdown("### 📝 Your Tweet")
        
        # Editable tweet with bug fix - ensure editable_tweet is never None
        current_editable = st.session_state.editable_tweet or ""
        edited_tweet = st.text_area(
            "Edit your tweet:",
            value=current_editable,
            height=120,
            max_chars=280,
            key="tweet_editor"
        )
        
        # Update editable version when user makes changes - BUG FIX
        if edited_tweet != st.session_state.editable_tweet:
            st.session_state.editable_tweet = edited_tweet or ""
        
        # Ensure editable_tweet is never None before getting length - BUG FIX
        editable_tweet_text = st.session_state.editable_tweet or ""
        char_count = len(editable_tweet_text)
        
        # Mobile-optimized metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Characters", f"{char_count}/280", delta=None)
        with col2:
            hashtags = editable_tweet_text.count('#')
            st.metric("Hashtags", hashtags)
        with col3:
            emojis = len([c for c in editable_tweet_text if ord(c) > 127])
            st.metric("Emojis", emojis)
        
        # Warning for character limit
        if char_count > 280:
            st.error("⚠️ Tweet is too long! Please shorten it.")
        elif char_count == 0:
            st.warning("⚠️ Tweet is empty!")
        
        # Action buttons - stacked vertically for mobile
        st.markdown("### 🎬 Actions")
        
        # Copy button - BUG FIX: Check for empty tweet
        if st.button("📋 Copy Tweet", use_container_width=True, disabled=(char_count > 280 or char_count == 0)):
            if editable_tweet_text:
                st.code(editable_tweet_text, language=None)
                st.success("✅ Copy the text above!")
            else:
                st.warning("⚠️ No tweet to copy!")
        
        # Post button with proper state management - BUG FIX
        if twitter_client:
            if not st.session_state.tweet_posted and char_count <= 280 and char_count > 0:
                if st.button("🐦 Post to Twitter", type="primary", use_container_width=True):
                    with st.spinner("Posting..."):
                        # Use the edited tweet, not the original - BUG FIX
                        success, result = post_tweet_to_twitter(twitter_client, editable_tweet_text)
                    
                    if success:
                        st.session_state.tweet_posted = True
                        st.success(f"🎉 Posted successfully!")
                        st.markdown(f"**Tweet ID:** `{result}`")
                        st.balloons()
                    else:
                        st.error(f"❌ Failed: {result}")
            elif st.session_state.tweet_posted:
                st.info("✅ Tweet already posted!")
            else:
                disabled_reason = "Tweet is too long!" if char_count > 280 else "Tweet is empty!" if char_count == 0 else "Twitter API not connected"
                st.button(f"🐦 {disabled_reason}", disabled=True, use_container_width=True)
        else:
            st.button("🐦 Twitter API not connected", disabled=True, use_container_width=True)
        
        # Generate new tweet button
        if st.button("🔄 Generate New Tweet", use_container_width=True):
            with st.spinner("Creating new tweet..."):
                new_tweet = generate_natural_human_tweet(
                    st.session_state.current_topic, 
                    st.session_state.headlines, 
                    user_pov.strip() or None if 'user_pov' in locals() else None
                )
                if new_tweet:
                    st.session_state.generated_tweet = new_tweet
                    st.session_state.editable_tweet = new_tweet
                    st.session_state.original_tweet = new_tweet
                    st.session_state.tweet_posted = False  # Reset posting status
                    st.rerun()
        
        # Show changes indicator - BUG FIX: Properly compare strings
        original_text = st.session_state.original_tweet or ""
        if editable_tweet_text != original_text:
            st.info("✏️ You've edited this tweet")
        
        # News headlines (collapsible for mobile)
        if st.session_state.headlines:
            with st.expander("📰 Source Headlines", expanded=False):
                for i, headline in enumerate(st.session_state.headlines, 1):
                    st.markdown(f"{i}. {headline}")
    
    # Show message when no tweet is generated yet
    elif not st.session_state.generated_tweet:
        st.markdown("""
        <div style='text-align: center; padding: 2rem; color: #666;'>
            <p>👆 Enter a trending topic above to get started!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Compact footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 1rem; color: #666; font-size: 0.8rem;'>
        Built with ❤️ • Streamlit + Perplexity AI + Twitter API
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
