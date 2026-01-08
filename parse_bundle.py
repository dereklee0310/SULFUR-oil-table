"""
Extract MonoBehaviour data from gamedefinitions_assets_all_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bundle.
"""

import json
import sys
import re
from pathlib import Path

from utils.utils import setup_logger, parse_bundle_args

import UnityPy

OUTPUT_DIR = Path("./tmp")
# Some items have incorrect m_Name that matches with this regex, don't want to touch this shit now ;)
OIL_NAME_REGEX = re.compile(r"Enchantment_(.*)Oil")

args = parse_bundle_args()
logger = setup_logger(args.logging_level)

def get_bundle():
    bundles = list(str(x) for x in Path("./").glob("gamedefinitions*.bundle"))
    if not bundles:
        logger.critical(".bundle file not found, please put it in the same directory")
        sys.exit()
    if len(bundles) > 1:
        logger.warning("Found multiple .bundle files, will use the first one it found")
    logger.info("Parsing '%s'", bundles[0])
    return bundles[0]


def parse_bundle():
    id_table = {"oil_ids" : []} # Record oil id on the fly
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    env = UnityPy.load(get_bundle())
    cnt = 0
    for obj in env.objects:
        if obj.type.name == "MonoBehaviour" and obj.peek_name():
            tree = obj.parse_as_dict()  # m_Structure is unpacked by UnityPy temporarily
            item_id = str(obj.path_id)
            item_name = tree["m_Name"]
            logger.debug("Parsing '%s'", item_name)

            # If the object has a displayName, it's mostly likely a pickable item, card, or achievement
            # Print oil only, but we need to dump all the json files including EnchantmentDefinition, Multipler, etc.
            if OIL_NAME_REGEX.match(item_name):
                cnt += 1
                logger.info(f"Found oil {cnt:>3}: '%s'", item_name)
                id_table["oil_ids"].append(item_id)

            id_table[item_id] = tree

    with open(OUTPUT_DIR / "data.json", "w", encoding="utf8") as f:
        json.dump(id_table, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parse_bundle()