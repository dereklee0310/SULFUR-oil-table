import json
import logging
from pathlib import Path
from pprint import pprint

import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder

JSON_DIR = "./output"
EXCEL_DIR = "./oils.xlsx"

NEW_COLUMNS = {
    "displayName": "Name",
    "includedInDemo": "Demo",
    "includedInEarlyAccess": "Early Access",
    "basePrice": "Base Price",
    "CostsDurability": "Costs Durability",
    "Kick": "Recoil",
    "Reload Speed": "Reload Speed",
    "Damage": "Damage",
    "Critical damage chance": "Crit Chance",
    "Disables aiming": "Disables Aiming",
    "Projectile drag multiplier": "More Drag",
    "Spread": "Spread",
    "Loot Chance Multiplier": "Loot\nChance\nMultiplier",
    "Bullet bounces": "Bullet Bounces",
    "Time scale": "Bullet Speed",
    "Damage%": "Damage%",
    "Bullet size": "Bullet Size",
    "Bullet drop": "Bullet Drop",
    "No money drops": "No Money Drops",
    "Move speed": "Move Speed",
    "Rounds per minute": "RPM",
    "Bullet Penetration": "Bullet Penetration",
    "Jump power": "Jump Power",
    "Max Durability": "Max Durability",
    "Number of projectiles": "Projectile Amount",
    "Projectile bounciness": "Projectile Bounciness",
    "Chance this consumes ammo": "Ammo Consume Chance",
    "Chance to consume extra ammo": "Chance to Consume Extra Ammo",
    "No organs drop": "No Organs Drop",
    "Durability Per Shot": "Durability Per Shot",
    "Projectile force multiplier": "Projectile Force Multiplier",
    "Accuracy when moving": "Accuracy When Moving",
    "Enchantment Random Oil": "Enchantment Random Oil",
}

format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, force=True, format=format, datefmt=datefmt)
logger = logging.getLogger(__name__)


def get_oil_filenames():
    return [file for file in Path(JSON_DIR).glob("Enchantment_*Oil*.json")]


def get_oil_info(filename):
    # Enchantment_*Oil
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)

    enchantment_id = data["appliesEnchantment"]["m_PathID"]
    enchantment_info = get_enchantment_info(id_to_filename[str(enchantment_id)])
    logger.info("Parsing %s", data["displayName"])
    info = {
        "displayName": data["displayName"],
        "includedInDemo": data["includedInDemo"],
        "includedInEarlyAccess": data["includedInEarlyAccess"],
        "basePrice": data["basePrice"],
        **enchantment_info,
    }
    return info


def get_enchantment_info(filename):
    # EnchantmentDefinition_*Oil
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
    return {
        "CostsDurability": data["CostsDurability"],
        # "IsElemental": data["IsElemental"],
        **get_modifiers_info(data["modifiersApplied"]),
    }


def get_modifiers_info(modifiers):
    results = {}
    for modifier in modifiers:
        name = id_to_item_name[str(modifier["attribute"]["m_PathID"])]
        # 100: boolean/add, 200: multiplier, 300: bullet size
        mod_type = modifier["modType"]
        value = modifier["value"]
        if name == "Damage" and mod_type == 200:
            results["Damage%"] = value
        results[name] = value

    return results


if __name__ == "__main__":
    oil_filenames = get_oil_filenames()
    # print(len(enchantment_oil_files))

    with open("id_to_filename.json", "r", encoding="utf8") as f:
        id_to_filename = json.load(f)

    with open("id_to_item_name.json", "r", encoding="utf8") as f:
        id_to_item_name = json.load(f)

    data = [get_oil_info(filename) for filename in oil_filenames]

    # Beautify
    df = pd.DataFrame(data)
    df = df.rename(columns=NEW_COLUMNS)
    df["Demo"] = df["Demo"].map({1: "Yes", 0: ""})
    df["Early Access"] = df["Early Access"].map({1: "Yes", 0: ""})
    df["Costs Durability"] = df["Costs Durability"].map({"TRUE": "Yes", "": ""})
    df["Disables Aiming"] = df["Disables Aiming"].map({1: "Yes", 0: ""})
    df["No Money Drops"] = df["No Money Drops"].map({1: "Yes", 0: ""})
    df["No Organs Drop"] = df["No Organs Drop"].map({1: "Yes", 0: ""})
    df["Enchantment Random Oil"] = df["Enchantment Random Oil"]
    df = df.map(lambda x: f"{x:.2f}" if isinstance(x, float) and not pd.isna(x) else x)
    df.to_excel(EXCEL_DIR, index=False)

    # Adjust width
    wb = openpyxl.load_workbook(EXCEL_DIR)
    ws = wb["Sheet1"]
    dim_holder = DimensionHolder(worksheet=ws)
    for col in range(ws.min_column, ws.max_column + 1):
        dim_holder[get_column_letter(col)] = ColumnDimension(
            ws, min=col, max=col, width=20
        )
    ws.column_dimensions = dim_holder
    wb.save(EXCEL_DIR)
