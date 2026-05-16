import streamlit as st
import pickle
import pandas as pd
import plotly.graph_objects as go

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="IPL Win Predictor",
    page_icon="🏏",
    layout="wide"
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

# ---------------- Load Model ----------------
with open("model.pkl", "rb") as f:
    model = pickle.load(f)

# ---------------- Title ----------------
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

    # ---------------- Fixed Over Selector ----------------
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
        left_output, right_output = st.columns([1, 1.2])

        # =================================================
        # LEFT SIDE
        # =================================================
        with left_output:

            st.markdown("## 🏆 Prediction Result")

            # Dynamic Colors
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

            # Progress Bar
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
        # RIGHT SIDE 3D GRAPH
        # =================================================
        with right_output:

            st.markdown("## 📈 3D Win Probability Graph")

            fig = go.Figure(data=[

                go.Bar(
                    x=[
                        batting_team,
                        bowling_team
                    ],

                    y=[
                        batting_win,
                        bowling_win
                    ],

                    text=[
                        f"{batting_win}%",
                        f"{bowling_win}%"
                    ],

                    textposition='auto'
                )

            ])

            fig.update_layout(

                template="plotly_dark",

                title="🏏 IPL Win Prediction",

                xaxis_title="Teams",

                yaxis_title="Winning Probability (%)",

                height=500,

                yaxis=dict(
                    range=[0, 100]
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
