import streamlit as st
from assistant_with_elasticsearch import create_assistant
from db_save import save_conversation
from judge import evaluate_relevance
from db_feedback import save_feedback


st.title("Ecommerce Chatbot")

# Sidebar
st.sidebar.header("Settings")

# Search type  selection
search_type = st.sidebar.selectbox("Select Search type", ["text", "vector", "hybrid"])
assistant = create_assistant(search_type)
    
user_input = st.text_input("Enter your question:")

if st.button("Ask"):
    with st.spinner("Processing..."):
        answer = assistant.rag(user_input)
        st.success("Completed!")
        st.write(answer)

        record = assistant.last_call
        st.write(f"Response time: {record.response_time:.2f}s")
        st.write(f"Prompt tokens: {record.prompt_tokens}")
        st.write(f"Completion tokens: {record.completion_tokens}")
        st.write(f"Cost: ${record.cost:.4f}")

        conversation_id = save_conversation(assistant.last_call, user_input)
        st.session_state.conversation_id = conversation_id

        relevance, explanation = evaluate_relevance(user_input, answer)
        save_feedback(conversation_id, "judge", relevance=relevance, explanation=explanation)

        st.write(f"Relevance: {relevance}")
        st.write(f"Explanation: {explanation}")

col1, col2 = st.columns(2)
with col1:
    if st.button("+1"):
        cid = st.session_state.conversation_id
        save_feedback(cid, "user", score=1)
        st.write("Thanks!")

with col2:
    if st.button("-1"):
        cid = st.session_state.conversation_id
        save_feedback(cid, "user", score=-1)
        st.write("Thanks for the feedback!")