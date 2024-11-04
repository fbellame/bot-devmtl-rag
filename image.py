import websocket  # websocket-client
import uuid
import json
import urllib.request
import urllib.parse
import random
from dotenv import load_dotenv
import os

# Step 1: Initialize the connection settings and load environment variables
load_dotenv()

# Get server address from environment variable, default to "localhost:8188" if not set
server_address = os.getenv('COMFYUI_SERVER_ADDRESS', 'localhost:8188')
client_id = str(uuid.uuid4())

# Queue prompt function
def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p, indent=4).encode('utf-8')  # Prettify JSON for print
    req = urllib.request.Request(f"https://{server_address}/prompt", data=data)
        
    return json.loads(urllib.request.urlopen(req).read())

# Get image function
def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    
    print(f"Fetching image from the server: {server_address}/view")
    print(f"Filename: {filename}, Subfolder: {subfolder}, Type: {folder_type}")
    with urllib.request.urlopen(f"https://{server_address}/view?{url_values}") as response:
        return response.read()

# Get history for a prompt ID
def get_history(prompt_id):
    print(f"Fetching history for prompt ID: {prompt_id}.")
    with urllib.request.urlopen(f"https://{server_address}/history/{prompt_id}") as response:
        return json.loads(response.read())

# Get images from the workflow
def get_images(ws, prompt, progress_bar):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}

    last_reported_percentage = 0
    
    print("Step 6: Start listening for progress updates via the WebSocket connection.")

    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'progress':
                data = message['data']
                current_progress = data['value']
                max_progress = data['max']
                percentage = int((current_progress / max_progress) * 100)

                # Only update progress every 10%
                if percentage >= last_reported_percentage + 10:
                    print(f"Progress: {percentage}% in node {data['node']}")
                    progress_bar.progress(percentage / 100)
                    last_reported_percentage = percentage

            elif message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    print("Execution complete.", "green")
                    break  # Execution is done
        else:
            continue  # Previews are binary data

    # Fetch history and images after completion
    print("Fetch the history and download the images after execution completes.")

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    print(f"Downloading image: {image['filename']} from the server.")
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
                output_images[node_id] = images_output

    return output_images

# Generate images function with customizable input
def generate_images(positive_prompt, progress_bar, steps=25, resolution=(1024, 1024)):
    # Establish WebSocket connection
    ws = websocket.WebSocket()
    ws_url = f"wss://{server_address}/ws?clientId={client_id}"
    print(f"Establishing WebSocket connection to {ws_url}")
    ws.connect(ws_url)
    
    # Load workflow from file and print it
    print("Loading the image generation workflow from 'workflow.json'.")
    with open("workflow.json", "r", encoding="utf-8") as f:
        workflow_data = f.read()

    workflow = json.loads(workflow_data)
    
    workflow["6"]["inputs"]["text"] = positive_prompt

    print(f"Setting resolution to {resolution[0]}x{resolution[1]}")
    workflow["27"]["inputs"]["width"] = resolution[0]
    workflow["27"]["inputs"]["height"] = resolution[1]

    # Set a random seed for the KSampler node
    seed = random.randint(1, 1000000000)
    print(f"Setting random seed for generation: {seed}")
    workflow["25"]["inputs"]["noise_seed"] = seed
    
    # Fetch generated images
    images = get_images(ws, workflow, progress_bar)

    # Close WebSocket connection after fetching the images
    print(f"Closing WebSocket connection to {ws_url}")
    ws.close()

    return images, seed

# Example of calling the method and saving the images
if __name__ == "__main__":
    # Step 2: User input for prompts
    positive_prompt = input("Enter the positive prompt: ")

    print("Step 2: User inputs the positive prompt for image generation.")
    input("Press Enter to continue...", "green")

    # Call the generate_images function
    images, seed = generate_images(positive_prompt)

    # Step 9: Save the images
    print("Step 9: Saving the generated images locally.")
    input("Press Enter to continue...", "green")
    
