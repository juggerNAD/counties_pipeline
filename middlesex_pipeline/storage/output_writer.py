import json

def write_record(record):
    with open("data/extracted_cases.jsonl", "a") as f:
        f.write(json.dumps(record) + "\n")
