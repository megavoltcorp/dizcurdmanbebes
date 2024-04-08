import os
import random
import json
import shutil

def shuffle_and_rename(images_dir, metadata_dir, project_name, base_uri="[[baseUri]]"):
    # Get all image filenames sorted numerically
    image_files = sorted(os.listdir(images_dir), key=lambda f: int(os.path.splitext(f)[0]))
    total_files = len(image_files)

    # Generate new shuffled indices
    shuffled_indices = list(range(1, total_files + 1))
    random.shuffle(shuffled_indices)

    # Rename image files to temporary names to avoid conflicts
    temp_image_format = "temp_{}.png"
    for index, file in enumerate(image_files):
        temp_name = temp_image_format.format(index + 1)
        shutil.move(os.path.join(images_dir, file), os.path.join(images_dir, temp_name))

    # Rename metadata files to temporary names to avoid conflicts
    metadata_files = sorted(os.listdir(metadata_dir), key=lambda f: int(os.path.splitext(f)[0]))
    temp_metadata_format = "temp_{}.json"
    for index, file in enumerate(metadata_files):
        temp_name = temp_metadata_format.format(index + 1)
        shutil.move(os.path.join(metadata_dir, file), os.path.join(metadata_dir, temp_name))

    # Rename from temporary to final, ensuring images and metadata match
    for new_index, old_index in enumerate(shuffled_indices, 1):
        # Handle images
        old_image_name = temp_image_format.format(old_index)
        new_image_name = f"{new_index}.png"
        shutil.move(os.path.join(images_dir, old_image_name), os.path.join(images_dir, new_image_name))

        # Handle metadata
        old_metadata_name = temp_metadata_format.format(old_index)
        new_metadata_name = f"{new_index}.json"
        old_metadata_path = os.path.join(metadata_dir, old_metadata_name)
        new_metadata_path = os.path.join(metadata_dir, new_metadata_name)

        if os.path.exists(old_metadata_path):
            with open(old_metadata_path, 'r') as file:
                metadata = json.load(file)

            # Update the 'name' and 'image' attributes in the JSON file
            metadata['name'] = f"{project_name} #{new_index}"
            metadata['image'] = f"{base_uri}/{new_image_name}"

            with open(new_metadata_path, 'w') as file:
                json.dump(metadata, file, indent=4)

            os.remove(old_metadata_path)

def main():
    images_dir = './output/images'
    metadata_dir = './output/metadata'
    project_name = 'dizcurd manbebes'
    shuffle_and_rename(images_dir, metadata_dir, project_name)

if __name__ == "__main__":
    main()
