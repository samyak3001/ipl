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
    # FIXED CRICKET OVER SELECTOR
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

balls_left = (
    int(overs_left) * 6
    + int((overs_left - int(overs_left)) * 10)
)

if balls_left > 0:
    rrr = round((runs_left * 6) / balls_left, 2)
else:
    rrr = 0

# =========================================================
# VALIDATIONS
# =========================================================
st.markdown("---")

if runs_left < 0:
    st.success(f"🏆 {batting_team} already won the match!")
    st.stop()

if overs_left <= 0 and runs_left > 0:
    st.error("❌ Match Over")
    st.stop()

# =========================================================
# MATCH METRICS
# =========================================================
metric1, metric2, metric3 = st.columns(3)

with metric1:
    st.metric("Runs Left", runs_left)

with metric2:
    st.metric("Overs Left", overs_left)

with metric3:
    st.metric("Wickets Left", wickets_left)

st.markdown(
    f"""
    <h2 style='color:white;'>
    Required Run Rate: {rrr}
    </h2>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# =========================================================
# PREDICTION BUTTON
# =========================================================
if st.button("🏏 Predict Winner"):

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
        # PREDICT PROBABILITY
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
        # OUTPUT LAYOUT
        # =================================================
        left_output, right_output = st.columns([1, 1.6])

        # =================================================
        # LEFT SIDE RESULTS
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

            st.metric(
                "Runs Left",
                runs_left
            )

            st.metric(
                "Required Run Rate",
                rrr
            )

            st.metric(
                "Wickets Left",
                wickets_left
            )

        # =================================================
        # RIGHT SIDE REALISTIC WORM GRAPH
        # =================================================
        with right_output:

            st.markdown("## 🪱 IPL Worm Graph")

            # =================================================
            # OVERS
            # =================================================
            overs = list(range(1, 21))

            # =================================================
            # REALISTIC BATTING PROGRESSION
            # =================================================
            batting_progress = []

            score = 0

            for i in range(20):

                # Powerplay
                if i < 6:
                    score += np.random.randint(6, 12)

                # Middle overs
                elif i < 15:
                    score += np.random.randint(4, 10)

                # Death overs
                else:
                    score += np.random.randint(8, 16)

                batting_progress.append(score)

            # Scale to current score
            scale_factor = (
                current_score /
                batting_progress[-1]
            )

            batting_progress = [
                round(x * scale_factor, 1)
                for x in batting_progress
            ]

            # =================================================
            # REALISTIC TARGET PROGRESSION
            # =================================================
            target_progress = []

            target_score = 0

            for i in range(20):

                # Powerplay
                if i < 6:
                    target_score += np.random.randint(7, 11)

                # Middle overs
                elif i < 15:
                    target_score += np.random.randint(5, 9)

                # Death overs
                else:
                    target_score += np.random.randint(9, 15)

                target_progress.append(target_score)

            # Scale to target
            target_scale = (
                target /
                target_progress[-1]
            )

            target_progress = [
                round(x * target_scale, 1)
                for x in target_progress
            ]

            # =================================================
            # CREATE FIGURE
            # =================================================
            fig = go.Figure()

            # =================================================
            # BATTING TEAM LINE
            # =================================================
            fig.add_trace(

                go.Scatter(

                    x=overs,

                    y=batting_progress,

                    mode='lines+markers',

                    name=batting_team,

                    line=dict(
                        width=5,
                        shape='spline'
                    ),

                    marker=dict(
                        size=8
                    )
                )
            )

            # =================================================
            # TARGET LINE
            # =================================================
            fig.add_trace(

                go.Scatter(

                    x=overs,

                    y=target_progress,

                    mode='lines+markers',

                    name=bowling_team,

                    line=dict(
                        width=5,
                        shape='spline'
                    ),

                    marker=dict(
                        size=8
                    )
                )
            )

            # =================================================
            # GRAPH LAYOUT
            # =================================================
            fig.update_layout(

                template="plotly_dark",

                title="🏏 IPL Worm Graph",

                xaxis_title="Overs",

                yaxis_title="Runs",

                height=550,

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
