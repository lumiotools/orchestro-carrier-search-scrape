import json


def merge_json_files(input_files, output_file):
    merged_data = []

    for file_path in input_files:
        with open(file_path, 'r', encoding="utf8") as f:
            data = json.load(f)
            merged_data.extend(data)

    with open(output_file, 'w') as f:
        json.dump(merged_data, f, indent=4)


input_files = ["api_docs_data_sheet_1_part_1.json",
               "api_docs_data_sheet_1.json", "api_docs_data_sheet_2.json"]

output_file = "api_docs_data.json"

merge_json_files(input_files, output_file)
