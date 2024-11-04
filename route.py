from semantic_router import Route
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer

from dotenv import *

load_dotenv(override=True)

# Route for Confoo conversation
conference = Route(
    name="/dev/mtl",
    utterances=[        
        "dev mtl",
        "/dev/mtl",
        "/dev/mtl2024",
        "conf",
        "conference",
        "champignon"
    ]
)

# Route for Image
image = Route(name="image", utterances=[
    "image",
    "génère",
    "Farid"
    ]
)

encoder = OpenAIEncoder()

routes=[conference, image]

dl = RouteLayer(encoder=encoder, routes=routes)