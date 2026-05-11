import streamlit as st
import json

# Health endpoint check
if st.query_params.get("health") == "1":
    st.json({"status": "ok"})
    st.stop()

# Simple UI for the health check app
st.title("Health Check Service")
st.write("This app provides health monitoring for the main application.")
st.write("Use ?health=1 parameter to get health status.")
