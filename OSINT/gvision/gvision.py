import io
import cv2
import numpy as np
import streamlit as st
from google.cloud import vision
from google.cloud.vision_v1 import types
from google.oauth2 import service_account
from streamlit_folium import folium_static
import folium
from PIL import Image
import xyzservices.providers as xyz
import json

def gvision_app():
    """Streamlit interface for GVision Image Analysis."""
    
    # Set page style
    st.title('📷 GVision - Reverse Image Search')
    st.write(
        "GVision is a Streamlit-based reverse image search tool that helps users analyze and retrieve information "
        "from images using open-source intelligence (OSINT) techniques. Upload an image, and the tool will scan for "
        "similar images, related metadata, and potential sources across various platforms."
    )

    # Sidebar - About Section
    st.sidebar.title('ℹ️ About')
    st.sidebar.info(
        "GVision uses Google Cloud Vision API to detect landmarks and web entities from images.\n\n"
        "For obtaining Google Cloud Vision API, please refer to the following "
        "[documentation](https://github.com/GONZOsint/gvision)."
    )

    # Upload config file (Persistent with session state)
    if "credentials" not in st.session_state:
        config_file = st.file_uploader('Upload a config file', type=['json'])

        if config_file is not None:
            try:
                credentials_json = json.loads(config_file.read())
                st.session_state.credentials = service_account.Credentials.from_service_account_info(credentials_json)
                st.session_state.client = vision.ImageAnnotatorClient(credentials=st.session_state.credentials)
                st.success("✅ Config file loaded successfully! You can now upload an image.")
            except json.JSONDecodeError:
                st.error("❌ Invalid JSON format. Please check your config file.")
                return
            except Exception as e:
                st.error(f"❌ Error loading config file: {e}")
                return
        else:
            st.warning('⚠️ Please upload a config file to proceed.')
            return  # Stop execution if config is not uploaded

    # Image Upload (Only appears after config is loaded)
    uploaded_file = st.file_uploader('Choose an image', type=['jpg', 'jpeg', 'png'])

    if uploaded_file is not None:
        with st.spinner('🔍 Analyzing the image...'):
            content = uploaded_file.read()
            image = types.Image(content=content)

            # Detect landmarks
            response = st.session_state.client.landmark_detection(image=image)
            landmarks = response.landmark_annotations

            st.subheader('📤 Uploaded Image:')
            image_pil = Image.open(io.BytesIO(content))
            st.image(image_pil, use_container_width=True)

            if landmarks:
                st.subheader('📍 Landmark Detected:')
                for landmark in landmarks:
                    st.write(f"- **{landmark.description}**")
                    st.write(f"- **Coordinates**: {landmark.locations[0].lat_lng.latitude}, {landmark.locations[0].lat_lng.longitude}")

                # Create Map
                def create_folium_map(landmarks):
                    providers = xyz.flatten()
                    m = folium.Map(
                        location=[landmarks[0].locations[0].lat_lng.latitude, landmarks[0].locations[0].lat_lng.longitude],
                        zoom_start=15
                    )
                    for landmark in landmarks:
                        folium.Marker(
                            location=[landmark.locations[0].lat_lng.latitude, landmark.locations[0].lat_lng.longitude],
                            tooltip=landmark.description
                        ).add_to(m)

                    folium.LayerControl().add_to(m)
                    return m

                folium_map = create_folium_map(landmarks)
                folium_static(folium_map)

            else:
                st.warning('❌ No landmarks detected.')

            # Detect logos
            response = st.session_state.client.logo_detection(image=image)
            logos_detected = response.logo_annotations
            if logos_detected:
                st.subheader('👓 Logos Detected:')
                for logo in logos_detected:
                    st.write(f"- {logo.description}")
            else:
                st.warning('❌ No Logos Detected.')

            # Detect objects
            response = st.session_state.client.object_localization(image=image)
            object_annotations = response.localized_object_annotations
            if object_annotations:
                st.subheader('🧳 Objects Detected:')
                annotated_image = cv2.imdecode(np.frombuffer(content, np.uint8), cv2.IMREAD_COLOR)
                for object_found in object_annotations:
                    vertices = [(int(vertex.x * annotated_image.shape[1]), int(vertex.y * annotated_image.shape[0]))
                                for vertex in object_found.bounding_poly.normalized_vertices]
                    for i in range(len(vertices)):
                        cv2.line(annotated_image, vertices[i], vertices[(i + 1) % len(vertices)], (0, 255, 0), 2)
                    cv2.putText(annotated_image, f"{object_found.name} ({round(object_found.score * 100, 1)}% Confidence)", 
                                (vertices[0][0], vertices[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
                st.image(annotated_image, channels="RGB")
            else:
                st.warning('❌ No Objects Detected.')

            # Detect web entities
            response = st.session_state.client.web_detection(image=image)
            web_entities = response.web_detection.web_entities
            if web_entities:
                st.subheader('🌐 Web Entities Detected:')
                for entity in web_entities:
                    st.write(f"- {entity.description}")

# Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. Developed by ECLOGIC.
    """)
