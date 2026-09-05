import streamlit as st
import requests
import base64
import urllib.parse
import os

st.set_page_config(page_title="SOCIO", layout="wide")

# --- Minimal, classy color palette ---
# Warm off-white background, one muted slate-navy accent, soft neutral borders.
# No bright colors, no gradients - kept deliberately restrained.
st.markdown("""
<style>
[data-testid="stApp"] {
    background-color: #FAF9F5;
}
h1, h2, h3 {
    color: #2B2B28 !important;
    font-weight: 600;
}
p, label, span, div {
    color: #2B2B28;
}
[data-testid="stSidebar"] {
    background-color: #F1EEE6;
    border-right: 1px solid #E3DFD3;
}
div.stButton > button[kind="primary"] {
    background-color: #33475B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    font-weight: 500;
}
div.stButton > button[kind="primary"]:hover {
    background-color: #24313F;
    color: #FFFFFF;
}
div.stButton > button[kind="secondary"] {
    background-color: transparent;
    color: #33475B;
    border: 1px solid #33475B;
    border-radius: 8px;
    font-weight: 500;
}
div.stButton > button[kind="secondary"]:hover {
    background-color: #EFEDE6;
}
input, textarea {
    border-radius: 8px !important;
    border: 1px solid #DAD5C8 !important;
}
[data-testid="stFileUploader"] {
    border-radius: 8px;
    border: 1px dashed #C9C3B3;
    padding: 0.5rem;
}
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border: 1px solid #E3DFD3 !important;
}
</style>
""", unsafe_allow_html=True)


def get_initials(email: str) -> str:
    """Turn an email into 1-2 letter initials for the avatar chip."""
    name_part = email.split("@")[0]
    pieces = [p for p in name_part.replace(".", "_").split("_") if p]
    if not pieces:
        return "?"
    if len(pieces) == 1:
        return pieces[0][:2].upper()
    return (pieces[0][0] + pieces[1][0]).upper()

# Backend URL: falls back to localhost for local dev, but can be overridden
# via Streamlit secrets (st.secrets["API_URL"]) or the API_URL env var when
# deployed, so this file doesn't need editing per-environment.
API_URL = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))

# Initialize session state
if 'token' not in st.session_state:
    st.session_state.token = None
if 'user' not in st.session_state:
    st.session_state.user = None


def get_headers():
    """Get authorization headers with token"""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}


def login_page():
    st.title("SOCIO")
    st.markdown("<p style='color:#6B6B63;margin-top:-10px;'>Welcome back</p>", unsafe_allow_html=True)

    # Simple form with two buttons
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")

    if email and password:
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Login", type="primary", use_container_width=True):
                # Login using FastAPI Users JWT endpoint
                login_data = {"username": email, "password": password}
                response = requests.post(f"{API_URL}/auth/jwt/login", data=login_data)

                if response.status_code == 200:
                    token_data = response.json()
                    st.session_state.token = token_data["access_token"]

                    # Get user info
                    user_response = requests.get(f"{API_URL}/users/me", headers=get_headers())
                    if user_response.status_code == 200:
                        st.session_state.user = user_response.json()
                        st.rerun()
                    else:
                        st.error("Failed to get user info")
                else:
                    st.error("Invalid email or password!")

        with col2:
            if st.button("Sign Up", type="secondary", use_container_width=True):
                # Register using FastAPI Users
                signup_data = {"email": email, "password": password}
                response = requests.post(f"{API_URL}/auth/register", json=signup_data)

                if response.status_code == 201:
                    st.success("Account created! Click Login now.")
                else:
                    error_detail = response.json().get("detail", "Registration failed")
                    st.error(f"Registration failed: {error_detail}")
    else:
        st.info("Enter your email and password above")


