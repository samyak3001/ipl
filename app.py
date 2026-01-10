import streamlit as st
import pickle
import pandas as pd

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="centered"
)

# ---------------- Dark Theme CSS ----------------
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
.main {
    background-color: #0E1117;
}
h1 {
    color: #FAFAFA;
}
label, .stNumberInput label, .stSelectbox label {
    color: #E5E7EB !important;
}
.footer {
    text-align: center;
    font-size: 14px;
    color: #9CA3AF;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Load Model ----------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ---------------- Header ----------------
st.markdown(
    "<h1 style='text-align:center;'>🏏 IPL Win Predictor</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------- Teams ----------------
teams = [
    "Chennai Super Kings",
    "Mumbai Indians",
    "Royal Challengers Bangalore",
    "Kolkata Knight Riders",
    "Delhi Capitals",
    "Sunrisers Hyderabad",
    "Rajasthan Royals",
    "Punjab Kings",
    "Gujarat Titans",
    "Lucknow Super Giants"
]

# ---------------- Inputs ----------------
col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox("🏏 Batting Team", teams)
    current_score = st.number_input("Current Score", 0, 300, 100)
    runs_left = st.number_input("Runs Left", 0, 300, 50)

with col2:
    bowling_team = st.selectbox("🎯 Bowling Team", teams)
    target = st.number_input("Target Score", 0, 300, 180)
    wickets_left = st.number_input("Wickets Left", 0, 10, 5)

overs_left = st.number_input("Overs Left", 0.0, 20.0, 5.0, step=0.1)

st.markdown("---")

# ---------------- Prediction ----------------
if st.button("🔮 Predict Winner", use_container_width=True):

    if batting_team == bowling_team:
        st.error("❌ Batting team and Bowling team must be different")
    else:
        input_df = pd.DataFrame(
            [[
                batting_team,
                bowling_team,
                target,
                current_score,
                runs_left,
                wickets_left,
                overs_left
            ]],
            columns=[
                "batting_team",
                "bowling_team",
                "target",
                "current_score",
                "runs_left",
                "wickets_left",
                "overs_left"
            ]
        )

        prediction = model.predict(input_df)[0]
        winning_team = batting_team if prediction == 1 else bowling_team

        st.success(f"🏆 **Winning Team: {winning_team}**")

# ---------------- Footer ----------------
st.markdown(
    "<hr><div class='footer'>Built by <b>Samyak </b></div>",
    unsafe_allow_html=True
)
