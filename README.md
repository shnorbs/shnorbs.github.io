# CV Template Editor

A simple Python tool to update your HTML CV from JSON data.

## Setup
```bash
pip install -r requirements.txt
```

## Usage
```bash
python cv_editor.py import-data --input cv_data_example.json
```

## Example JSON Format
```json
{
  "contact": {
    "name": "John Doe",
    "title": "Software Engineer",
    "email": "john@example.com"
  },
  "experience": [
    {
      "position": "Developer",
      "company": "Tech Corp",
      "duration": "2023 - Present",
      "description": "Built awesome software"
    }
  ]
}
```

The tool automatically backs up your HTML file before making changes.ate Editor CLI

A simple command-line tool to import CV data from JSON files into your HTML CV template. This tool allows you to update your entire CV content by importing structured JSON data.

## Features

- 📥 **Import CV Data** - Import complete CV data from JSON files
- � **Auto Backup** - Automatically creates backups before making changes
- ✅ **JSON Validation** - Validates JSON format and shows helpful error messages


## Demo GIFs

- ![Plain Theme](assets/Plain.gif)
- ![Birds](assets/birds.gif)
- ![Waves](assets/waves.gif)
- ![fog](assets/fog.gif)

