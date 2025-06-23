# main.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth
import requests
import json
import time
from datetime import datetime
import pandas as pd
from typing import Dict, List, Optional
import uuid
import plotly.express as px
import plotly.graph_objects as go
import re

# Page configuration
st.set_page_config(
    page_title="Academic Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern chat UI
def load_css():
    st.markdown("""
    <style>
    /* Main theme colors - Sky Blue */
    :root {
        --primary-color: #87CEEB;
        --secondary-color: #4682B4;
        --accent-color: #1E90FF;
        --background-color: #F0F8FF;
        --text-color: #2F4F4F;
        --chat-bg: #FFFFFF;
        --user-msg-bg: #E6F3FF;
        --bot-msg-bg: #F8F9FA;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main-container {
        background: linear-gradient(135deg, #F0F8FF 0%, #E6F3FF 100%);
        min-height: 100vh;
        padding: 0;
    }
    
    /* Header styling */
    .chat-header {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        padding: 1rem 2rem;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .chat-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .chat-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        margin: 0;
        margin-top: 5px;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 0 1rem;
    }
    
    /* Message styling */
    .message-container {
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }
    
    .user-message {
        background: var(--user-msg-bg);
        border: 1px solid var(--primary-color);
        border-radius: 18px 18px 5px 18px;
        padding: 12px 16px;
        margin-left: 20%;
        position: relative;
    }
    
    .bot-message {
        background: var(--bot-msg-bg);
        border: 1px solid #E0E0E0;
        border-radius: 18px 18px 18px 5px;
        padding: 12px 16px;
        margin-right: 20%;
        position: relative;
    }
    
    .message-time {
        font-size: 0.75rem;
        color: #888;
        margin-top: 5px;
        text-align: right;
    }
    
    .bot-message .message-time {
        text-align: left;
    }
    
    /* Typing indicator */
    .typing-indicator {
        background: var(--bot-msg-bg);
        border: 1px solid #E0E0E0;
        border-radius: 18px 18px 18px 5px;
        padding: 12px 16px;
        margin-right: 20%;
        margin-bottom: 1rem;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: var(--secondary-color);
        animation: typingDot 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typingDot {
        0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid var(--primary-color);
        padding: 12px 20px;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--secondary-color);
        box-shadow: 0 0 0 2px rgba(70, 130, 180, 0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, var(--background-color), white);
    }
    
    /* Pagination */
    .pagination-container {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 10px;
        margin: 20px 0;
    }
    
    .pagination-btn {
        background: var(--primary-color);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .pagination-btn:hover {
        background: var(--secondary-color);
    }
    
    .pagination-btn:disabled {
        background: #ccc;
        cursor: not-allowed;
    }
    </style>
    """, unsafe_allow_html=True)

class DataVisualizationManager:
    def __init__(self):
        pass
    
    def detect_data_request(self, user_input: str, bot_response: str) -> Dict:
        """Detect if user is asking for data visualization"""
        viz_keywords = [
            'grafik', 'chart', 'plot', 'visualisasi', 'tabel', 'table',
            'diagram', 'statistik', 'data', 'perbandingan', 'trend'
        ]
        
        user_lower = user_input.lower()
        response_lower = bot_response.lower()
        
        # Check if user asking for visualization
        needs_viz = any(keyword in user_lower for keyword in viz_keywords)
        
        # Check if response contains structured data
        has_numbers = bool(re.search(r'\d+', bot_response))
        has_lists = '1.' in bot_response or '2.' in bot_response or '-' in bot_response
        
        return {
            "needs_visualization": needs_viz,
            "has_data": has_numbers and has_lists,
            "type": self._determine_viz_type(user_input, bot_response)
        }
    
    def _determine_viz_type(self, user_input: str, bot_response: str) -> str:
        """Determine what type of visualization to create"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['perbandingan', 'compare', 'vs']):
            return 'comparison'
        elif any(word in user_lower for word in ['trend', 'waktu', 'time', 'tahun']):
            return 'timeline'
        elif any(word in user_lower for word in ['distribusi', 'percentage', 'persen']):
            return 'pie'
        elif any(word in user_lower for word in ['tabel', 'table', 'list']):
            return 'table'
        else:
            return 'bar'
    
    def extract_data_from_response(self, response: str) -> List[Dict]:
        """Extract structured data from AI response"""
        lines = response.split('\n')
        data = []
        
        for line in lines:
            # Look for patterns like "1. Item: Value" or "- Item: Value"
            pattern = r'(?:\d+\.\s*|-\s*)([^:]+):\s*(.+)'
            match = re.search(pattern, line)
            
            if match:
                label = match.group(1).strip()
                value_text = match.group(2).strip()
                
                # Try to extract numbers
                number_match = re.search(r'(\d+(?:\.\d+)?)', value_text)
                if number_match:
                    value = float(number_match.group(1))
                    data.append({"label": label, "value": value, "description": value_text})
        
        return data
    
    def create_visualization(self, data: List[Dict], viz_type: str, title: str = "Data Visualization"):
        """Create visualization based on data and type"""
        if not data:
            return None
        
        df = pd.DataFrame(data)
        
        if viz_type == 'bar':
            fig = px.bar(df, x='label', y='value', title=title,
                        color='value', color_continuous_scale='Blues')
            fig.update_layout(xaxis_tickangle=-45)
            
        elif viz_type == 'pie':
            fig = px.pie(df, values='value', names='label', title=title)
            
        elif viz_type == 'comparison':
            fig = px.bar(df, x='label', y='value', title=title,
                        color='label', color_discrete_sequence=px.colors.qualitative.Set3)
            
        elif viz_type == 'timeline':
            fig = px.line(df, x='label', y='value', title=title,
                         markers=True, line_shape='spline')
            
        else:  # default bar
            fig = px.bar(df, x='label', y='value', title=title)
        
        # Customize layout
        fig.update_layout(
            template='plotly_white',
            height=400,
            margin=dict(t=50, l=50, r=50, b=50)
        )
        
        return fig
    
    def create_table(self, data: List[Dict], title: str = "Data Table"):
        """Create a formatted table from data"""
        if not data:
            return None
        
        df = pd.DataFrame(data)
        return df

# Firebase initialization
@st.cache_resource
def init_firebase():
    try:
        # Try to get existing app
        app = firebase_admin.get_app()
    except ValueError:
        # Initialize new app
        try:
            if st.secrets.get("firebase"):
                # For Streamlit Cloud deployment
                firebase_config = dict(st.secrets["firebase"])
                
                # Fix private key formatting
                if "private_key" in firebase_config:
                    private_key = firebase_config["private_key"]
                    # Replace literal \n with actual newlines
                    if "\\n" in private_key:
                        firebase_config["private_key"] = private_key.replace("\\n", "\n")
                
                cred = credentials.Certificate(firebase_config)
            else:
                # For local development - check if file exists
                import os
                if os.path.exists("firebase-credentials.json"):
                    cred = credentials.Certificate("firebase-credentials.json")
                else:
                    st.error("❌ Firebase credentials file not found!")
                    st.info("Please create 'firebase-credentials.json' file with your Firebase service account key.")
                    st.stop()
            
            app = firebase_admin.initialize_app(cred)
            
        except Exception as e:
            st.error(f"❌ Firebase initialization failed: {str(e)}")
            st.info("🔧 **Troubleshooting Steps:**")
            st.info("1. Check if your Firebase service account key is valid")
            st.info("2. Ensure private_key format is correct (with proper newlines)")
            st.info("3. Verify project_id and other credentials")
            st.info("4. Make sure Firestore is enabled in your Firebase project")
            
            # Show debug information
            with st.expander("🐛 Debug Information"):
                if st.secrets.get("firebase"):
                    config_keys = list(st.secrets["firebase"].keys())
                    st.write("Available config keys:", config_keys)
                    if "private_key" in st.secrets["firebase"]:
                        pk = st.secrets["firebase"]["private_key"]
                        st.write("Private key starts with:", pk[:50] + "...")
                        st.write("Contains \\n?", "\\n" in pk)
                        st.write("Contains newlines?", "\n" in pk)
                else:
                    st.write("No Firebase secrets found in Streamlit configuration")
            
            st.stop()
    
    return firestore.client()

# Authentication functions
class AuthManager:
    def __init__(self):
        self.db = init_firebase()
    
    def create_user_account(self, email: str, password: str, display_name: str):
        """Create a new user account"""
        try:
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )
            return {"success": True, "user_id": user.uid}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_user_credentials(self, email: str, password: str):
        """Verify user credentials (simplified for demo)"""
        try:
            # In real implementation, you'd verify password hash
            # For now, we'll just check if user exists
            user = auth.get_user_by_email(email)
            return {"success": True, "user_id": user.uid, "display_name": user.display_name}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_admin(self, email: str) -> bool:
        """Check if user is admin"""
        # Define admin emails here or in database
        admin_emails = ["rizkyanandaalamsyahdly@gmail.com", "administrator@akademik.com"]
        return email.lower() in admin_emails

def generate_anonymous_user_id():
    """Generate anonymous user ID"""
    if "anonymous_user_id" not in st.session_state:
        st.session_state.anonymous_user_id = f"anon_{uuid.uuid4().hex[:8]}"
    return st.session_state.anonymous_user_id

# Chat functions
class ChatManager:
    def __init__(self):
        self.db = init_firebase()
        self.api_url = st.secrets.get("ngrok_api_url", "YOUR_NGROK_URL_HERE")
        self.viz_manager = DataVisualizationManager()
    
    def process_response_with_visualization(self, user_input: str, bot_response: str) -> Dict:
        """Process response and create visualization if needed"""
        viz_info = self.viz_manager.detect_data_request(user_input, bot_response)
        
        result = {
            "response": bot_response,
            "visualization": None,
            "table": None,
            "viz_type": None
        }
        
        if viz_info["needs_visualization"] and viz_info["has_data"]:
            data = self.viz_manager.extract_data_from_response(bot_response)
            
            if data:
                if viz_info["type"] == 'table':
                    result["table"] = self.viz_manager.create_table(data, "Data Table")
                else:
                    result["visualization"] = self.viz_manager.create_visualization(
                        data, viz_info["type"], "Academic Data Visualization"
                    )
                    result["viz_type"] = viz_info["type"]
        
        return result
    
    def send_message_to_api(self, prompt: str) -> Dict:
        """Send message to ngrok API"""
        try:
            headers = {"Content-Type": "application/json"}
            payload = {"prompt": prompt}
            
            response = requests.post(f"{self.api_url}/generate", 
                                   json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {"success": True, "response": data.get("response", "No response received")}
            else:
                return {"success": False, "error": f"API Error: {response.status_code}"}
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Connection error: {str(e)}"}
    
    def save_conversation(self, user_id: str, user_input: str, bot_response: str):
        """Save conversation to Firestore"""
        try:
            doc_ref = self.db.collection("conversations").document(user_id).collection("messages").document()
            doc_ref.set({
                "input": user_input,
                "response": bot_response,
                "timestamp": datetime.now(),
                "is_anonymous": user_id.startswith("anon_")  # Track if user is anonymous
            })
            return True
        except Exception as e:
            st.error(f"Error saving conversation: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, page: int = 1, page_size: int = 10) -> Dict:
        """Get paginated conversation history"""
        try:
            query = (self.db.collection("conversations")
                    .document(user_id)
                    .collection("messages")
                    .order_by("timestamp", direction=firestore.Query.DESCENDING)
                    .limit(page_size)
                    .offset((page - 1) * page_size))
            
            docs = query.stream()
            messages = []
            
            for doc in docs:
                data = doc.to_dict()
                messages.append({
                    "id": doc.id,
                    "input": data.get("input", ""),
                    "response": data.get("response", ""),
                    "timestamp": data.get("timestamp")
                })
            
            # Get total count for pagination
            total_docs = len(list(self.db.collection("conversations")
                                .document(user_id)
                                .collection("messages").stream()))
            
            return {
                "success": True,
                "messages": messages,
                "total": total_docs,
                "page": page,
                "total_pages": (total_docs + page_size - 1) // page_size
            }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_all_conversations(self) -> List[Dict]:
        """Get all conversations for admin panel"""
        try:
            conversations = []
            users_ref = self.db.collection("conversations")
            
            # Gunakan list_documents() untuk mendapatkan semua document references
            user_doc_refs = users_ref.list_documents()
            
            for user_doc_ref in user_doc_refs:
                user_id = user_doc_ref.id
                
                # Langsung akses subcollection messages tanpa cek parent document
                messages_ref = user_doc_ref.collection("messages")
                
                # Ambil semua messages
                messages = list(messages_ref.stream())
                
                for msg_doc in messages:
                    data = msg_doc.to_dict()
                    conversations.append({
                        "user_id": user_id,
                        "message_id": msg_doc.id,
                        "input": data.get("input", ""),
                        "response": data.get("response", ""),
                        "timestamp": data.get("timestamp")
                    })
            
            return conversations
        
        except Exception as e:
            st.error(f"Error fetching conversations: {e}")
            return []

# UI Components
def render_chat_header():
    """Render chat header"""
    st.markdown("""
    <div class="chat-header">
        <div class="chat-title">
            <img src="https://hmpstrplpolmed.com/assets/img/logo/hmpstrpl.webp" 
                 width="60" height="auto" alt="Logo">
            🎓 Academic Chatbot
        </div>
        <div class="chat-subtitle">
            Powered by Llama 3.1 Fine-tuned Model | Tanyakan Informasi Seputar TRPL | Informasi Dosen, Mahasiswa, RPS, Seputar Magang, Skripsi dan Lainnya
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_typing_indicator():
    """Render typing indicator"""
    st.markdown("""
    <div class="typing-indicator">
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <span style="margin-left: 10px; color: #666;">AI sedang mengetik...</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_message_with_viz(message: str, is_user: bool, timestamp: datetime = None, 
                           visualization=None, table=None):
    """Render a chat message with optional visualization"""
    if timestamp is None:
        timestamp = datetime.now()
    
    message_class = "user-message" if is_user else "bot-message"
    time_str = timestamp.strftime("%H:%M")
    
    # Render text message
    st.markdown(f"""
    <div class="message-container">
        <div class="{message_class}">
            <div>{message}</div>
            <div class="message-time">{time_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Render visualization if available
    if not is_user:  # Only for bot messages
        if visualization is not None:
            st.plotly_chart(visualization, use_container_width=True)
        
        if table is not None:
            st.subheader("📊 Data Table")
            st.dataframe(table, use_container_width=True)

def render_pagination(current_page: int, total_pages: int, key_prefix: str = ""):
    """Render pagination controls"""
    if total_pages <= 1:
        return current_page
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⬅️ First", key=f"{key_prefix}_first", disabled=current_page <= 1):
            return 1
    
    with col2:
        if st.button("◀️ Prev", key=f"{key_prefix}_prev", disabled=current_page <= 1):
            return current_page - 1
    
    with col3:
        st.markdown(f"<div style='text-align: center; padding: 10px;'>Page {current_page} of {total_pages}</div>", 
                   unsafe_allow_html=True)
    
    with col4:
        if st.button("Next ▶️", key=f"{key_prefix}_next", disabled=current_page >= total_pages):
            return current_page + 1
    
    with col5:
        if st.button("Last ➡️", key=f"{key_prefix}_last", disabled=current_page >= total_pages):
            return total_pages
    
    return current_page

def render_sidebar():
    """Render sidebar with login/logout options"""
    with st.sidebar:
        if st.session_state.get("user_id"):
            # Logged in user
            st.markdown(f"### Welcome, {st.session_state.user_name}! 👋")
            st.success("✅ Logged in")
        else:
            # Anonymous user
            st.markdown("### 👤 Anonymous User")
            st.info("💡 Login to save your chat history!")
            
            if st.button("🔑 Login", use_container_width=True):
                st.session_state.show_login = True
                st.rerun()
        
        if st.button("🔄 New Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.show_history = False
            st.rerun()
        
        # Chat History - only for logged in users
        if st.session_state.get("user_id"):
            if st.button("📚 Chat History", use_container_width=True):
                st.session_state.show_history = not st.session_state.get("show_history", False)
                st.rerun()
        else:
            if st.button("📚 Chat History", use_container_width=True, disabled=True):
                pass
            st.caption("Login required to view history")
        
        # Admin Panel - only for logged in admins
        if st.session_state.get("is_admin", False):
            if st.button("👨‍💼 Admin Panel", use_container_width=True):
                st.session_state.current_page_name = "admin"
                st.rerun()
        
        # Logout button - only for logged in users
        if st.session_state.get("user_id"):
            if st.button("🚪 Logout", use_container_width=True):
                # Keep anonymous ID but clear login data
                anon_id = st.session_state.get("anonymous_user_id")
                for key in list(st.session_state.keys()):
                    if key != "anonymous_user_id":
                        del st.session_state[key]
                if anon_id:
                    st.session_state.anonymous_user_id = anon_id
                st.rerun()

# Main pages
# def login_page():
#     """Login/Register page"""
#     st.markdown("<h1 style='text-align: center; color: #4682B4;'>🎓 Academic Chatbot</h1>", unsafe_allow_html=True)
#     st.markdown("<p style='text-align: center; color: #666;'>Sign in to start chatting with our AI assistant</p>", unsafe_allow_html=True)
    
#     auth_manager = AuthManager()
    
#     tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
#     with tab1:
#         with st.form("login_form"):
#             email = st.text_input("Email", placeholder="Enter your email")
#             password = st.text_input("Password", type="password", placeholder="Enter your password")
            
#             if st.form_submit_button("Sign In", use_container_width=True):
#                 if email and password:
#                     result = auth_manager.verify_user_credentials(email, password)
#                     if result["success"]:
#                         st.session_state.user_id = result["user_id"]
#                         st.session_state.user_email = email
#                         st.session_state.user_name = result.get("display_name", email.split("@")[0])
#                         st.session_state.is_admin = auth_manager.is_admin(email)
#                         st.success("Login successful!")
#                         st.rerun()
#                     else:
#                         st.error(f"Login failed: {result['error']}")
#                 else:
#                     st.warning("Please fill in all fields")
    
#     with tab2:
#         with st.form("register_form"):
#             reg_name = st.text_input("Full Name", placeholder="Enter your full name")
#             reg_email = st.text_input("Email", placeholder="Enter your email")
#             reg_password = st.text_input("Password", type="password", placeholder="Create a password")
#             reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
#             if st.form_submit_button("Sign Up", use_container_width=True):
#                 if all([reg_name, reg_email, reg_password, reg_confirm]):
#                     if reg_password == reg_confirm:
#                         result = auth_manager.create_user_account(reg_email, reg_password, reg_name)
#                         if result["success"]:
#                             st.success("Account created successfully! Please sign in.")
#                         else:
#                             st.error(f"Registration failed: {result['error']}")
#                     else:
#                         st.error("Passwords don't match")
#                 else:
#                     st.warning("Please fill in all fields")

def show_login_modal():
    """Show login modal for anonymous users"""
    st.markdown("## 🔑 Login to Save Your Chat History")
    
    auth_manager = AuthManager()
    
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        with st.form("login_form_modal"):
            email = st.text_input("Email", placeholder="Enter your email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Sign In", use_container_width=True):
                    if email and password:
                        result = auth_manager.verify_user_credentials(email, password)
                        if result["success"]:
                            st.session_state.user_id = result["user_id"]
                            st.session_state.user_email = email
                            st.session_state.user_name = result.get("display_name", email.split("@")[0])
                            st.session_state.is_admin = auth_manager.is_admin(email)
                            st.session_state.show_login = False
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {result['error']}")
                    else:
                        st.warning("Please fill in all fields")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_login = False
                    st.rerun()
    
    with tab2:
        with st.form("register_form_modal"):
            reg_name = st.text_input("Full Name", placeholder="Enter your full name")
            reg_email = st.text_input("Email", placeholder="Enter your email")
            reg_password = st.text_input("Password", type="password", placeholder="Create a password")
            reg_confirm = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Sign Up", use_container_width=True):
                    if all([reg_name, reg_email, reg_password, reg_confirm]):
                        if reg_password == reg_confirm:
                            result = auth_manager.create_user_account(reg_email, reg_password, reg_name)
                            if result["success"]:
                                st.success("Account created successfully! Please sign in.")
                            else:
                                st.error(f"Registration failed: {result['error']}")
                        else:
                            st.error("Passwords don't match")
                    else:
                        st.warning("Please fill in all fields")
            
            with col2:
                if st.form_submit_button("Cancel", use_container_width=True):
                    st.session_state.show_login = False
                    st.rerun()

def chat_page():
    """Main chat interface"""
    load_css()
    render_chat_header()
    
    chat_manager = ChatManager()
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "current_page" not in st.session_state:
        st.session_state.current_page = 1
    
    # Get user ID (logged in or anonymous)
    current_user_id = st.session_state.get("user_id", generate_anonymous_user_id())
    
    # Render sidebar
    render_sidebar()
    
    # Show login modal if requested
    if st.session_state.get("show_login", False):
        show_login_modal()
        return
    
    # Main chat area
    if st.session_state.get("show_history", False):
        if not st.session_state.get("user_id"):
            st.warning("⚠️ Please login to view chat history")
            return
            
        st.subheader("📚 Chat History")
        
        history_result = chat_manager.get_conversation_history(
            st.session_state.user_id, 
            st.session_state.current_page
        )
        
        if history_result["success"]:
            messages = history_result["messages"]
            
            if messages:
                for msg in reversed(messages):
                    with st.expander(f"💬 {msg['input'][:50]}... - {msg['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
                        st.markdown(f"**You:** {msg['input']}")
                        st.markdown(f"**AI:** {msg['response']}")
                
                st.session_state.current_page = render_pagination(
                    history_result["page"], 
                    history_result["total_pages"],
                    "history"
                )
            else:
                st.info("No chat history found.")
        else:
            st.error(f"Error loading history: {history_result['error']}")
        
        return
    
    # Chat interface
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display messages
    for message in st.session_state.messages:
        render_message_with_viz(
            message["content"], 
            message["role"] == "user",
            message.get("timestamp", datetime.now()),
            message.get("visualization"),
            message.get("table")
        )
    
    # Chat input
    user_input = st.chat_input("Type your academic question here...")
    
    if user_input:
        # Add user message
        user_msg = {
            "role": "user", 
            "content": user_input, 
            "timestamp": datetime.now()
        }
        st.session_state.messages.append(user_msg)
        
        # Show typing indicator
        with st.empty():
            render_typing_indicator()
            time.sleep(1)
            
            # Get AI response
            result = chat_manager.send_message_to_api(user_input)
            
            if result["success"]:
                bot_response = result["response"]
                
                # Process for visualization
                processed_result = chat_manager.process_response_with_visualization(
                    user_input, bot_response
                )
                
                # Add bot message with visualization data
                bot_msg = {
                    "role": "assistant", 
                    "content": processed_result["response"], 
                    "timestamp": datetime.now(),
                    "visualization": processed_result["visualization"],
                    "table": processed_result["table"]
                }
                st.session_state.messages.append(bot_msg)
                
                # Save to database (works for both logged in and anonymous users)
                chat_manager.save_conversation(
                    current_user_id, 
                    user_input, 
                    bot_response
                )
            else:
                error_msg = {
                    "role": "assistant", 
                    "content": f"Sorry, I encountered an error: {result['error']}", 
                    "timestamp": datetime.now()
                }
                st.session_state.messages.append(error_msg)
        
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

def admin_page():
    """Admin panel for viewing all conversations"""
    st.title("👨‍💼 Admin Panel")
    
    chat_manager = ChatManager()
    
    # Back button
    if st.button("⬅️ Back to Chat"):
        st.session_state.current_page_name = "chat"
        st.rerun()
    
    st.subheader("📊 All Conversations")
    
    # Tambahkan debug info
    with st.expander("🐛 Debug Info"):
        try:
            # Debug 1: Cek semua collections di root level
            collections = chat_manager.db.collections()
            st.write("Available collections:")
            for collection in collections:
                st.write(f"- {collection.id}")
            
            # Debug 2: Cek apakah ada data di collection conversations
            conversations_ref = chat_manager.db.collection("conversations")
            
            # Coba ambil semua documents (termasuk yang tidak ada parent doc)
            all_docs = list(conversations_ref.list_documents())
            st.write(f"Documents in conversations collection: {len(all_docs)}")
            
            # Debug 3: Cek setiap document
            for doc_ref in all_docs:
                st.write(f"Document ID: {doc_ref.id}")
                
                # Cek apakah document benar-benar ada
                doc_snapshot = doc_ref.get()
                if doc_snapshot.exists:
                    st.write(f"  - Document exists with data: {doc_snapshot.to_dict()}")
                else:
                    st.write(f"  - Document doesn't exist (only subcollections)")
                
                # Cek subcollections
                subcollections = doc_ref.collections()
                for subcoll in subcollections:
                    subcoll_docs = list(subcoll.stream())
                    st.write(f"  - Subcollection '{subcoll.id}': {len(subcoll_docs)} messages")
            
            # Debug 4: Langsung cek method save_conversation
            st.write(f"Current user_id: {st.session_state.get('user_id', 'Not set')}")
            
        except Exception as e:
            st.error(f"Debug error: {e}")
            import traceback
            st.code(traceback.format_exc())
            
    # Get all conversations
    conversations = chat_manager.get_all_conversations()
    
    if conversations:
        # Convert to DataFrame
        df = pd.DataFrame(conversations)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp', ascending=False)
        
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", len(conversations))
        with col2:
            st.metric("Unique Users", df['user_id'].nunique())
        with col3:
            st.metric("Today's Messages", 
                     len(df[df['timestamp'].dt.date == datetime.now().date()]))
        
        # Export button
        if st.button("📥 Export Data"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"conversations_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        # Display conversations
        st.subheader("Recent Conversations")
        
        # Pagination for admin view
        page_size = 20
        total_pages = (len(df) + page_size - 1) // page_size
        
        if "admin_page" not in st.session_state:
            st.session_state.admin_page = 1
        
        start_idx = (st.session_state.admin_page - 1) * page_size
        end_idx = start_idx + page_size
        page_df = df.iloc[start_idx:end_idx]
        
        for _, row in page_df.iterrows():
            with st.expander(f"👤 {row['user_id'][:8]}... - {row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"):
                st.markdown(f"**User Input:** {row['input']}")
                st.markdown(f"**AI Response:** {row['response']}")
                st.markdown(f"**Timestamp:** {row['timestamp']}")
        
        # Admin pagination
        st.session_state.admin_page = render_pagination(
            st.session_state.admin_page, 
            total_pages,
            "admin"
        )
        
    else:
        st.info("No conversations found.")

# Main app
def main():
    load_css()
    
    # Initialize anonymous user ID jika belum ada user_id
    if "user_id" not in st.session_state:
        generate_anonymous_user_id()
    
    # Route to appropriate page
    current_page = st.session_state.get("current_page_name", "chat")
    
    if current_page == "admin" and st.session_state.get("is_admin", False):
        admin_page()
    else:
        chat_page()

if __name__ == "__main__":
    main()