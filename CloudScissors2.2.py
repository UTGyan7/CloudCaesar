import cohere
import streamlit as st

co = cohere.Client("FBB6grIy3MMhF1l4sYECTOliIyjcZc1UhhDO232M")  # Replace with your actual API key

def chatbot_response(user_input):
    response = co.generate(
    model='command',  # Choose the right model (like 'command' for chat)
    prompt=user_input
    )

    return (response.generations[0].text)

# Ensure session state is initialized
if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("Cloud Scissors")

for msg in st.session_state["messages"]:
    st.markdown(f"**{msg['role'].capitalize()}:** {msg['content']}")

user_input = st.text_input("You: ", "")

if st.button("Send") and user_input:
    # Get response
    response = chatbot_response(user_input)

    # Append user input and response to session state
    st.session_state["messages"].append({"role": "user", "content": user_input})
    st.session_state["messages"].append({"role": "assistant", "content": response})

    # Rerun script to display updated history
    st.experimental_rerun()
