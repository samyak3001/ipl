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
# CUSTOM CSS
# =========================================================
st.markdown("""
<style>

body {
    background-color: #0E1117;
}

.main {
    background-color: #0E1117;
}

h1,h2,h3,h4 {
    color: white;
}

label {
    color: white !important;
}

.stButton>button {
    width: 100%;
    background-color: #2563EB;
    color: white;
    border-radius: 12px;
    height: 52px;
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
    """
    <h1 style='text-align:center;'>
    🏏 IPL Win Predictor
    </h1>
    """,
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

    # VALID CRICKET OVERS
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

balls_left = (
    int(overs_left) * 6
    + int((overs_left - int(overs_left)) * 10)
)

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

if batting_team == bowling_team:
    st.error("❌ Batting and Bowling teams cannot be same")
    st.stop()

# =========================================================
# MATCH METRICS
# =========================================================
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Runs Left", max(runs_left, 0))

with m2:
    st.metric("Balls Left", balls_left)

with m3:
    st.metric("Wickets Left", wickets_left)

with m4:
    st.metric("Required RR", max(rrr, 0))

st.markdown("---")

# =========================================================
# PREDICT BUTTON
# =========================================================
if st.button("🏏 Predict Winner"):

    # =====================================================
    # MATCH RESULT CONDITIONS
    # =====================================================

    # Batting team won
    if current_score >= target:

        st.success(
            f"🏆 {batting_team} WON THE MATCH!"
        )

        st.balloons()

        st.info(
            f"{batting_team} successfully chased "
            f"{target}."
        )

        st.stop()

    # All out
    if wickets_left == 0 and current_score < target:

        st.error(
            f"❌ {batting_team} ALL OUT!"
        )

        st.success(
            f"🏆 {bowling_team} WON THE MATCH!"
        )

        st.stop()

    # Overs completed
    if balls_left <= 0 and current_score < target:

        st.success(
            f"🏆 {bowling_team} WON THE MATCH!"
        )

        st.stop()

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

        # =================================================
        # MODEL PREDICTION
        # =================================================
        probability = model.predict_proba(input_df)

        batting_win = float(probability[0][1] * 100)
        bowling_win = float(probability[0][0] * 100)

        # =================================================
        # REALISTIC CRICKET ENGINE
        # =================================================

        pressure = rrr - crr

        # -------------------------------------------------
        # WICKETS FACTOR
        # -------------------------------------------------
        if wickets_left >= 8:
            batting_win += 8

        elif wickets_left >= 6:
            batting_win += 5

        elif wickets_left >= 4:
            batting_win += 2

        elif wickets_left == 3:
            batting_win -= 3

        elif wickets_left == 2:
            batting_win -= 8

        elif wickets_left == 1:
            batting_win -= 18

        # -------------------------------------------------
        # REQUIRED RUN RATE FACTOR
        # -------------------------------------------------
        if rrr <= 6:
            batting_win += 10

        elif rrr <= 8:
            batting_win += 5

        elif rrr <= 10:
            batting_win += 0

        elif rrr <= 12:
            batting_win -= 8

        elif rrr <= 15:
            batting_win -= 15

        else:
            batting_win -= 25

        # -------------------------------------------------
        # PRESSURE FACTOR
        # -------------------------------------------------
        batting_win -= pressure * 1.5

        # -------------------------------------------------
        # LAST OVER LOGIC
        # -------------------------------------------------
        if balls_left <= 6:

            # Easy finish
            if runs_left <= 6:

                batting_win += 15

            # Tough finish
            elif runs_left >= 12:

                batting_win -= 20

        # -------------------------------------------------
        # LAST BALL SPECIAL CASES
        # -------------------------------------------------
        if balls_left == 1:

            # 1 needed
            if runs_left == 1:
                batting_win = 96

            # 2 needed
            elif runs_left == 2:

                if wickets_left >= 5:
                    batting_win = 68

                elif wickets_left >= 3:
                    batting_win = 60

                else:
                    batting_win = 45

            # Boundary needed
            elif runs_left >= 4:
                batting_win -= 20

        # -------------------------------------------------
        # EASY CHASE BONUS
        # -------------------------------------------------
        if runs_left <= balls_left:
            batting_win += 8

        # -------------------------------------------------
        # IMPOSSIBLE CHASE
        # -------------------------------------------------
        if rrr >= 20 and balls_left <= 12:
            batting_win -= 35

        # -------------------------------------------------
        # CLAMP VALUES
        # -------------------------------------------------
        batting_win = max(
            1,
            min(99, batting_win)
        )

        bowling_win = 100 - batting_win

        batting_win = round(batting_win, 2)
        bowling_win = round(bowling_win, 2)

        # =================================================
        # OUTPUT LAYOUT
        # =================================================
        left_output, right_output = st.columns([1, 1.6])

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

            st.progress(int(progress_value))

            st.markdown("### 📊 Match Stats")

            st.metric("Current RR", crr)
            st.metric("Required RR", rrr)
            st.metric("Balls Left", balls_left)

        # =================================================
        # RIGHT SIDE GRAPH
        # =================================================
        with right_output:

            st.markdown("## 🪱 IPL Run Rate Worm Graph")

            overs = list(range(1, 21))

            batting_rr = []
            bowling_rr = []

            rr1 = 0
            rr2 = 0

            for i in range(20):

                rr1 += np.random.uniform(0.1, 0.6)

                if i > 14:
                    rr1 += np.random.uniform(0.2, 0.8)

                batting_rr.append(round(rr1, 2))

                rr2 += np.random.uniform(0.1, 0.5)

                if i > 14:
                    rr2 += np.random.uniform(0.2, 0.7)

                bowling_rr.append(round(rr2, 2))

            batting_rr = np.array(batting_rr)
            bowling_rr = np.array(bowling_rr)

            batting_rr = (
                batting_rr /
                batting_rr.max()
            ) * max(crr, 1)

            bowling_rr = (
                bowling_rr /
                bowling_rr.max()
            ) * max(rrr, 1)

            # GRAPH
            fig = go.Figure()

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

            # LAYOUT
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
