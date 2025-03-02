import streamlit as st
import requests

API_URL = "http://unified_ai_agent:8001"

st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("AI Research Assistant")

query = st.text_input("Enter your query:")
if st.button("Search AI") and query.strip():
    try:
        response = requests.post(f"{API_URL}/query", json={"query": query})
        response.raise_for_status()
        st.write("### AI Response:")
        st.write(response.json().get("response", "No response"))
    except requests.exceptions.RequestException as e:
        st.error(f"Error querying AI: {e}")

if st.button("Start Research Task") and query.strip():
    try:
        response = requests.post(f"{API_URL}/research", json={"query": query})
        response.raise_for_status()
        st.success("Research task started!")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to start research: {e}")

if st.button("Fetch ETL Data"):
    try:
        response = requests.get(f"{API_URL}/etl-data")
        response.raise_for_status()
        st.write("### ETL Data:")
        st.json(response.json())
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to fetch ETL data: {e}")
