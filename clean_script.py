import json
import string

# Base62 alphabet
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase

def to_base62(num):
    """Convert integer to base62 string."""
    if num == 0:
        return BASE62_ALPHABET[0]
    base62 = ""
    while num > 0:
        num, rem = divmod(num, 62)
        base62 = BASE62_ALPHABET[rem] + base62
    return base62

input_file = "./db/metadata_merged.jsonl"
output_file = "./db/metadata_fixed_ids.jsonl"

seen_ids = set()
duplicates_count = 0
int_ids_count = 0

with open(input_file, "r") as fin, open(output_file, "w") as fout:
    for idx, line in enumerate(fin, start=1):
        record = json.loads(line)
        id_val = record["id"]

        # Type check
        if not isinstance(id_val, str):
            int_ids_count += 1

        # Duplicate check
        if id_val in seen_ids:
            duplicates_count += 1
        else:
            seen_ids.add(id_val)

        # Convert idx to base62 and pad to length 5
        new_id = to_base62(idx).rjust(5, "0")
        record["id"] = new_id

        fout.write(json.dumps(record) + "\n")

print("📊 Process complete")
print(f"Integer-type IDs: {int_ids_count}")
print(f"Duplicate IDs: {duplicates_count}")
print(f"New file written: {output_file}")

