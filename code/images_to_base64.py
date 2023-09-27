import base64
import os
from dotenv import load_dotenv

load_dotenv()

collection_size = os.getenv('COLLECTION_SIZE')
collection_size = int(collection_size) + 1


'''for j in range(1, 5):
    with open(f"assets/images/{j}.gif", "rb") as img_file:
        my_string = base64.b64encode(img_file.read())
    my_string = str(my_string)[2:]
    my_string = my_string[:-1]
    my_string= "data:image/gif;base64,"+my_string
#print(my_string)'''
string_array = []
with open(f"assets/images/test", "rb") as img_file:
    my_string = (img_file.read())
print(my_string)
my_string= "data:image/gif;base64,"+str(my_string)
for i in range (0,len(my_string),64):
    string_array.append(my_string[i:i+64])
#string_array.append(my_string[i:len(my_string)]) not needed
j=55
with open(f"assets/ByteImages/BytesImage{j}.txt", 'w') as f:
    for line in string_array[:-1]:
        f.write(f'"{str(line)}",\n')
    f.write(f'{str(string_array[len(string_array)-1])}')
