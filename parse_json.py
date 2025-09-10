import json
import logging
from pathlib import Path
from pprint import pprint
from collections import defaultdict

import openpyxl
import pandas as pd
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension, DimensionHolder

from utils.utils import setup_logging

JSON_DIR = "./output"
EXCEL_PATH = "./oils.xlsx"

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
    "MISC": "MISC",  # Not a built-in one, for sheet name conversion
}

logger = setup_logging()


def get_oil_filenames():
    return [file for file in Path(JSON_DIR).glob("Enchantment_*Oil*.json")]


def get_oil_info(filename):
    # Enchantment_*Oil
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)

    enchantment_id = data["appliesEnchantment"]["m_PathID"]
    enchantment_info = get_enchantment_info(id_to_filename[str(enchantment_id)])
    logger.debug("Parsing %s", data["displayName"])
    info = {
        "displayName": data["displayName"],
        "includedInDemo": "Yes" if data["includedInDemo"] == 1 else "",
        "includedInEarlyAccess": "Yes" if data["includedInEarlyAccess"] == 1 else "",
        "basePrice": data["basePrice"],
        **enchantment_info,
    }
    return info


def get_enchantment_info(filename):
    # EnchantmentDefinition_*Oil
    with open(filename, "r", encoding="utf8") as f:
        data = json.load(f)
    return {
        "CostsDurability": "Yes" if data["CostsDurability"] == 1 else "",
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
        elif name in ("No money drops", "No organs drop", "Enchantment Random Oil"):
            results[name] = "Yes" if value == 1 else ""
        else:
            results[name] = value
    return results


def get_oil_types(info):
    types = []
    checks = (
        ("Kick", lambda v: v < 0),
        ("Reload Speed", lambda v: v > 0),
        ("Damage", lambda v: v > 0),
        ("Critical damage chance", lambda v: v > 0),
        ("Spread", lambda v: v < 0),
        ("Bullet bounces", lambda v: v > 0),
        ("Time scale", lambda v: v > 0),
        ("Damage%", lambda v: v > 0),
        ("Bullet size", lambda v: v > 0),
        ("Rounds per minute", lambda v: v > 0),
        ("Bullet Penetration", lambda v: v > 0),
        ("Max Durability", lambda v: v > 0),
        ("Number of projectiles", lambda v: v > 0),
        ("Chance this consumes ammo", lambda v: v < 0),
    )
    types = [key for key, cond in checks if cond(info.get(key, 0))]
    return types if types else ["MISC"]


if __name__ == "__main__":
    logger.info("Parsing json files in %s", JSON_DIR)
    oil_filenames = get_oil_filenames()

    with open("id_to_filename.json", "r", encoding="utf8") as f:
        id_to_filename = json.load(f)
    with open("id_to_item_name.json", "r", encoding="utf8") as f:
        id_to_item_name = json.load(f)

    oil_infos = [get_oil_info(filename) for filename in oil_filenames]

    oil_groups = defaultdict(list)
    for oil_info in oil_infos:
        for type in get_oil_types(oil_info):
            oil_groups[type].append(oil_info)

    # Beautify
    with pd.ExcelWriter("oils.xlsx", engine="openpyxl") as writer:
        df = pd.DataFrame(oil_infos)
        df = df.rename(columns=NEW_COLUMNS)
        df = df.map(
            lambda x: f"{x:.2f}" if isinstance(x, float) and not pd.isna(x) else x
        )
        df.to_excel(writer, sheet_name="Comparison Table", index=False)
        for group_name, oil_infos in oil_groups.items():
            df = pd.DataFrame(oil_infos)
            df = df.rename(columns=NEW_COLUMNS)
            df = df.map(
                lambda x: f"{x:.2f}" if isinstance(x, float) and not pd.isna(x) else x
            )
            df.to_excel(writer, sheet_name=NEW_COLUMNS[group_name], index=False)

    # Adjust width
    wb = openpyxl.load_workbook(EXCEL_PATH)
    for worksheet in wb.sheetnames:
        ws = wb[worksheet]
        dim_holder = DimensionHolder(worksheet=ws)
        for col in range(ws.min_column, ws.max_column + 1):
            dim_holder[get_column_letter(col)] = ColumnDimension(
                ws, min=col, max=col, width=10
            )
        ws.column_dimensions = dim_holder
    wb.save(EXCEL_PATH)
