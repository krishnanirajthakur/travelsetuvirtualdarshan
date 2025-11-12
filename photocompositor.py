# Install: pip install streamlit rembg Pillow
import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

# Configure the basic page settings
st.set_page_config(
    page_title="Photo Composer",
    page_icon="✂️",
    layout="wide"
)

# --- THE IMAGE PROCESSING LOGIC ---
def composite_images_web(fg_file, bg_file, scale_factor):
    """Handles image processing: background removal, resizing, and compositing."""
    try:
        # 1. READ AND REMOVE BACKGROUND
        fg_input = Image.open(BytesIO(fg_file.read())).convert("RGBA") 
        fg_removed_bg = remove(fg_input).convert("RGBA")
        
        # 2. READ BACKGROUND
        bg_img = Image.open(BytesIO(bg_file.read())).convert("RGB")

        # 3. RESIZE AND CENTER FOREGROUND
        original_width, original_height = fg_removed_bg.size
        bg_width, bg_height = bg_img.size
        
        # Calculate new dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Check for minimum size constraints before resizing
        if new_width == 0 or new_height == 0:
            return None, "Error: Scale factor resulted in zero dimension."
        
        # Resize the foreground
        fg_resized = fg_removed_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate position to center the foreground
        x_pos = max(0, (bg_width - new_width) // 2)
        y_pos = max(0, (bg_height - new_height) // 2)
        box = (x_pos, y_pos, x_pos + new_width, y_pos + new_height)
        
        # 4. COMPOSITE
        bg_img.paste(fg_resized, box, mask=fg_resized)
        
        # 5. SAVE RESULT TO MEMORY (BytesIO)
        processed_image_io = BytesIO()
        bg_img.save(processed_image_io, format='JPEG')
        processed_image_io.seek(0)
        
        return processed_image_io, None

    except Exception as e:
        return None, f"An error occurred during processing: {e}"

# --- STREAMLIT APP LAYOUT AND UI ---

st.title("✂️ Free Photo Background Swapper")
st.markdown("Easily remove the background from one image and composite it onto another. The final image is saved as a JPEG.")

st.divider()

# Create two columns for a clean layout
col1, col2 = st.columns([1, 2]) # col2 is twice as wide as col1

with col1:
    st.header("1. Upload & Settings")
    
    # Upload Widgets
    foreground_file = st.file_uploader(
        "**Upload your Foreground Photo (The Cutout)**", 
        type=['png', 'jpg', 'jpeg'],
        help="This image will have its background removed."
    )
    
    background_file = st.file_uploader(
        "**Upload the New Background Image**", 
        type=['png', 'jpg', 'jpeg'],
        help="The final image will be pasted onto this."
    )

    st.subheader("Image Scale")
    # Scale Slider
    scale = st.slider(
        "Resize Factor for Cutout (0.1 = 10% | 1.0 = 100%)", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.5, 
        step=0.05,
        help="Adjust the size of the foreground photo relative to its original size."
    )

with col2:
    st.header("2. Result & Download")

    if foreground_file and background_file:
        
        # Show a progress spinner while processing
        with st.spinner('Processing image... This may take a moment to remove the background.'):
            # Call the processing function
            output_image_io, error_message = composite_images_web(foreground_file, background_file, scale)
            
        if output_image_io:
            st.success("✅ Success! Image ready for download.")
            
            st.image(
                output_image_io, 
                caption=f"Final Composited Image (Scale Factor: {scale:.2f})", 
                use_column_width=True
            )
            
            # Provide a clear download button
            st.download_button(
                label="⬇️ Download Composited Image (JPEG)",
                data=output_image_io,
                file_name="composited_result.jpg",
                mime="image/jpeg",
                type="primary" # Use the primary button style
            )
            
        elif error_message:
            st.error(f"Processing Failed: {error_message}")
    
    else:
        st.info("Please upload both a Foreground Photo and a New Background Image to begin.")