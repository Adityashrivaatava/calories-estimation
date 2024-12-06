from dotenv import load_dotenv
import streamlit as st
import os
import google.generativeai as genai
from PIL import Image

# Load environment variables
load_dotenv()

# Configure the Google Generative AI SDK
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load Google Gemini Pro Vision API and get a response
def get_gemini_response(image, prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content([prompt, image[0]])
    return response.text

# Prepare the uploaded image for the API
def input_image_setup(uploaded_file):
    bytes_data = uploaded_file.getvalue()
    image_parts = [
        {
            "mime_type": uploaded_file.type,
            "data": bytes_data
        }
    ]
    return image_parts

# Streamlit Configuration
st.set_page_config(
    page_title="NutriTrack AI: Your Health & Wellness Companion",
    page_icon="🍏",
    layout="wide"
)

# Custom CSS for enhanced UI
st.markdown("""
    <style>
        .app-header {
            text-align: center;
            font-size: 2.8rem;
            color: #2E8B57;
            font-weight: bold;
        }
        .sub-header {
            text-align: center;
            font-size: 1.2rem;
            color: #6A5ACD;
        }
        .card {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 10px;
            margin: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
        }
        .btn-calculate {
            display: inline-block;
            width: 100%;
            background-color: #4CAF50;
            color: white;
            padding: 10px;
            font-size: 1rem;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .btn-calculate:hover {
            background-color: #45a049;
        }
        .image-container {
            text-align: center;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# App Title
st.markdown('<div class="app-header">Food Recognititon & Calories Estimation Using Yolov5</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Analyze food, calculate BMI, and determine daily calorie needs.</div>', unsafe_allow_html=True)

# Main Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["🍴 Calorie Estimation", "📏 BMI Calculator", "🔥 Daily Calorie Requirement", "💧 Water Intake Calculator", "📚 Meal History"]
)

# ---- Tab 1: Calorie Estimation ----
with tab1:
    st.markdown('<div class="card"><h3>🍴 Calorie Estimation Using AI</h3></div>', unsafe_allow_html=True)
    st.write("Upload an image of your meal, and AI will estimate its calorie content and provide detailed results.")

    input_prompt = """
    You are an expert Nutritionist and Food Image Analyst. Analyze the food items present in the uploaded image and perform the following tasks:
    1. Identify each distinct food item present in the image.
    2. For each identified food item, provide:
       - Name of the food item.
       - Estimated quantity or portion size (e.g., grams, slices, etc.).
       - Estimated calorie count based on the portion size.
    3. Summarize the results in a well-structured table with the following columns:
       - Food Item
       - Portion Size
       - Calorie Count
    4. At the end, calculate and display the **total calorie count** of all the identified food items.
    Ensure accuracy and clarity in your results.
    """

    input_text = st.text_area("Additional input or details (optional):")
    uploaded_file = st.file_uploader("Upload an image of your meal:", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.markdown('<div class="image-container">', unsafe_allow_html=True)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if st.button("Analyze Image", key="calorie_button"):
        if uploaded_file is None:
            st.error("Please upload an image to analyze.")
        else:
            try:
                image_data = input_image_setup(uploaded_file)
                full_prompt = f"{input_prompt}\n\nAdditional Input: {input_text}" if input_text else input_prompt
                response = get_gemini_response(image_data, full_prompt)
                st.success("Analysis Complete!")
                st.write(response)

                # Log meal details
                if "meal_logs" not in st.session_state:
                    st.session_state["meal_logs"] = []
                st.session_state["meal_logs"].append({
                    "meal_name": input_text or "Unnamed Meal",
                    "response": response
                })

            except Exception as e:
                st.error(f"Error: {e}")

# ---- Tab 2: BMI Calculator ----
with tab2:
    st.markdown('<div class="card"><h3>📏 BMI Calculator</h3></div>', unsafe_allow_html=True)
    st.write("Calculate your Body Mass Index (BMI) to understand your health status.")

    weight_bmi = st.number_input("Enter your weight (in kilograms):", min_value=1.0, step=0.1, key="weight_bmi")
    height_bmi = st.number_input("Enter your height (in meters):", min_value=0.5, step=0.01, key="height_bmi")

    if st.button("Calculate BMI", key="bmi_button"):
        if height_bmi > 0:
            bmi = weight_bmi / (height_bmi ** 2)
            st.subheader(f"Your BMI: {bmi:.2f}")

            if bmi < 18.5:
                st.info("Underweight: Aim for a balanced diet and regular meals.")
            elif 18.5 <= bmi < 24.9:
                st.success("Normal weight: Great job maintaining your health!")
            elif 25 <= bmi < 29.9:
                st.warning("Overweight: Consider regular exercise and dietary adjustments.")
            else:
                st.error("Obesity: Consult a healthcare professional for guidance.")
        else:
            st.error("Height must be greater than zero.")

# ---- Tab 3: Daily Calorie Requirement ----
with tab3:
    st.markdown('<div class="card"><h3>🔥 Daily Calorie Requirement Calculator</h3></div>', unsafe_allow_html=True)
    st.write("Determine your daily calorie needs based on your age, weight, height, and activity level.")

    age = st.number_input("Age (in years):", min_value=1, step=1, value=25, key="age_calorie")
    weight_calorie = st.number_input("Weight (in kilograms):", min_value=1.0, step=0.1, value=70.0, key="weight_calorie")
    height_calorie = st.number_input("Height (in meters):", min_value=0.5, step=0.01, value=1.75, key="height_calorie")
    gender = st.selectbox("Gender:", ["Male", "Female"], key="gender_calorie")
    activity_level = st.selectbox("Activity Level:", [
        "Sedentary (little or no exercise)",
        "Lightly active (light exercise/sports 1-3 days/week)",
        "Moderately active (moderate exercise/sports 3-5 days/week)",
        "Very active (hard exercise/sports 6-7 days/week)"
    ], key="activity_level_calorie")

    if st.button("Calculate Daily Calories", key="calorie_req_button"):
        if age > 0 and weight_calorie > 0 and height_calorie > 0:
            bmr = 10 * weight_calorie + 6.25 * (height_calorie * 100) - 5 * age + (5 if gender == "Male" else -161)
            activity_multipliers = {
                "Sedentary (little or no exercise)": 1.2,
                "Lightly active (light exercise/sports 1-3 days/week)": 1.375,
                "Moderately active (moderate exercise/sports 3-5 days/week)": 1.55,
                "Very active (hard exercise/sports 6-7 days/week)": 1.725
            }
            calorie_needs = bmr * activity_multipliers[activity_level]
            st.success(f"Your daily calorie requirement: {calorie_needs:.2f} kcal")
        else:
            st.error("Please provide valid inputs.")

# ---- Tab 4: Water Intake Calculator ----
with tab4:
    st.markdown('<div class="card"><h3>💧 Water Intake Calculator</h3></div>', unsafe_allow_html=True)
    st.write("Determine your daily water intake requirement based on your weight and activity level.")

    weight_water = st.number_input("Enter your weight (in kilograms):", min_value=1.0, step=0.1, key="weight_water")
    activity_level_water = st.selectbox("Select your activity level:", [
        "Sedentary (little or no exercise)",
        "Lightly active (light exercise/sports 1-3 days/week)",
        "Moderately active (moderate exercise/sports 3-5 days/week)",
        "Very active (hard exercise/sports 6-7 days/week)"
    ], key="activity_level_water")

    if st.button("Calculate Water Intake", key="water_button"):
        activity_multiplier = {
            "Sedentary (little or no exercise)": 30,
            "Lightly active (light exercise/sports 1-3 days/week)": 35,
            "Moderately active (moderate exercise/sports 3-5 days/week)": 40,
            "Very active (hard exercise/sports 6-7 days/week)": 45
        }
        water_needs = weight_water * activity_multiplier[activity_level_water] / 1000  # Convert to liters
        st.success(f"You should drink approximately {water_needs:.2f} liters of water daily.")
