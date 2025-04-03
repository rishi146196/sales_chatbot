import streamlit as st
import requests

# FastAPI backend URL
FASTAPI_URL = "http://127.0.0.1:8000/chatbot/"

st.title("📦 Supply Chain Chatbot")

st.markdown("Ask about stock availability, pricing, or order status.")

# Initialize chat history if not exists
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# User input
query = st.text_input("Enter your query:")

if st.button("Ask Chatbot"):
    if query:
        response = requests.post(FASTAPI_URL, json={"query": query})

        if response.status_code == 200:
            bot_response = response.json().get("response", "No response received.")
            
            # Store query and response in chat history
            st.session_state.chat_history.append(("You", query))
            st.session_state.chat_history.append(("🤖 Chatbot", bot_response))

            # Clear input box after submission
            
            # Clear input by resetting query
            query = ""


        else:
            st.error("Error connecting to chatbot API.")
    else:
        st.warning("Please enter a query!")

# Display chat history
st.write("### Chat History")
for sender, message in st.session_state.chat_history:
    with st.chat_message(sender):
        st.markdown(f"**{sender}:** {message}")
