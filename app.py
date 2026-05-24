import streamlit as st
import re
from collections import Counter
from datetime import datetime
import plotly.express as px
import pandas as pd

# =====================
# PAGE CONFIG
# =====================
st.set_page_config(page_title="WhatsApp Analyzer", layout="wide")

# =====================
# PREMIUM UI STYLE
# =====================
st.markdown("""
<style>
.main {background-color: #0b1220; color: #e5e7eb;}
h1, h2, h3 {color: #60a5fa;}
.block-container {padding-top: 2rem;}
</style>
""", unsafe_allow_html=True)

# =====================
# SIDEBAR
# =====================
st.sidebar.title("⚙️ Controls")
uploaded_file = st.sidebar.file_uploader("Upload WhatsApp chat (.txt)", type=["txt"])

st.title("💬 WhatsApp Premium Analyzer")
st.caption("Clean insights. Interactive charts. Real vibes.")

if uploaded_file:
    lines = uploaded_file.read().decode("utf-8").splitlines()

    pattern = r"^(\d{2}/\d{2}/\d{4}),\s(\d{1,2}:\d{2}\s[ap]m)\s-\s"

    message_count = 0
    users = Counter()
    daily_activity = Counter()
    monthly_activity = Counter()
    hour_activity = Counter()

    data = []

    for line in lines:
        match = re.match(pattern, line, re.IGNORECASE)
        if not match:
            continue

        message_count += 1

        date_str = match.group(1)
        time_str = match.group(2).lower()

        rest = line.split(" - ", 1)[1]

        if ": " in rest:
            sender, msg = rest.split(": ", 1)
        else:
            sender, msg = "unknown", ""

        users[sender] += 1

        try:
            dt = datetime.strptime(date_str + " " + time_str, "%d/%m/%Y %I:%M %p")

            daily_activity[dt.strftime("%Y-%m-%d")] += 1
            monthly_activity[dt.strftime("%Y-%m")] += 1
            hour_activity[dt.hour] += 1

            data.append({
                "date": dt.strftime("%Y-%m-%d"),
                "month": dt.strftime("%Y-%m"),
                "hour": dt.hour,
                "user": sender
            })

        except:
            continue

    df = pd.DataFrame(data)

    # =====================
    # METRICS
    # =====================
    st.subheader("📊 Overview")
    unique_days = len(daily_activity)
    avg_per_day = message_count / unique_days if unique_days else 0

    col1, col2 = st.columns(2)
    col1.metric("Total Messages", message_count)
    col2.metric("Avg Messages / Day", f"{avg_per_day:.2f}")

    # =====================
    # TOP USERS (INTERACTIVE)
    # =====================
    st.subheader("👑 Top Contributors")

    top_users = users.most_common(10)
    df_users = pd.DataFrame(top_users, columns=["User", "Messages"])

    fig_users = px.bar(df_users, x="User", y="Messages", title="Top Users")
    st.plotly_chart(fig_users, use_container_width=True)

    # =====================
    # HOURLY HEATMAP (INTERACTIVE)
    # =====================
    st.subheader("⏰ Activity by Hour")

    df_hour = df.groupby("hour").size().reset_index(name="messages")
    fig_hour = px.bar(df_hour, x="hour", y="messages", title="Messages by Hour")
    st.plotly_chart(fig_hour, use_container_width=True)

    # =====================
    # DAILY TREND
    # =====================
    st.subheader("📅 Daily Activity")

    df_daily = df.groupby("date").size().reset_index(name="messages")
    fig_daily = px.line(df_daily, x="date", y="messages", title="Daily Activity")
    st.plotly_chart(fig_daily, use_container_width=True)

    # =====================
    # MONTHLY TREND
    # =====================
    st.subheader("📆 Monthly Activity")

    df_month = df.groupby("month").size().reset_index(name="messages")
    fig_month = px.line(df_month, x="month", y="messages", title="Monthly Activity")
    st.plotly_chart(fig_month, use_container_width=True)

else:
    st.info("Upload a WhatsApp chat file from the sidebar to begin.")
