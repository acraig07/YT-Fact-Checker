import streamlit as st
import pandas as pd
from src.data import get_connection, load_factcheck

st.set_page_config(page_title="Data", page_icon="💾", layout="wide")
st.title("🔍 Fact-Check Archive")

@st.cache_data(ttl=60)
def list_entries():
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT id, timestamp, url FROM entries ORDER BY timestamp DESC",
        conn
    )
    conn.close()
    return df

entries_df = list_entries()
if entries_df.empty:
    st.info("No records yet.")
    st.stop()

entries_df["Select"] = False

edited = st.data_editor(
    entries_df,
    hide_index=True,
    use_container_width=True,
)

sel = edited[edited["Select"]]
if sel.shape[0] == 1:
    entry_id = int(sel.iloc[0]["id"])
    record   = load_factcheck(entry_id)

    st.markdown("---")
    st.header(f"Entry #{entry_id}")
    st.write("**URL:**", record["url"])
    st.write("**Timestamp (UTC):**", record["timestamp"])
    st.write("**LLM Models Used:**", ", ".join(record["llms"]))

    st.subheader("Claims & LLM Votes")
    df = (
        pd.DataFrame.from_dict(record["results"], orient="index",
                               columns=["LLM #1", "LLM #2", "LLM #3"])
          .reset_index()
          .rename(columns={"index": "Claim"})
    )

    icon_map = {'True': '✅ True', 'False': '❌ False'}
    df_icons = df.copy()
    for col in ["LLM #1", "LLM #2", "LLM #3"]:
        df_icons[col] = df_icons[col].map(icon_map)

    st.dataframe(
        df_icons[["Claim", "LLM #1", "LLM #2", "LLM #3"]],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("✅ Check exactly one row above to display its detail view.")