def upload_page():
    st.title("Share something")

    uploaded_file = st.file_uploader("Choose media", type=['png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov', 'mkv', 'webm'])
    caption = st.text_area("Caption:", placeholder="What's on your mind?")

    if uploaded_file and st.button("Share", type="primary"):
        with st.spinner("Uploading..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            data = {"caption": caption}
            response = requests.post(f"{API_URL}/upload", files=files, data=data, headers=get_headers())

            if response.status_code == 200:
                st.success("Posted!")
                st.rerun()
            else:
                st.error("Upload failed!")


def encode_text_for_overlay(text):
    """Encode text for ImageKit overlay - base64 then URL encode"""
    if not text:
        return ""
    # Base64 encode the text
    base64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
    # URL encode the result
    return urllib.parse.quote(base64_text)


def create_transformed_url(original_url, transformation_params, caption=None):
    if caption:
        encoded_caption = encode_text_for_overlay(caption)
        # Add text overlay at bottom with semi-transparent background
        text_overlay = f"l-text,ie-{encoded_caption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end"
        transformation_params = text_overlay

    if not transformation_params:
        return original_url

    # ImageKit URLs are always <scheme>://<host>/<imagekit_id>/<file_path>.
    # Insert the transformation segment right after the imagekit_id, using
    # urlsplit instead of assuming a fixed index, so this keeps working even
    # if the file path itself contains extra slashes or query strings.
    parsed = urllib.parse.urlsplit(original_url)
    path_parts = parsed.path.lstrip("/").split("/", 1)

    if len(path_parts) != 2:
        # Unexpected URL shape (not a standard ImageKit CDN URL) - return
        # the original rather than guessing and risking a broken image.
        return original_url

    imagekit_id, file_path = path_parts
    new_path = f"/{imagekit_id}/tr:{transformation_params}/{file_path}"
    return urllib.parse.urlunsplit(
        (parsed.scheme, parsed.netloc, new_path, parsed.query, parsed.fragment)
    )


def feed_page():
    st.title("Feed")

    response = requests.get(f"{API_URL}/feed", headers=get_headers())
    if response.status_code == 200:
        posts = response.json()["posts"]

        if not posts:
            st.info("No posts yet! Be the first to share something.")
            return

        for post in posts:
            with st.container(border=True):
                col1, col2, col3 = st.columns([0.6, 4, 1])
                with col1:
                    initials = get_initials(post['email'])
                    st.markdown(
                        f"<div style='width:34px;height:34px;border-radius:50%;"
                        f"background:#33475B;color:#FFFFFF;display:flex;"
                        f"align-items:center;justify-content:center;font-size:13px;"
                        f"font-weight:600;'>{initials}</div>",
                        unsafe_allow_html=True,
                    )
                with col2:
                    st.markdown(f"**{post['email']}**  \n"
                                f"<span style='color:#6B6B63;font-size:13px;'>{post['created_at'][:10]}</span>",
                                unsafe_allow_html=True)
                with col3:
                    if post.get('is_owner', False):
                        if st.button("Delete", key=f"delete_{post['id']}", help="Delete post"):
                            response = requests.delete(
                                f"{API_URL}/delete/{post['id']}",
                                headers=get_headers()
                            )
                            if response.status_code == 200:
                                st.success("Post deleted!")
                                st.rerun()
                            else:
                                st.error("Failed to delete post!")

                # Uniform media display with caption overlay
                caption = post.get('caption', '')
                if post['file_type'] == 'image':
                    uniform_url = create_transformed_url(post['url'], "", caption)
                    st.image(uniform_url, width=300)
                else:
                    # For videos: specify only height to maintain aspect ratio + caption overlay
                    uniform_video_url = create_transformed_url(post['url'], "w-400,h-200,cm-pad_resize,bg-blurred")
                    st.video(uniform_video_url, width=300)
                    st.caption(caption)
    else:
        st.error("Failed to load feed")


# Main app logic
if st.session_state.user is None:
    login_page()
else:
    # Sidebar navigation
    st.sidebar.title(f"Hi, {st.session_state.user['email'].split('@')[0]}")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.session_state.token = None
        st.rerun()

    st.sidebar.markdown("---")
    page = st.sidebar.radio("Navigate:", ["Feed", "Upload"])

    if page == "Feed":
        feed_page()
    else:
        upload_page()
