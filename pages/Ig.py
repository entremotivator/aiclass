import os
import tempfile
from pathlib import Path

import streamlit as st

# Optional, but helps when running behind proxies
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

st.set_page_config(page_title="IG Post / Reels Downloader", page_icon="📥", layout="centered")

st.title("📥 Instagram Post / Reels Downloader")
st.caption("Paste an Instagram URL (reel, post, or video). Uses yt-dlp under the hood.")

DEFAULT_URL = "https://www.instagram.com/reel/DKuN44FJP5Q/?igsh=NXNiODdzdTdjNGFs"
url = st.text_input("Instagram URL", value=DEFAULT_URL, placeholder="https://www.instagram.com/reel/...", label_visibility="visible")

with st.expander("Advanced (optional) - Cookies for private/blocked content"):
    st.markdown(
        "If the video is private, age-gated, or your network gets blocked by Instagram, upload a Netscape 'cookies.txt'. "
        "You can export it with browser extensions. This is optional for public reels."
    )
    cookies_file = st.file_uploader("Upload cookies.txt", type=["txt"], accept_multiple_files=False)

col1, col2 = st.columns(2)
get_info = col1.button("🔎 Get info", type="secondary")
do_download = col2.button("⬇️ Download", type="primary")

# Lazy import so the app loads fast
def _ydl(cookies_path: str | None = None, quiet=True):
    try:
        from yt_dlp import YoutubeDL
    except Exception as e:
        st.error("yt-dlp isn't installed. Add `yt-dlp` to requirements.txt and redeploy.")
        raise
    ydl_opts = {
        "quiet": quiet,
        "no_warnings": True,
        "noprogress": True,
        "retries": 3,
        "concurrent_fragment_downloads": 3,
        # Lower rate to be a better citizen / sometimes helps avoid throttling
        "ratelimit": None,
        "http_chunk_size": 1048576,
        "outtmpl": "%(title).95s.%(ext)s",
    }
    if cookies_path:
        ydl_opts["cookiefile"] = cookies_path
    return YoutubeDL(ydl_opts)

@st.cache_data(show_spinner=False)
def extract_info(url: str, cookies_bytes: bytes | None):
    cookies_path = None
    tmp = None
    if cookies_bytes:
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
        tmp.write(cookies_bytes)
        tmp.flush()
        cookies_path = tmp.name
    try:
        ydl = _ydl(cookies_path, quiet=True)
        info = ydl.extract_info(url, download=False)
        return info
    finally:
        if tmp:
            try:
                os.unlink(tmp.name)
            except Exception:
                pass

def _describe_info(info: dict) -> tuple[str, str | None, list[tuple[str,str]]]:
    # Returns (title, thumbnail, formats[(format_id, human_label)])
    title = info.get("title") or info.get("fulltitle") or "Instagram media"
    thumb = info.get("thumbnail")
    formats = []
    for f in info.get("formats", []):
        # Filter only video formats with extension
        if not f.get("ext"):
            continue
        # Build a readable label
        height = f.get("height")
        fps = f.get("fps")
        tbr = f.get("tbr")
        vcodec = f.get("vcodec")
        acodec = f.get("acodec")
        size = f.get("filesize") or f.get("filesize_approx")
        parts = []
        if height:
            parts.append(f"{height}p")
        if fps:
            parts.append(f"{int(fps)}fps")
        if tbr:
            parts.append(f"{int(tbr)}kbps")
        if vcodec and vcodec != "none":
            parts.append(vcodec.split(".")[-1])
        if acodec and acodec != "none":
            parts.append("audio")
        if size:
            # rough MB
            try:
                parts.append(f"{int(size)/1024/1024:.1f}MB")
            except Exception:
                pass
        label = " • ".join(parts) if parts else f.get("format") or f.get("format_id")
        formats.append((f.get("format_id"), label))
    # Deduplicate by format_id, preserve order
    seen = set()
    uniq = []
    for fid, lbl in formats:
        if fid and fid not in seen:
            uniq.append((fid, lbl))
            seen.add(fid)
    return title, thumb, uniq

selected_format = st.session_state.get("selected_format", None)

info = None
if get_info and url.strip():
    with st.spinner("Fetching info..."):
        try:
            info = extract_info(url.strip(), cookies_file.read() if cookies_file else None)
            title, thumb, fmts = _describe_info(info)
            st.success(f"Found: {title}")
            if thumb:
                st.image(thumb, caption="Thumbnail", use_column_width=True)
            if fmts:
                selected_format = st.selectbox("Choose quality/format", options=[f[0] for f in fmts], format_func=lambda k: dict(fmts)[k])
                st.session_state["selected_format"] = selected_format
            else:
                st.info("No multiple formats reported. The 'best' format will be used.")
        except Exception as e:
            st.error(f"Could not fetch info. {e}")

if do_download and url.strip():
    with st.spinner("Downloading..."):
        tmpdir = tempfile.mkdtemp(prefix="igdl_")
        cookies_path = None
        tmp_cookie = None
        try:
            if cookies_file:
                tmp_cookie = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
                tmp_cookie.write(cookies_file.getvalue())
                tmp_cookie.flush()
                cookies_path = tmp_cookie.name

            from yt_dlp import YoutubeDL
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "noprogress": True,
                "retries": 3,
                "concurrent_fragment_downloads": 3,
                "outtmpl": os.path.join(tmpdir, "%(title).95s.%(ext)s"),
            }
            if cookies_path:
                ydl_opts["cookiefile"] = cookies_path
            if selected_format:
                ydl_opts["format"] = selected_format
            else:
                ydl_opts["format"] = "bestvideo*+bestaudio/best"

            with YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(url.strip(), download=True)
                # Determine downloaded file path
                filename = ydl.prepare_filename(res)
                # Some extractors adjust ext after download (e.g., .mp4)
                if not os.path.exists(filename):
                    # Try to find any file in tmpdir
                    files = list(Path(tmpdir).glob("*"))
                    if files:
                        filename = str(files[0])

            if os.path.exists(filename):
                data = Path(filename).read_bytes()
                name = Path(filename).name
                st.success("Download ready:")
                st.download_button("Save file", data=data, file_name=name, mime="video/mp4")
            else:
                st.error("Download finished but file not found.")

        except Exception as e:
            st.error(f"Download failed: {e}")
        finally:
            # Best effort cleanup of cookies
            if tmp_cookie:
                try:
                    os.unlink(tmp_cookie.name)
                except Exception:
                    pass

st.markdown("---")
st.caption("Note: Respect Instagram's Terms of Use and only download content you have rights to save.")
