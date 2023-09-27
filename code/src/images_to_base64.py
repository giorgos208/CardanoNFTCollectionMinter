import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Retrieve and convert the collection size to an integer
collection_size = int(os.getenv('COLLECTION_SIZE')) + 1

# Loop through each image in the collection
for j in range(1, collection_size):
    # Read and encode the image as base64
    with open(f"project/assets/images/{j}.png", "rb") as img_file:
        encoded_image = base64.b64encode(img_file.read()).decode('utf-8')
    
    # Create the base64 image string
    base64_string = f"data:image/png;base64,{encoded_image}"
    
    # Split the base64 string into chunks of 64 characters
    string_array = [base64_string[i:i + 64] for i in range(0, len(base64_string), 64)]

    # Write the chunks into a text file
    with open(f"project/assets/ByteImages/BytesImage{j}.txt", 'w') as f:
        for line in string_array[:-1]:
            f.write(f"{line}\n")
        f.write(string_array[-1])
