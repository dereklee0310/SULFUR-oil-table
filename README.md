# SULFUR Oil Table

A simple Python script that parses oil data from a Unity .bundle file and exports it to an Excel worksheet.

![Demo](demo.png)

## Getting Started

### Dependencies
#### pip
```
pip install -r requirements.txt
```
#### uv
```
uv sync
```

### Executing program
1. Locate Game Definitions Bundle  

Copy the following file into this project directory:
```
gamedefinitions_assets_all_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bundle
```
You can find it at:
```
C:\Program Files (x86)\Steam\steamapps\common\SULFUR\Sulfur_Data\StreamingAssets\aa\StandaloneWindows64\
```
And the project directory should looks like this now:
```
.
├── LICENSE
├── README.md
├── demo.png
├── gamedefinitions_assets_all_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bundle
├── oils.xlsx
├── parse_bundle.py
├── parse_json.py
└── requirements.txt
```

1. Extract Oil data to JSON
```
python parse_bundle.py
```
2. Convert JSON to Excel
```
python parse_json.py
```

## Acknowledgments
* [UnityPy](https://github.com/K0lb3/UnityPy/tree/master)