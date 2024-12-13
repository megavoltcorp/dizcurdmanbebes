import os
import random
import json
import shutil

def shuffle_and_rename(images_dir, metadata_dir, project_name, base_uri="[[baseUri]]"):
    # Get the list of image files and ensure it's in numeric order
    image_files = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    image_files.sort(key=lambda x: int(os.path.splitext(x)[0]))
    
    total_files = len(image_files)
    indices = list(range(1, total_files + 1))
    shuffled_indices = random.sample(indices, len(indices))  # Shuffle indices

    # First, rename all files to a temporary name
    temp_format = "temp_{}{}"  # Temporary file name format
    for index in indices:
        os.rename(os.path.join(images_dir, f"{index}.png"), os.path.join(images_dir, temp_format.format(index, '.png')))
        os.rename(os.path.join(metadata_dir, f"{index}.json"), os.path.join(metadata_dir, temp_format.format(index, '.json')))

    # Then, rename the temporary files to their new shuffled names
    for original, shuffled in zip(indices, shuffled_indices):
        # Rename image files
        shutil.move(os.path.join(images_dir, temp_format.format(original, '.png')), 
                    os.path.join(images_dir, f"{shuffled}.png"))

        # Load, update, and rename metadata files
        temp_metadata_path = os.path.join(metadata_dir, temp_format.format(original, '.json'))
        with open(temp_metadata_path, 'r') as file:
            metadata = json.load(file)

        metadata['name'] = f"{project_name} #{shuffled}"
        metadata['image'] = f"{base_uri}/{shuffled}.png"

        with open(os.path.join(metadata_dir, f"{shuffled}.json"), 'w') as file:
            json.dump(metadata, file, indent=4)

        os.remove(temp_metadata_path)

def main():
    images_dir = './output/images'
    metadata_dir = './output/metadata'
    project_name = 'community membooors'
    shuffle_and_rename(images_dir, metadata_dir, project_name)

if __name__ == "__main__":
    main()
