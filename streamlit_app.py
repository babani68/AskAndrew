import streamlit as st
import requests

# The URL where your PrivateGPT API server is running
privategpt_url = "http://0.0.0.0:8001"
completion_endpoint = "/v1/completions"

# Function to make API call and get response
def get_chatbot_response(prompt):
    data = {
        "prompt": prompt,
        "include_sources": True,
        "use_context": True
    }
    response = requests.post(privategpt_url + completion_endpoint, json=data)
    if response.status_code == 200:
        completion = response.json()
        formatted_text = completion['choices'][0]['message']['content'].replace('\\n', '\n')
        video_id = completion['choices'][0]['sources'][1]['document']['doc_metadata']['file_name']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        if "trained with online data published by Andrew Huberman" in formatted_text:
            return f"{formatted_text.strip()}\n\nNeed more info on how LLMs work? -> https://help.openai.com"
        else:
            return f"{formatted_text.strip()}\n\nNeed more info? Here is the link to the podcast! -> {video_url}"
    else:
        return f"Error: {response.status_code}, {response.text}"

# App title
st.set_page_config(page_title="AskAndrew - a ChatBot based on Andrew Huberman's Podcasts")

# Title and login credentials
with st.sidebar:
    st.title('AskAndrew')
    # Include your login credentials code here

# Store chat messages
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_chatbot_response(prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
