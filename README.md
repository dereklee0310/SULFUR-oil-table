# SULFUR Oil Table

A simple script that parses SULFUR oil data from a .bundle file and exports it to an Excel worksheet.

![Demo](examples/demo.png)

## Getting Started

### Dependencies
```
uv sync
```

### Executing program
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
├── examples
├── gamedefinitions_assets_all_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.bundle
├── oils.xlsx
├── parse_bundle.py
├── parse_json.py
├── pyproject.toml
├── requirements.txt
├── utils
└── uv.lock
```

1. Extract data from .bundle and dump into `data.json`
```
uv run parse_bundle.py
```
2. Parse `data.json`
```
uv run parse_json.py
```

## Acknowledgments
* [UnityPy](https://github.com/K0lb3/UnityPy/tree/master)