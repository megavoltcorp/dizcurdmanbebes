import glob
import random
import json
import os
import shutil
from progress.bar import Bar
from PIL import Image
from threading import Thread
from threading import Semaphore

ASSET_FOLDER = "./assets"
assetFiles = glob.glob(f'{ASSET_FOLDER}/*.png')

class gen():
    def __init__(self):
        self.groups = [
            {
                "partTypes": ["Background", "Type", "Hat", "Mouth", "Eyes", "Nose", "Clothes"],
                "count": 350
            },
            {
                "partTypes": ["Background", "Type",  "Hair", "Mouth", "Eyes", "Nose",  "Clothes"],
                "count": 350
            },
            {
                "partTypes": ["Background", "Type", "Mouth", "Eyes", "Nose"],
                "count": 290
            },
            {
                "partTypes": ["Special"],
                "count": 7
            },
            {
                "partTypes": ["Honorary"],
                "count": 2
            },
        ]
        self.check_path_requirements()
        self.sem = Semaphore(100)
        self.project_name = 'DizcurdManBebes'
        self.description = 'Eber since I became a Dizcurd ManBebes, i jumped rite into da NFT wurld. I collerct picshurz on da inturnet, hang out wit my fwens on Discurd, an its da bestest part of my day. Bein a ManBebe means i stan tuff wit my crew. If somthin makez me mad, u bet imma post my feelz on X an tell my fwens in DMz — cuz das wut Membooors do. We stick togethur like… like buttcheeks!! No one can brake our bond, we da pudgiest crew on da inturnet!!'

    def check_path_requirements(self):
        required_paths = ['assets', 'output', 'output/images', 'output/metadata']
        for path in required_paths:
            full_path = os.path.join(os.getcwd(), path)
            if not os.path.exists(full_path):
                os.makedirs(full_path)

    def parseParts(self, partTypes):
        _allParts = {}
        for partType in partTypes:
            parts = [f for f in assetFiles if f.lower().startswith(f'{ASSET_FOLDER}/{partType.lower()}-')]
            totalRarity = 0
            parsedParts = []

            for part in parts:
                splittedPart = part.split('-')
                partName = splittedPart[1]
                rarity = splittedPart[2].replace('.png', '')
                totalRarity += int(float(rarity) * 10)
                parsedParts.append({
                    "asset": part,
                    "type": partType.lower(),
                    "name": partName,
                    "rarity": int(float(rarity) * 10),
                })

            _allParts[partType] = parsedParts

            for part in _allParts[partType]:
                part["rarity"] = part["rarity"] / (totalRarity + 1)

        return _allParts

    def getRandomPart(self, parts, type):
        partTypes = parts[type]
        normalizedParts = [partType for partType in partTypes for _ in range(int(partType["rarity"] * 1000))]
        return random.choice(normalizedParts)

    def getRandomWolf(self, partTypes, allParts, previousWolfs=[]):
        wolf = []
        for partType in partTypes:
            wolf.append(self.getRandomPart(allParts, partType))

        exists = len([g for g in previousWolfs if self.listMatch(g, wolf, 'asset')])
        return wolf if not exists else self.getRandomWolf(partTypes, allParts, previousWolfs)

    def listMatch(self, a, b, key):
        return len(a) == len(b) and all(a[i][key] == b[i][key] for i in range(len(a)))

    def saveMetadata(self, wolf, id):
        with open(f'output/metadata/{id}.json', 'w') as json_file:
            metadata = {
                "attributes": [{"trait_type": part["type"], "value": part["name"]} for part in wolf],
                "description": self.description,
                "image": f"[[baseUri]]/{id}.png",
                "name": f"{self.project_name} #{id}",
            }
            json.dump(metadata, json_file, indent=4)

    def run(self):
        file_index = 1  # Start file naming from 1 and continue across all groups
        for group in self.groups:
            partTypes = group['partTypes']
            count = group['count']
            allParts = self.parseParts(partTypes)
            wolfs = []
            bar = Bar('Randomizing', max=count, suffix='%(percent)d%%\tElapsed: %(elapsed)ds\tEta: %(eta)ds\tAVG: %(avg)s')

            for i in range(count):
                wolf = self.getRandomWolf(partTypes, allParts, wolfs)
                self.saveMetadata(wolf, file_index)
                layers = [part['asset'] for part in wolf]
                output_path = f'output/images/{file_index}.png'
                join_images(layers=layers, output=output_path, sem=self.sem).start()
                wolfs.append(wolf)
                file_index += 1  # Increment the file_index after each NFT is generated
                bar.next()
            bar.finish()
        print("NFT generation completed.")

    def randomize_output(self):
        from rando import shuffle_and_rename  # Import here to avoid circular imports
        images_dir = './output/images'
        metadata_dir = './output/metadata'
        shuffle_and_rename(images_dir, metadata_dir, self.project_name)

class join_images(Thread):
    def __init__(self, layers, output, sem):
        super().__init__()
        self.layers = layers
        self.output = output
        self.sem = sem

    def run(self):
        self.sem.acquire()
        images = [Image.open(layer).convert("RGBA") for layer in self.layers]
        base_image = images[0]
        for image in images[1:]:
            base_image = Image.alpha_composite(base_image, image)
        base_image.save(self.output, 'PNG')
        self.sem.release()

if __name__ == "__main__":
    generator = gen()
    generator.run()