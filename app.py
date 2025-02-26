import streamlit as st
import os
import subprocess
from src.yt import checkURL

def main():
    st.write("# YouTube Fact Checker")
    if URL := st.chat_input("Enter YouTube URL"):

        if checkURL(URL):
            st.write(f"User has sent the URL: {URL}")
        else:
            st.write(f"Invalid URL: {URL}")

if __name__ == "__main__":
    # If streamlit instance is running
    if os.environ.get("STREAMLIT_RUNNING") == "1":
        main()

    # If streamlit is not running
    else:
        os.environ["STREAMLIT_RUNNING"] = "1"  # Set the environment variable to indicate Streamlit is running
        subprocess.run(["streamlit", "run", __file__, "--server.port=5000", "--server.address=0.0.0.0"])
