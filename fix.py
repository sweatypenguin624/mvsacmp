import re
with open('vehicle-counting/pipeline/counting/main.py', 'r') as f:
    content = f.read()

# Add tqdm to the loop
if 'from tqdm import tqdm' not in content:
    content = content.replace('for frame_idx, frame in reader.frames(start_frame=start_frame):',
                              'from tqdm import tqdm\n        for frame_idx, frame in tqdm(reader.frames(start_frame=start_frame), desc="Processing frames", unit="frames"):')

# Import export_csv at the top if not there
if 'from .output import export_csv' not in content:
    content = content.replace('from pathlib import Path\n', 'from pathlib import Path\nfrom .output import export_csv\n')

# Save records
save_logic = """
    logger.info("Processing complete. Final Counts:")
    for cls_name, data in counter.counts.items():
        count = data["total"]
        logger.info(f"{cls_name}: {count}")
        
    records_csv_path = output_dir / "records.csv"
    export_csv(records, records_csv_path)
    logger.info(f"Wrote {len(records)} counting records to {records_csv_path}")
"""

if 'export_csv(records' not in content:
    content = re.sub(
        r'logger\.info\("Processing complete\. Final Counts:"\).*?logger\.info\(f"\{cls_name\}: \{count\}"\)',
        save_logic.strip(),
        content,
        flags=re.DOTALL
    )

with open('vehicle-counting/pipeline/counting/main.py', 'w') as f:
    f.write(content)
print("Patch applied.")
