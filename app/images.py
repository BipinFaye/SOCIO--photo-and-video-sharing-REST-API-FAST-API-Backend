from dotenv import load_dotenv
from imagekitio import ImageKit
import os

load_dotenv()

IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")

if not IMAGEKIT_PRIVATE_KEY:
    raise ValueError(
        "IMAGEKIT_PRIVATE_KEY environment variable is not set"
    )

imagekit = ImageKit(
    private_key=IMAGEKIT_PRIVATE_KEY
)
