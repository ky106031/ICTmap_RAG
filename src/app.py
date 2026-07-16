import streamlit as st

from rag_pipeline import run_pipeline


st.set_page_config(
    page_title="理科ICT GraphRAG",
    page_icon="🔬",
)

st.title("理科ICT活用 GraphRAG")
st.caption("ICT活用事例を知識グラフから検索し、根拠関係に基づいて回答します。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = st.chat_input("質問を入力してください")

if user_query:
    st.session_state.messages.append({
        "role": "user",
        "content": user_query,
    })

    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.spinner("GraphRAGで検索・回答生成中です..."):
            result = run_pipeline(user_query=user_query)
            answer = result["generated_answer"]

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
    })