import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="wide"
)

# =========================================================
# DARK THEME CSS
# =========================================================
st.markdown("""
<style>

body {
    background-color: #0E1117;
}

.main {
    background-color: #0E1117;
}

h1, h2, h3 {
    color: white;
}

label {
    color: white !important;
}

.stButton>button {
    width: 100%;
    background-color: #2563EB;
    color: white;
    border-radius: 10px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    border: none;
}

.stButton>button:hover {
    background-color: #1D4ED8;
    color: white;
}

.footer {
    text-align: center;
    color: #9CA3AF;
    font-size: 14px;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD MODEL
# =========================================================
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# =========================================================
# TITLE
# =========================================================
st.markdown(
    "<h1 style='text-align:center;'>🏏 IPL Win Predictor</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

# =========================================================
# TEAMS
# =========================================================
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

# =========================================================
# INPUT SECTION
# =========================================================
left_input, right_input = st.columns(2)

with left_input:

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

with right_input:

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

    # =====================================================
    # VALID CRICKET OVERS
    # =====================================================
    overs_left = st.selectbox(
        "Overs Left",
        [
            round(i / 10, 1)
            for i in range(0, 201)
            if (i % 10) <= 5
        ],
        index=50
    )

# =========================================================
# CALCULATIONS
# =========================================================
runs_left = target - current_score

# Balls Left
balls_left = (
    int(overs_left) * 6
    + int((overs_left - int(overs_left)) * 10)
)

# Overs Completed
overs_completed = 20 - overs_left

# Current Run Rate
if overs_completed > 0:
    crr = round(current_score / overs_completed, 2)
else:
    crr = 0

# Required Run Rate
if balls_left > 0:
    rrr = round((runs_left * 6) / balls_left, 2)
else:
    rrr = 0

# =========================================================
# VALIDATIONS
# =========================================================
st.markdown("---")

if runs_left <= 0:
    st.success(f"🏆 {batting_team} already won the match!")
    st.stop()

if balls_left <= 0 and runs_left > 0:
    st.error("❌ Match Over")
    st.stop()

# =========================================================
# MATCH METRICS
# =========================================================
metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("Runs Left", runs_left)

with metric2:
    st.metric("Balls Left", balls_left)

with metric3:
    st.metric("Wickets Left", wickets_left)

with metric4:
    st.metric("Required RR", rrr)

st.markdown("---")

# =========================================================
# PREDICT BUTTON
# =========================================================
if st.button("🏏 Predict Winner"):

    # =====================================================
    # INPUT DATAFRAME
    # =====================================================
    input_df = pd.DataFrame(
        [[
            batting_team,
            bowling_team,
            target,
            current_score,
            runs_left,
            wickets_left,
            overs_left,
            balls_left,
            crr,
            rrr
        ]],
        columns=[
            "batting_team",
            "bowling_team",
            "target",
            "current_score",
            "runs_left",
            "wickets_left",
            "overs_left",
            "balls_left",
            "crr",
            "rrr"
        ]
    )

    try:

        # =================================================
        # MODEL PREDICTION
        # =================================================
        probability = model.predict_proba(input_df)

        batting_win = round(
            probability[0][1] * 100,
            2
        )

        bowling_win = round(
            probability[0][0] * 100,
            2
        )

        # =================================================
        # REALISTIC LAST OVER FIXES
        # =================================================

        # 1 run from 1+ ball
        if runs_left == 1 and balls_left >= 1:

            batting_win = 97
            bowling_win = 3

        # 2 runs from 1 ball
        elif runs_left == 2 and balls_left == 1:

            if wickets_left >= 3:
                batting_win = 65

            elif wickets_left == 2:
                batting_win = 55

            else:
                batting_win = 42

            bowling_win = 100 - batting_win

        # Boundary needed from 1 ball
        elif runs_left >= 4 and balls_left == 1:

            if wickets_left >= 5:
                batting_win = 30

            else:
                batting_win = 15

            bowling_win = 100 - batting_win

        # Easy chase
        elif runs_left <= balls_left:

            batting_win = max(
                batting_win,
                80
            )

            bowling_win = 100 - batting_win

        # Tough chase
        elif runs_left > balls_left * 2:

            bowling_win = max(
                bowling_win,
                80
            )

            batting_win = 100 - bowling_win

        # Almost impossible chase
        if wickets_left <= 1 and runs_left > 12:

            bowling_win = 95
            batting_win = 5

        # =================================================
        # OUTPUT LAYOUT
        # =================================================
        left_output, right_output = st.columns([1, 1.7])

        # =================================================
        # LEFT SIDE RESULT
        # =================================================
        with left_output:

            st.markdown("## 🏆 Prediction Result")

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

            # =================================================
            # PROGRESS BAR
            # =================================================
            st.progress(int(progress_value))

            st.markdown("### 📊 Match Stats")

            st.metric("Current RR", crr)
            st.metric("Required RR", rrr)
            st.metric("Balls Left", balls_left)

        # =================================================
        # RIGHT SIDE WORM GRAPH
        # =================================================
        with right_output:

            st.markdown("## 🪱 IPL Run Rate Worm Graph")

            overs = list(range(1, 21))

            batting_rr = []
            bowling_rr = []

            rr1 = 0
            rr2 = 0

            for i in range(20):

                # Batting curve
                rr1 += np.random.uniform(0.1, 0.6)

                if i > 14:
                    rr1 += np.random.uniform(0.2, 0.8)

                batting_rr.append(round(rr1, 2))

                # Bowling curve
                rr2 += np.random.uniform(0.1, 0.5)

                if i > 14:
                    rr2 += np.random.uniform(0.2, 0.7)

                bowling_rr.append(round(rr2, 2))

            batting_rr = np.array(batting_rr)
            bowling_rr = np.array(bowling_rr)

            # Scale curves
            batting_rr = (
                batting_rr /
                batting_rr.max()
            ) * max(crr, 1)

            bowling_rr = (
                bowling_rr /
                bowling_rr.max()
            ) * max(rrr, 1)

            # =================================================
            # CREATE GRAPH
            # =================================================
            fig = go.Figure()

            # Batting line
            fig.add_trace(

                go.Scatter(

                    x=overs,

                    y=batting_rr,

                    mode='lines',

                    name=batting_team,

                    line=dict(
                        width=5,
                        shape='spline'
                    )
                )
            )

            # Bowling line
            fig.add_trace(

                go.Scatter(

                    x=overs,

                    y=bowling_rr,

                    mode='lines',

                    name=bowling_team,

                    line=dict(
                        width=5,
                        shape='spline'
                    )
                )
            )

            # =================================================
            # GRAPH LAYOUT
            # =================================================
            fig.update_layout(

                template="plotly_dark",

                title="🏏 IPL Run Rate Worm Graph",

                xaxis_title="Overs",

                yaxis_title="Run Rate",

                height=600,

                hovermode="x unified",

                legend_title="Teams",

                xaxis=dict(
                    tickmode='linear'
                )
            )

            # =================================================
            # SHOW GRAPH
            # =================================================
            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as e:

        st.error(f"Prediction Error: {e}")

# =========================================================
# FOOTER
# =========================================================
st.markdown(
    """
    <hr>
    <div class='footer'>
        Built by <b>Samyak</b>
    </div>
    """,
    unsafe_allow_html=True
)
