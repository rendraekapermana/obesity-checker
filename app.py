import streamlit as st
import joblib
import pandas as pd
import os

# Load pipeline
model_path = os.path.join(os.path.dirname(__file__), 'obesity_pipeline.pkl')
model = joblib.load(model_path)

st.set_page_config(page_title="Obesity Prediction", layout="centered")
st.title("🚶‍♂️ Obesity Category Prediction")

# Explain scales for 0-3 parameters
def explain_scale(param, value):
    explanations = {
        "FCVC": {
            0: "Never (do not consume vegetables)",
            1: "Sometimes",
            2: "Often",
            3: "Always"
        },
        "FAF": {
            0: "Never (no physical activity)",
            1: "Rarely",
            2: "Sometimes",
            3: "Always"
        },
        "TUE": {
            0: "0-1 hour using technology",
            1: "1-2 hours",
            2: "2-3 hours",
            3: "More than 3 hours"
        }
    }
    return explanations.get(param, {}).get(value, "Unknown")

# Advice generator based on all input features and prediction
def generate_advice(prediction, data):
    advices = []

    if "Obesity" in prediction:
        advices.append("• Your category indicates obesity. It is important to adopt a healthier lifestyle to reduce risks.")
        advices.append("• Consult a healthcare professional for personalized guidance.")
    elif prediction == "Overweight":
        advices.append("• You are overweight. Focus on balanced diet and regular physical activity.")
    elif "Underweight" in prediction:
        advices.append("• You are underweight. Consider increasing calorie intake and consult a healthcare professional if needed.")
    else:
        advices.append("• Your weight is within a healthy range. Maintain your current healthy habits.")

    if data["Gender"] == "Female":
        advices.append("• Women may benefit from strength training to improve metabolism.")
    else:
        advices.append("• Men should monitor muscle mass and cardiovascular health regularly.")

    if data["Age"] < 18:
        advices.append("• Since you are under 18, focus on growth-friendly nutrition and physical activities.")
    elif data["Age"] > 60:
        advices.append("• Older adults should focus on maintaining muscle mass and bone health.")

    if data["family_history_with_overweight"] == "yes":
        advices.append("• Family history indicates a higher risk; regular check-ups and healthy lifestyle are key.")
    if data["FAVC"] == "yes":
        advices.append("• Reduce frequent consumption of high-calorie foods to control weight.")
    if data["FCVC"] <= 1:
        advices.append("• Increase vegetable consumption to improve nutrient intake and digestion.")
    if data["NCP"] < 3:
        advices.append("• Consider eating 3 balanced meals daily to maintain energy levels.")
    elif data["NCP"] > 4:
        advices.append("• Avoid excessive meals to prevent unnecessary calorie intake.")
    if data["CAEC"] in ["Frequently", "Always"]:
        advices.append("• Limit snacking between meals to avoid excess calories.")
    if data["SMOKE"] == "yes":
        advices.append("• Quit smoking to improve overall health and metabolism.")
    if data["CH2O"] < 2:
        advices.append("• Increase daily water intake; aim for at least 2 liters per day.")
    if data["SCC"] == "no":
        advices.append("• Monitor calorie intake to better manage your diet.")
    if data["FAF"] <= 1:
        advices.append("• Increase physical activity frequency to at least 3 times per week.")
    if data["TUE"] >= 2:
        advices.append("• Limit sedentary time spent on technology; try to stand up and move every hour.")
    if data["CALC"] in ["Frequently", "Always"]:
        advices.append("• Reduce alcohol consumption as it adds empty calories.")
    if data["MTRANS"] in ["Automobile", "Motorbike"]:
        advices.append("• Use more active transportation like walking or biking when possible.")

    if not advices:
        advices.append("• Keep maintaining your healthy lifestyle!")

    return "\n".join(advices)

# Input form
with st.form("prediction_form"):
    st.write("Please enter the following information:")

    Gender = st.selectbox("Gender", ["Male", "Female"])
    Age = st.slider("Age", 10, 100, 25)
    Height = st.number_input("Height (cm)", value=170.0, format="%.1f")
    Weight = st.number_input("Weight (kg)", value=70)
    family_history = st.selectbox("Family history with overweight", ["yes", "no"])
    FAVC = st.selectbox("Frequent consumption of high calorie food", ["yes", "no"])
    FCVC = st.slider("Frequency of vegetable consumption (0=Never, 3=Always)", 0, 3, 2)
    NCP = st.slider("Number of main meals", 1, 5, 3)
    CAEC = st.selectbox("Consumption of food between meals", ["no", "Sometimes", "Frequently", "Always"])
    SMOKE = st.selectbox("Do you smoke?", ["yes", "no"])
    CH2O = st.slider("Daily water intake (liters)", 0.0, 10.0, 2.0)
    SCC = st.selectbox("Calories monitoring?", ["yes", "no"])
    FAF = st.slider("Physical activity frequency (0=Never, 3=Always)", 0, 3, 1)
    TUE = st.slider("Time using technology (hours) (0=0-1 hr, 3=more than 3 hrs)", 0, 3, 1)
    CALC = st.selectbox("Consumption of alcohol", ["no", "Sometimes", "Frequently", "Always"])
    MTRANS = st.selectbox("Transportation used", ["Public_Transportation", "Walking", "Automobile", "Motorbike", "Bike"])

    submitted = st.form_submit_button("Predict")

if submitted:
    input_df = pd.DataFrame([{
        "Gender": Gender,
        "Age": Age,
        "Height": Height,
        "Weight": Weight,
        "family_history_with_overweight": family_history,
        "FAVC": FAVC,
        "FCVC": FCVC,
        "NCP": NCP,
        "CAEC": CAEC,
        "SMOKE": SMOKE,
        "CH2O": CH2O,
        "SCC": SCC,
        "FAF": FAF,
        "TUE": TUE,
        "CALC": CALC,
        "MTRANS": MTRANS
    }])

    # Model prediction
    prediction = model.predict(input_df)[0]

    # BMI Calculation and rule-based adjustment
    bmi = Weight / ((Height / 100) ** 2)

    if bmi < 16:
        prediction = "Severely Underweight"
    elif 16 <= bmi < 18.5:
        prediction = "Underweight"
    elif 18.5 <= bmi < 25:
        prediction = "Normal Weight"
    elif 25 <= bmi < 30:
        prediction = "Overweight"
    elif 30 <= bmi < 35:
        prediction = "Obesity I"
    elif 35 <= bmi < 40:
        prediction = "Obesity II"
    else:
        prediction = "Obesity III"

    st.success(f"✅ Obesity category prediction: **{prediction}**")

    st.markdown(f"### BMI: {bmi:.2f}")

    st.markdown("### Input Explanation:")
    st.markdown(f"- Frequency of vegetable consumption: {explain_scale('FCVC', FCVC)}")
    st.markdown(f"- Physical activity frequency: {explain_scale('FAF', FAF)}")
    st.markdown(f"- Time using technology: {explain_scale('TUE', TUE)}")
    st.markdown(f"- Daily water intake: {CH2O:.1f} liters")

    advice_text = generate_advice(prediction, {
        "Gender": Gender,
        "Age": Age,
        "family_history_with_overweight": family_history,
        "FAVC": FAVC,
        "FCVC": FCVC,
        "NCP": NCP,
        "CAEC": CAEC,
        "SMOKE": SMOKE,
        "CH2O": CH2O,
        "SCC": SCC,
        "FAF": FAF,
        "TUE": TUE,
        "CALC": CALC,
        "MTRANS": MTRANS,
    })
    
    st.markdown("### Personalized Advice:")
    st.text(advice_text)

