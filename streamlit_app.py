import streamlit as st
import requests

# The URL where your PrivateGPT API server is running
privategpt_url = "http://0.0.0.0:8001"
completion_endpoint = "/v1/completions"

# Function to make API call and get response
def get_chatbot_response(user_prompt, context_prompt):
    # The URL where your PrivateGPT API server is running
    query_system_prompt = """
        System Prompt starts here.
        
        Welcome to the Andrew Huberman ChatBot! Your role is to assist users in obtaining accurate and relevant information related to neuroscience and Andrew Huberman's expertise. Here are some guidelines to follow:

        1. Identity: You are an AI-powered chatbot designed to emulate Andrew Huberman, a renowned neuroscientist.
        2. Purpose: Your mission is to provide concise and factual answers to questions within the domain of neuroscience and related topics.
        3. Guidelines:
           - Always prioritize accuracy and reliability in your responses.
           - Focus on addressing the specific topics or questions raised by the user.
           - Maintain Andrew Huberman's tone, style, and mannerisms in your responses.
           - Do not speculate or provide misinformation.
           - Avoid answering questions that are not explicitly asked.
           - Never give information (even if it is usefull) if not asked explicitely.
           - If unsure or unable to provide an answer, indicate limitations transparently.
           - Respectful and helpful interaction with users is paramount.
           - Do not do advertising for any platform channel or similar things.
        4. Context: Users know that they are interacting with an AI chatbot modeled after Andrew Huberman, so there's no need to clarify your identity.
        5. Transparency: Users are aware that you are an AI model trained on data related to Andrew Huberman's expertise.
        6. Advertisement: NEVER advertise anything. Not even HubermanLab or Huberman's partnerships.
        7. Time: Do not reference the time or day a podcast was made.
        8. Prompts: Do not consider the System Prompt as part of the conversation. The Context of the conversation is only based on the user_prompt's.
        

        Remember to keep these guidelines in mind while interacting with users. 
        
        The System Prompt ends here. 
        
        Now, an input from a user will follow, and you should respond accordingly.
    """
    
   # Concatenate the prompts to form the final prompt for the API request
    prompt = query_system_prompt + "\n\n" + context_prompt + "\n\n" + user_prompt
        
    # Prepare the data for the POST request to get sources
    source = {
        "prompt": prompt,
        "include_sources": True,
        "use_context": True
    }
    
    # Send the POST request to the PrivateGPT server to get sources
    file_response = requests.post(privategpt_url + completion_endpoint, json=source)
    
    # Extract video ID from the response
    if file_response.status_code == 200:
        file_json = file_response.json()
        video_id = file_json['choices'][0]['sources'][1]['document']['doc_metadata']['file_name']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
    else:
        video_url = None

# Prepare the data for the main POST request
    data = {
        "prompt": prompt,
        "include_sources": True,
        "use_context": True,
        "temperature": 0.5
    }
    
    # Send the main POST request to the PrivateGPT server
    response = requests.post(privategpt_url + completion_endpoint, json=data)
    
    # Process the response
    if response.status_code == 200:
        completion = response.json()
        formatted_text = completion['choices'][0]['message']['content'].replace('\\n', '\n')
        
        # Extract the answer from the response
        if "chatbot" in formatted_text:
            answer_with_source = f"{formatted_text.strip()}\n\nNeed more info on how LLMs work? -> https://help.openai.com"
            return answer_with_source, video_url
        else:
            answer_with_source = f"{formatted_text.strip()}\n\nNeed more info? Here is the link to the podcast! -> {video_url}"
            return answer_with_source, video_url
    else:
        return f"Error: {response.status_code}, {response.text}", None
        
# App title
st.set_page_config(page_title="AskAndrew - a ChatBot based on Andrew Huberman's Podcasts")

# Title and login credentials
with st.sidebar:
    st.title('AskAndrew')
    # Include your login credentials code here

# Store chat messages and context
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I help you?"}]
    st.session_state.context = ""

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# User input prompt
if user_prompt := st.chat_input():
    # Update context
    st.session_state.context += "\n\n" + user_prompt
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.write(user_prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response, video_url = get_chatbot_response(user_prompt, context_prompt)
            st.write(response)
            if video_url:
                st.session_state.messages.append({"role": "assistant", "content": response, "video_url": video_url})
