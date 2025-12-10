"""
Extract MonoBehaviour data from Unity bundle file.
"""

import json
import sys
import re
from collections import defaultdict
from pathlib import Path
from pprint import pprint

from utils.utils import setup_logging

import UnityPy

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

logger = setup_logging("INFO")

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

    bundles = list(str(x) for x in Path("./").glob("*.bundle"))
    if not bundles:
        logger.critical(".bundle file not found, please put it in the same directory")
        sys.exit()
    if len(bundles) > 1:
        logger.warning("Found multiple .bundle files, will use the first one it found")
    logger.info("Parsing %s", bundles[0])

    env = UnityPy.load(bundles[0])
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour" and obj.serialized_type.node:
            tree = obj.read_typetree()

            if tree["m_Name"] in BLACKLIST:
                logger.debug("Ignoring %s", tree["m_Name"])
                continue
            logger.debug("Parsing %s", tree["m_Name"])

            if tree["m_Name"].startswith("Enchantment_") and not tree["m_Name"].endswith("Oil"):
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
