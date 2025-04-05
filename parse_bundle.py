"""
Extract MonoBehaviour data from Unity bundle file.
"""

import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from pprint import pprint

import UnityPy

SRC = "./gamedefinitions_assets_all_d7975836da373a5d7cd8a8695aeb3d27.bundle"
JSON_DIR = "./output"

# top 18: k = sorted(name_counts.items(), key=lambda x: x[1], reverse=True)[:18]
BLACKLIST = set(
    [
        "",
        "Meta And Loading Setup Node",
        "Runner",
        "Create Start Area Node",
        "Finalize Level Node",
        "Spawn Pool Objects Node",
        "Spawn Enemies Node",
        "Reg Static Units And Mutate Units Node",
        "Spawn Player Node",
        "Build Nav Mesh Node",
        "Await Nav Mesh Build Node",
        "Show Level Node",
        "Setup Loot Node",
        "Create Main Path Node",
        "Spawn Events Node",
        "Add extra rooms",
        "Add Barricades Node",
        "Add extension rooms",
    ]
)

format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, force=True, format=format, datefmt=datefmt)
logger = logging.getLogger(__name__)


def check_label_or_itemDescriptionName(tree):
    if "label" in tree and "itemDescriptionName" not in tree:
        print("Label:", tree["m_Name"], tree["label"])
    elif "label" not in tree and "itemDescriptionName" in tree:
        print("itemDescriptionName:", tree["m_Name"], tree["itemDescriptionName"])


if __name__ == "__main__":
    id_to_item_name = {}  # Superset of buff/debuffs, including misc items
    id_to_filename = {}  # Oils
    name_counts = defaultdict(int)  # Handle duplicated names, e.g., PenetrationOil
    regex = re.compile(r"Enchantment(Definition)?_(.*)Oil")

    folder = Path(JSON_DIR)
    folder.mkdir(parents=True, exist_ok=True)

    env = UnityPy.load(SRC)
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour" and obj.serialized_type.node:
            tree = obj.read_typetree()

            if tree["m_Name"] in BLACKLIST:
                logger.debug("Ignoring %s", tree["m_Name"])
                continue
            logger.info("Parsing %s", tree["m_Name"])
            # It has two name: label and itemDescriptionName,
            # Use the first one becauese some itemDescriptionName are missing,
            # But we need to rename this name later because it's ugly.
            if "label" in tree:
                id_to_item_name[obj.path_id] = tree["label"]

            filename = str(Path(JSON_DIR) / f"{tree['m_Name']}.json")
            if name_counts[tree["m_Name"]] > 0:
                count = name_counts[tree["m_Name"]]
                new_filename = str(Path(JSON_DIR) / f"{tree['m_Name']}_{count}.json")
                logger.debug("Duplicated name: %s", tree["m_Name"])
                logger.debug("Rename %s to %s", filename, new_filename)
                filename = new_filename
            name_counts[tree["m_Name"]] += 1

            id_to_filename[obj.path_id] = filename

            # m_Structure is unpacked by UnityPy temporarily
            if not regex.match(tree["m_Name"]):
                continue
            with open(filename, "w", encoding="utf8") as f:
                json.dump(tree, f, ensure_ascii=False, indent=4)

    with open("id_to_item_name.json", "w", encoding="utf8") as f:
        json.dump(id_to_item_name, f, ensure_ascii=False, indent=4)
    with open("id_to_filename.json", "w", encoding="utf8") as f:
        json.dump(id_to_filename, f, ensure_ascii=False, indent=4)
