import cohere
import streamlit as st

co = cohere.Client("FBB6grIy3MMhF1l4sYECTOliIyjcZc1UhhDO232M")  # Replace with your actual API key

def chatbot_response(user_input):
    response = co.generate(
    model='command',  # Choose the right model (like 'command' for chat)
    prompt=user_input
    )

    return (response.generations[0].text)

st.title("Cloud Scissors")

user_input = st.text_input("You: ", "")
if st.button("Send"):
    response = chatbot_response(user_input)
    st.text_area("Chatbot:", response, height=100)
