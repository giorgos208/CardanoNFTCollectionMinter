import json

# Read ID and names from files
with open("project/assets/names/shuffled_full_names_no_spaces.txt", 'r') as h:
    array_ID = h.read().splitlines()

with open("project/assets/names/shuffled_full_names.txt", 'r') as g:
    array_names = g.read().splitlines()

# Read existing metadata
with open('project/assets/metadata/_metadata.json', 'r') as f:
    data = json.load(f)

# Iterate over the JSON object to modify it
for i in range(len(data)):
    temp_string = data[i]["image"][7:-4]
    
    # Read byte image from file
    with open(f"project/assets/ByteImages/BytesImage{temp_string}.txt", 'r') as file:
        byte_images = file.read().splitlines()

    # Update metadata
    data[i]["id"] = array_ID[i]
    data[i]["name"] = array_names[i]
    data[i]["image"] = byte_images

# Write the updated metadata to a new JSON file
with open("project/assets/metadata/final_metadata.json", "w") as outfile:
    json.dump(data, outfile)
