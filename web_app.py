import streamlit as st
import os
from config import PROVIDERS, CATEGORIES, MOODS, RESOLUTIONS
import wallpaper

st.set_page_config(page_title="Easy Wallpaper", page_icon="🖼️", layout="wide")

st.title("🖼️ Easy Wallpaper")
st.markdown("### Download and set beautiful wallpapers from multiple sources.")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Helper to get provider by name
# Sort provider names for consistent order
provider_names = {p.get_name(): k for k, p in sorted(PROVIDERS.items(), key=lambda item: int(item[0]))}
selected_provider_name = st.sidebar.selectbox("Select Provider", list(provider_names.keys()))
provider_id = provider_names[selected_provider_name]
provider = PROVIDERS[provider_id]

st.sidebar.markdown(f"**Description:** {provider.get_description()}")

# Categories
categories = CATEGORIES.get(selected_provider_name, [])
if categories:
    category = st.sidebar.selectbox("Category", categories)
else:
    # Some providers might just take free text
    category = st.sidebar.text_input("Category", "random")

# Moods
moods = MOODS.get(selected_provider_name, [""])
# Filter out empty strings for display if there are other options
display_moods = [m for m in moods if m]
if display_moods:
    mood = st.sidebar.selectbox("Mood", display_moods)
else:
    mood = ""

# Resolution
resolution = st.sidebar.selectbox("Target Resolution", RESOLUTIONS, index=0)

# Set resolution on provider if supported
provider.set_resolution(resolution)

# Main area
col1, col2 = st.columns([3, 1])

if "current_image" not in st.session_state:
    st.session_state.current_image = None
if "current_image_path" not in st.session_state:
    st.session_state.current_image_path = None

with col1:
    st.subheader("Preview")
    if st.button("⬇️ Download & Preview", type="primary"):
        try:
            with st.spinner(f"Downloading from {selected_provider_name}..."):
                # Clean up previous state
                st.session_state.current_image = None
                st.session_state.current_image_path = None

                image_data = provider.download_image(category, mood)
                st.session_state.current_image = image_data
                st.success("Image downloaded successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.session_state.current_image:
        st.image(st.session_state.current_image, caption=f"{selected_provider_name} - {category} ({mood})", use_container_width=True)

with col2:
    st.subheader("Actions")
    if st.session_state.current_image:
        if st.button("🖥️ Set as Wallpaper"):
            try:
                with st.spinner("Setting wallpaper..."):
                    # Save first
                    filename = f"wallpaper_{selected_provider_name}_{category}_{mood}.png".replace(" ", "_").replace("__", "_")
                    path = wallpaper.save_wallpaper(st.session_state.current_image, filename)
                    st.session_state.current_image_path = path

                    # Set wallpaper
                    wallpaper.set_wallpaper(path)
                    st.balloons()
                    st.success(f"Wallpaper set successfully!")
            except Exception as e:
                st.error(f"Failed to set wallpaper: {e}")

        if st.session_state.current_image_path:
             st.info(f"Saved to: `{st.session_state.current_image_path}`")

    st.markdown("---")
    st.markdown("#### API Keys")
    st.caption("Ensure API keys are set in your environment variables for premium providers.")

    with st.expander("Check Environment Variables"):
        keys = [
            "PEXELS_API_KEY",
            "PIXABAY_API_KEY",
            "UNSPLASH_ACCESS_KEY",
            "WALLHAVEN_API_KEY",
            "NASA_API_KEY"
        ]
        for key in keys:
            val = os.getenv(key)
            status = "✅ Set" if val else "❌ Not Set"
            st.write(f"**{key}**: {status}")

st.markdown("---")
st.caption("Run with `streamlit run web_app.py`")
