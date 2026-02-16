import streamlit as st
import numpy as np
import pickle

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AQI Prediction", page_icon="🌫️", layout="wide")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    with open("Final_model_AirQualityPrediction.pkl", "rb") as f:
        return pickle.load(f)

model = load_model()

# ---------------- SESSION STATE ----------------
if "page" not in st.session_state:
    st.session_state.page = "input"

# ---------------- COUNTRY → CITY MAPPING ----------------
country_city_map = {
    "USA": ["Los Angeles", "New York"],
    "India": ["Chennai", "Delhi", "Mumbai"],
    "UAE": ["Dubai"],
    "UK": ["London"],
    "Australia": ["Sydney"],
    "China": ["Shanghai"]
}

# ---------------- CUSTOM CSS (Responsive & Theme Safe) ----------------
st.markdown("""
<style>
/* Responsive App Container */
.stApp {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    padding: 10px;
    transition: background 0.5s ease;
}

/* Adaptive Title */
.title {
    text-align: center;
    font-size: clamp(28px, 5vw, 40px);
    font-weight: bold;
    margin-bottom: 20px;
}

/* Button Styling */
button[kind="primary"] {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color: white !important;
    font-size: clamp(16px, 3vw, 18px);
    border-radius: 10px;
    padding: 8px 20px;
    box-shadow: 0px 0px 20px #00c6ff;
    transition: transform 0.2s;
}
button[kind="primary"]:hover {
    transform: scale(1.05);
}

/* Smoke Animation - responsive */
.smoke-container {
    position: relative;
    height: 25vh;
    width: 100%;
    max-width: 500px;
    margin: 20px auto;
}
.smoke {
    position: absolute;
    bottom: 0;
    width: 15vw;
    max-width: 150px;
    height: 15vw;
    max-height: 150px;
    background: radial-gradient(circle, currentColor 20%, transparent 70%);
    border-radius: 50%;
    filter: blur(25px);
    animation: rise 4s infinite ease-in-out;
}
@keyframes rise {
    0% { transform: translateY(0) scale(1); opacity: 0.6; }
    50% { transform: translateY(-100px) scale(1.4); opacity: 0.8; }
    100% { transform: translateY(-200px) scale(1.8); opacity: 0; }
}

/* Adaptive Dark/Light Theme */
@media (prefers-color-scheme: dark) {
    .stApp {
        background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
        color: white;
    }
    button[kind="primary"] {
        box-shadow: 0px 0px 20px #00c6ff;
    }
}
@media (prefers-color-scheme: light) {
    .stApp {
        background: linear-gradient(to right, #e0f7fa, #80deea, #26c6da);
        color: black;
    }
    button[kind="primary"] {
        box-shadow: 0px 0px 20px #0072ff;
    }
}

/* Responsive Columns for Mobile */
@media (max-width: 768px) {
    .st-bc {  /* Streamlit column wrapper */
        flex-direction: column !important;
    }
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# INPUT PAGE
# =====================================================
if st.session_state.page == "input":

    st.markdown('<p class="title">🌫️ Air Quality Index Prediction</p>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    # LEFT SIDE (Pollution)
    with col1:
        st.subheader("Pollution Values")
        pm25 = st.number_input("PM2.5", min_value=0.0, max_value=500.0, value=0.0, step=0.01, format="%.2f")
        pm10 = st.number_input("PM10", min_value=0.0, max_value=500.0, value=0.0, step=0.01, format="%.2f")
        no2 = st.number_input("NO2", min_value=0.0, max_value=300.0, value=0.0, step=0.01, format="%.2f")
        so2 = st.number_input("SO2", min_value=0.0, max_value=300.0, value=0.0, step=0.01, format="%.2f")
        co = st.number_input("CO", min_value=0.0, max_value=300.0, value=0.0, step=0.01, format="%.2f")
        o3 = st.number_input("O3", min_value=0.0, max_value=300.0, value=0.0, step=0.01, format="%.2f")

    # RIGHT SIDE (Weather & Location)
    with col2:
        st.subheader("Weather Conditions")
        temp = st.number_input("Temperature (°C)", min_value=-10.0, max_value=100.0, value=25.0, step=0.01, format="%.2f")
        humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=50.0, step=0.01, format="%.2f")
        windspeed = st.number_input("Wind Speed (km/h)", min_value=0, max_value=100, value=5, step=1)

        # Country & City selection
        country = st.selectbox("Select Country", list(country_city_map.keys()))
        city = st.selectbox("Select City", country_city_map[country])

    st.markdown("<br>", unsafe_allow_html=True)
    center1, center2, center3 = st.columns([2,2,2])

    # PREDICT BUTTON
    with center2:
        if st.button("🔮 Predict AQI", type="primary"):

            # Validation: Ensure city belongs to country
            if city not in country_city_map[country]:
                st.error(f"❌ Invalid city '{city}' for country '{country}'. Please select a valid city.")
            else:
                # COUNTRY ENCODING
                country_usa = 1 if country == "USA" else 0

                # CITY ENCODING (all cities)
                all_cities = sum(country_city_map.values(), [])  # flatten list
                city_encoding = [1 if city == c else 0 for c in all_cities]

                # INPUT ARRAY
                input_data = np.array([[pm25, pm10, no2, so2, co, o3, temp, humidity, windspeed, country_usa, *city_encoding]])

                # PREDICTION
                try:
                    prediction = model.predict(input_data)
                    st.session_state.aqi = prediction[0]
                    st.session_state.page = "result"
                    st.rerun()
                except Exception as e:
                    st.error(f"Prediction failed: {e}")

# =====================================================
# RESULT PAGE
# =====================================================
if st.session_state.page == "result":

    aqi = st.session_state.aqi

    # AQI LEVEL DECISION
    if aqi <= 50:
        bg_color = "#1e7f3f"  # Green
        status = "🟢 Good Air Quality"
        message = "Air quality is safe and clean."
    elif aqi <= 100:
        bg_color = "#c9a227"  # Yellow
        status = "🟡 Moderate Pollution"
        message = "Sensitive people should be cautious."
    else:
        bg_color = "#8b1e1e"  # Red
        status = "🔴 High Pollution"
        message = "Avoid outdoor activities. Wear a mask."

    # APPLY SOLID BACKGROUND
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: white;
    }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center;'>AQI Prediction Result</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>AQI Value: {aqi:.2f}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='text-align:center;'>{status}</h2>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align:center;'>{message}</h4>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # BACK BUTTON
    center1, center2, center3 = st.columns([2,2,2])
    with center2:
        if st.button("⬅ Back"):
            st.session_state.page = "input"
            st.rerun()
