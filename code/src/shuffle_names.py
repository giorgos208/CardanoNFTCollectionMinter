import numpy as np

# Read first names from the file
with open("project/assets/names/first_names.txt", 'r') as f:
    Names = f.read().splitlines()

# Read last names from the file
with open("project/assets/names/last_names.txt", 'r') as g:
    Surnames = g.read().splitlines()

# Generate full names and full names without spaces
Fullnames = [f"{name} {surname}" for name in Names for surname in Surnames]
Fullnames_no_spaces = [f"{name}{surname}" for name in Names for surname in Surnames]

# Shuffle the list of full names
np.random.shuffle(Fullnames)

# Write the shuffled full names to a file
with open("project/assets/names/shuffled_full_names.txt", 'w') as f:
    f.write("\n".join(Fullnames))

# Write the shuffled full names without spaces to another file
with open("project/assets/names/shuffled_full_names_no_spaces.txt", 'w') as f:
    f.write("\n".join(Fullnames_no_spaces))
