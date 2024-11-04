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
        
        def top_result(query):
            result = search.results(query=query, num_results=1)
            
            if result:  # Check if there's at least one result
                top_result = result[0]  # Get the first result
                # Transform the first result to a mapping
                return {
                    "title": top_result.get("title"),
                    "snippet": top_result.get("snippet"),
                    "link": top_result.get("link")
                }
            else:
                return None  # Return None if no results are found
    
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

# Create an empty placeholder for the input
placeholder = st.empty()

# Function to get user input
def get_text():
    input_text = placeholder.text_input("You: ", "", key="input", on_change=submit_input)
    return input_text

# Function to submit input
def submit_input():
    user_input = st.session_state["input"]

    if user_input and st.session_state["vectorstore"]:
        vectorstore = st.session_state["vectorstore"]
        chain = get_chain(vectorstore)

        # Clear previous res192.168.1.223ponses when a new question is asked
        st.session_state["last_question"] = user_input
        st.session_state["last_answer"] = ""
        st.session_state["last_retrieved_docs"] = []

        # Route the question
        route = dl(user_input)
        print(route)

        if route.name == 'image':

            # Initialize Streamlit progress bar
            progress_bar = st.progress(0)
            # generate image from prompt
            images, seed = generate_images(user_input, progress_bar)

            st.session_state["last_answer"] = "L'image a été sauvegardé dans "

            for node_id in images:
                for image_data in images[node_id]:
                    image = Image.open(io.BytesIO(image_data))
                    filename = f"outputs/{node_id}-{seed}.png"
                    image.save(filename)
                    print(f"Image saved as {filename}")

                    # Display the image in Streamlit
                    caption = f"Génération d'image avec le prompt: '{user_input}'"
                    st.image(image, caption= caption)
                    st.session_state["last_answer"] = caption


        elif route.name is not None:
            print(route.name)
            # Get answer from the LLM
            output = chain.invoke(user_input)
            st.session_state["last_answer"] = output["answer"]
            st.session_state["last_retrieved_docs"] = output["retrieved_docs"]
        else:
            # use search tool (google) to reply
            search_tool = st.session_state["search_tool"]
            
            output = search_tool.run(user_input)
            
            if output:
                # Use structured output for display
                formatted_output = f"**{output['title']}**\n\n{output['snippet']}\n\n[Learn more]({output['link']})"
                st.session_state["last_answer"] = formatted_output
            else:
                st.session_state["last_answer"] = "No relevant search results found."


        # Clear input after submission
        st.session_state["input"] = ""

# Get user input (this will trigger on_change with the submit_input function)
get_text()

# Display the last question and answer
if st.session_state["last_question"]:
    # Display the user's last message
    message(st.session_state["last_question"], is_user=True, key="last_user", avatar_style='big-smile')

    # Display the assistant's last answer
    message(st.session_state["last_answer"], key="last_assistant", avatar_style='adventurer')

    # Display the last references, if any
    last_retrieved_docs = st.session_state["last_retrieved_docs"]
    if last_retrieved_docs:
        st.markdown("**Références :**")
        for j, doc in enumerate(last_retrieved_docs):
            source = doc.metadata.get('source', 'Source inconnue')
            with st.expander(f"[{j + 1}] {source}"):
                st.write(doc.page_content)

