import streamlit as st
import pickle
import pandas as pd
import altair as alt
import plotly.express as px

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
.stButton>button {
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    height: 50px;
    font-size: 16px;
    font-weight: bold;
    border: none;
}
.stButton>button:hover {
    background-color: #1D4ED8;
    color: white;
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
    batting_team = st.selectbox(
        "🏏 Batting Team",
        teams
    )

    current_score = st.number_input(
        "Current Score",
        min_value=0,
        max_value=300,
        value=100
    )

    target = st.number_input(
        "Target Score",
        min_value=1,
        max_value=300,
        value=180
    )

with col2:
    bowling_team = st.selectbox(
        "🎯 Bowling Team",
        [team for team in teams if team != batting_team]
    )

    wickets_left = st.number_input(
        "Wickets Left",
        min_value=0,
        max_value=10,
        value=5
    )

    # ---------------- Fixed Over Input ----------------
    overs_left = st.selectbox(
        "Overs Left",
        [
            round(i / 10, 1)
            for i in range(0, 201)
            if (i % 10) <= 5
        ],
        index=50
    )

# ---------------- Calculations ----------------
runs_left = target - current_score

# ---------------- Validation ----------------
st.markdown("---")

if runs_left < 0:
    st.success(f"🏆 {batting_team} already won the match!")
    st.stop()

if overs_left <= 0 and runs_left > 0:
    st.error("❌ Match Over")
    st.stop()

# ---------------- Match Metrics ----------------
col3, col4, col5 = st.columns(3)

with col3:
    st.metric("Runs Left", runs_left)

with col4:
    st.metric("Overs Left", overs_left)

with col5:
    st.metric("Wickets Left", wickets_left)

# ---------------- Required Run Rate ----------------
balls_left = (
    int(overs_left) * 6
    + int((overs_left - int(overs_left)) * 10)
)

if balls_left > 0:
    rrr = round((runs_left * 6) / balls_left, 2)
else:
    rrr = 0

st.write(f"## Required Run Rate: {rrr}")

st.markdown("---")

# ---------------- Prediction ----------------
if st.button("🏏 Predict Winner", use_container_width=True):

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

    try:

        # ---------------- Predict Probabilities ----------------
        if hasattr(model, "predict_proba"):

            probability = model.predict_proba(input_df)

            batting_win = round(
                probability[0][1] * 100,
                2
            )

            bowling_win = round(
                probability[0][0] * 100,
                2
            )

            # ---------------- Dynamic Colors ----------------
            if batting_win > bowling_win:

                st.success(
                    f"🏏 {batting_team}: "
                    f"{batting_win}% chance to win"
                )

                st.error(
                    f"🎯 {bowling_team}: "
                    f"{bowling_win}% chance to win"
                )

                progress_value = batting_win

            else:

                st.success(
                    f"🎯 {bowling_team}: "
                    f"{bowling_win}% chance to win"
                )

                st.error(
                    f"🏏 {batting_team}: "
                    f"{batting_win}% chance to win"
                )

                progress_value = bowling_win

            # ---------------- Progress Bar ----------------
            st.progress(int(progress_value))

            # ---------------- Comparison Data ----------------
            chart_data = pd.DataFrame({
                "Team": [
                    batting_team,
                    bowling_team
                ],
                "Winning Chance": [
                    batting_win,
                    bowling_win
                ]
            })

            # ---------------- 3D Style Graph ----------------
            fig = px.bar(
                chart_data,
                x="Team",
                y="Winning Chance",
                color="Team",
                text="Winning Chance",
                height=500
            )

            fig.update_traces(
                texttemplate='%{text:.2f}%',
                textposition='outside'
            )

            fig.update_layout(
                title="🏆 Win Probability Comparison",
                template="plotly_dark",
                xaxis_title="Teams",
                yaxis_title="Winning Probability (%)",
                yaxis=dict(range=[0, 100])
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            prediction = model.predict(input_df)[0]

            winning_team = (
                batting_team
                if prediction == 1
                else bowling_team
            )

            st.success(
                f"🏆 Winning Team: {winning_team}"
            )

    except Exception as e:
        st.error(f"Prediction Error: {e}")

# ---------------- Footer ----------------
st.markdown(
    """
    <hr>
    <div class='footer'>
        Built by <b>Samyak</b>
    </div>
    """,
    unsafe_allow_html=True
)
