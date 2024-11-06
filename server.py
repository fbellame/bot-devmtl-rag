import streamlit as st
from streamlit_chat import message
import os
from ingest_data import embed_doc
import io
from route import dl
from kownledge import get_chain
from langchain_core.tools import Tool
from langchain_google_community import GoogleSearchAPIWrapper
from image import generate_images
from PIL import Image

title = "Mon web BOT personnel:"
st.set_page_config(page_title=title, page_icon=":shark:")
st.header(title)

# Initialize the vector store on first load
if "vectorstore" not in st.session_state:
    with st.spinner("Vector Database: création de la base de connaissance..."):
        vectorstore = embed_doc("data")
        st.session_state["vectorstore"] = vectorstore
        search = GoogleSearchAPIWrapper()
        st.session_state["google_search"] = search
        
        def top_result(query):
            google_search = st.session_state["google_search"]
            result = google_search.results(query=query, num_results=1)
            if result:
                top_result = result[0]
                return {
                    "title": top_result.get("title"),
                    "snippet": top_result.get("snippet"),
                    "link": top_result.get("link")
                }
            else:
                return None

        search_tool = Tool(
            name="google_search",
            description="Search Google for recent results.",
            func=top_result,
        )
        st.session_state["search_tool"] = search_tool
        st.write("Base de connaissances créée avec succès!")

# Initialize the state for the last question and answer
if "last_question" not in st.session_state:
    st.session_state["last_question"] = ""
if "last_answer" not in st.session_state:
    st.session_state["last_answer"] = ""
if "last_retrieved_docs" not in st.session_state:
    st.session_state["last_retrieved_docs"] = []

# Image size selection
with st.expander("Image size"):
    size_option = st.radio("Select image size:", ("Small", "Medium", "Large"))
    size_mapping = {"Small": (256, 256), "Medium": (512, 512), "Large": (1024, 1024)}
    image_size = size_mapping[size_option]  # Get the selected size

# Function to get user input
placeholder = st.empty()
def get_text():
    input_text = placeholder.text_input("You: ", "", key="input", on_change=submit_input)
    return input_text

# Function to handle search
def search(user_input):
    search_tool = st.session_state["search_tool"]
    output = search_tool.run(user_input)
    if output:
        formatted_output = f"**{output['title']}**\n\n{output['snippet']}\n\n[Learn more]({output['link']})"
        return formatted_output
    else:
        return "No relevant search results found."

# Function to generate images
def generate_image(user_input, image_size):
    progress_bar = st.progress(0)
    images, seed = generate_images(user_input, resolution=image_size, progress_bar=progress_bar)
    saved_images = []
    for node_id, image_data_list in images.items():
        for image_data in image_data_list:
            image = Image.open(io.BytesIO(image_data))
            filename = f"outputs/{node_id}-{seed}.png"
            image.save(filename)
            st.image(image, caption=f"Generated image with prompt: '{user_input}'")
            saved_images.append(filename)
    return f"Generated images saved: {', '.join(saved_images)}"

# Function to call RAG (Retrieval-Augmented Generation)
def call_RAG(user_input):
    vectorstore = st.session_state["vectorstore"]
    chain = get_chain(vectorstore)
    output = chain.invoke(user_input)
    return output["answer"], output["retrieved_docs"]

# Main function to submit input
def submit_input():
    user_input = st.session_state["input"]
    if user_input and st.session_state["vectorstore"]:
        st.session_state["last_question"] = user_input
        st.session_state["last_answer"] = ""
        st.session_state["last_retrieved_docs"] = []

        # Route the question
        route = dl(user_input)
        if route.name == 'image':
            st.session_state["last_answer"] = generate_image(user_input, image_size)
        elif route.name is not None:
            answer, retrieved_docs = call_RAG(user_input)
            st.session_state["last_answer"] = answer
            st.session_state["last_retrieved_docs"] = retrieved_docs
        else:
            st.session_state["last_answer"] = search(user_input)

        st.session_state["input"] = ""

# Get user input
get_text()

# Display the last question and answer
if st.session_state["last_question"]:
    message(st.session_state["last_question"], is_user=True, key="last_user", avatar_style='big-smile')
    message(st.session_state["last_answer"], key="last_assistant", avatar_style='adventurer')

    # Display last references
    last_retrieved_docs = st.session_state["last_retrieved_docs"]
    if last_retrieved_docs:
        st.markdown("**Références :**")
        for j, doc in enumerate(last_retrieved_docs):
            source = doc.metadata.get('source', 'Source inconnue')
            with st.expander(f"[{j + 1}] {source}"):
                st.write(doc.page_content)
