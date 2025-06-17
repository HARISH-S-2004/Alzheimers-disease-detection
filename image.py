import os

# Set the directory containing the jpg files
folder_path = r'C:\Users\haris\Downloads\Alzheimers-disease-detection\Dataset\Mild_Demented'

# Get a list of all jpg files in the folder
jpg_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

# Count the number of jpg files
file_count = len(jpg_files)

# Check if no jpg files are found
if file_count == 0:
    print("No JPG files found in the specified folder.")
else:
    print(f"{file_count} JPG files found. Proceeding with renaming...")

    # Sort the files to maintain a specific order (optional)
    jpg_files.sort()

    # Rename all files sequentially
    for i, filename in enumerate(jpg_files):
        new_name = f"image{i+1}.jpg"
        src = os.path.join(folder_path, filename)
        dst = os.path.join(folder_path, new_name)
        os.rename(src, dst)
        print(f"Renamed '{filename}' to '{new_name}'")

    print("Renaming completed.")
