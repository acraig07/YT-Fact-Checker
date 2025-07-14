import streamlit as st
import pandas as pd
import base64
from controller import FactCheckController
controller = FactCheckController()

st.set_page_config(
    page_title="YouTube Fact Checker",
    layout="wide",
    initial_sidebar_state="auto",
)
st.markdown(
    """
    <style>
      /* Allow main content to go up to 1200px */
      .block-container {
        max-width: 1000px !important;
        padding-left: 2rem;
        padding-right: 2rem;
      }

      /* Only style the chat input—doesn't hit other inputs */
      [data-testid="stChatInput"] input {
        width: 600px !important;
        max-width: 90vw;
      }

      /* Center your header nicely */
      h1 {
        text-align: center;
        margin-bottom: 30px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

@st.cache_resource(show_spinner=False)
def cached_fact_check(video_id):
    return controller.run_cached(video_id)

def main():
    st.markdown("""
        <style>
            /* Center title with margin below */
            h1 {
                text-align: center;
                margin-bottom: 30px;
            }
            /* Container to center content */
            .centered-container {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }
            /* Make chat input wider */
            .stChatInput input {
                width: 600px !important;
                max-width: 90vw;
            }
        </style>
    """, unsafe_allow_html=True)

    with open("assets/youtube_social_icon_white.png", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    img_html = (
        f"<img "
        f" src='data:image/png;base64,{b64}'"
        f" width='50'"
        f" style='vertical-align:middle; margin-right:10px;'"
        f"/>"
    )

    st.markdown(f"<h1>{img_html}YouTube Fact-Checker</h1>", unsafe_allow_html=True)

    with st.container():
        URL = st.chat_input("Enter a YouTube URL")

    if URL:
        with st.spinner(f"**Processing:** {URL}"):
            success, results = controller.run(URL)

        if success:
            icon_map = {'True': '✅', 'False': '❌'}

            rows = []
            for claim, votes in results.items():
                icons = ' '.join(icon_map[v] for v in votes)
                t = votes.count('True')
                f = votes.count('False')
                if t == 3:
                    verdict = 'Very Likely True'
                elif t == 2:
                    verdict = 'Likely True'
                elif f == 3:
                    verdict = 'Very Likely False'
                elif f == 2:
                    verdict = 'Likely False'
                else:
                    verdict = 'Mixed'
                rows.append({
                    'Claim': claim,
                    'Result': f'{icons}  {verdict}'
                })

            df = pd.DataFrame(rows)
            df.index = df.index + 1  # Start index at 1
            df['Claim'] = df['Claim'].str.wrap(100)
            column_config = {
                "Result": st.column_config.TextColumn(
                    "Result",
                    width="small",
                    required = True,
                ),
            }

            left, middle, right = st.columns([0.0001, 30, 0.0001])
            with middle:
                st.data_editor(
                    df,
                    column_config=column_config,
                    use_container_width=True,
                    hide_index=False,
                    disabled=True,
                    row_height=None,
                )
        else:
            st.error(results)

if __name__ == "__main__":
    main()
