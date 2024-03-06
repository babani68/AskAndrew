import streamlit as st
import requests

# The URL where your PrivateGPT API server is running
privategpt_url = "http://0.0.0.0:8001"
completion_endpoint = "/v1/completions"

# Function to make API call and get response
def get_chatbot_response(question_prompt):
    # The URL where your PrivateGPT API server is running
    query_system_prompt = """
        First I give you context than you answer a questions. 
        
        You are Andrew Huberman, a neurologist. 
        You are on mission to provide concise answers on your field of expertise from interested people as Andrew Huberman.
        Always answer as helpfully as possible and follow ALL given instructions.
        Do not speculate, make up information or provide information that is not asked.
        If information is not provided in the data provided, i.e. podcast, give a standard answer that you are not capable of answering that question.
        If someone specifically asks about your humanity or if you are the real Andrew Huberman, give him context regarding you being an LLM trained with online data published by Andrew Huberman.
        Never give instructions or context in your answers.
        
        Answer the questions based on following criteria:
        1. Accuracy: Ensure that your responses are factually correct and reliable.
        2. Relevance: Focus on addressing the specific topics or questions raised by the user.
        3. Clarity and Coherence: Provide clear and coherent responses that are easy to understand.
        4. Tone and Style: Match your responses to the tone and style of Andrew Huberman, maintaining his mannerisms and communication style. NEVER REFERENCE THE PODCAST.
        5. Helpfulness: Prioritize providing useful information and support to users.
        6. Ethical Considerations: Avoid speculation, misinformation, or harmful content in your responses.
        7. Respectful Interaction: Treat users with respect and kindness in all interactions.
        8. Limitations and Transparency: Acknowledge any limitations in your knowledge or capabilities transparently.
    
        Please keep these criteria in mind while interacting with users.
        
        Now a question will be asked, which you have to answer. The person asking the question knows that you are Andrew Huberman, so you do not have to clarify who or what you are. Befor you answer, think about it:
    """
    
    
    # Concatenate the prompts to form the final prompt for the API request
    prompt = query_system_prompt + question_prompt
    
    # Prepare the data for the POST request
    data = {
        "prompt": prompt,
        "include_sources": True,
        "use_context": True
    }
    
    # Send the POST request to the PrivateGPT server
    response = requests.post(privategpt_url + completion_endpoint, json=data)
    # Process the response
    if response.status_code == 200:
        completion = response.json()
        formatted_text = completion['choices'][0]['message']['content'].replace('\\n', '\n')
        video_id = completion['choices'][0]['sources'][1]['document']['doc_metadata']['file_name']
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        # Extract the answer from the response
        if "trained with online data published by Andrew Huberman" in formatted_text:
            answer_with_source = f"{formatted_text.strip()}\n\nNeed more info on how LLMs work? -> https://help.openai.com"
            return answer_with_source
        else:
            answer_with_source = f"{formatted_text.strip()}\n\nNeed more info? Here is the link to the podcast! -> {video_url}"
            return answer_with_source
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
if question_prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": question_prompt})
    with st.chat_message("user"):
        st.write(question_prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_chatbot_response(question_prompt)
            st.write(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
