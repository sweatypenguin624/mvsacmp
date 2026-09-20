import sys
import os
import argparse
import shutil
from ultralytics import YOLO

parser = argparse.ArgumentParser()
parser.add_argument('--source', type=str, required=True, help="Path to .pt file")
parser.add_argument('--dest', type=str, required=True, help="Destination .engine file path")
args = parser.parse_args()

pt_source = args.source
pt_dest = 'historical-processor/' + os.path.basename(pt_source)

if not os.path.exists(pt_dest):
    print(f'Copying {pt_source} to {pt_dest}...')
    shutil.copy2(pt_source, pt_dest)

model = YOLO(pt_dest)

def try_export(batch_size):
    print(f'\nStarting TRT FP16 Dynamic Export with batch={batch_size}...')
    try:
        exported_path = model.export(
            format='engine',
            half=True,
            imgsz=1280,
            dynamic=True,
            batch=batch_size,
            workspace=16,
            device='0'
        )
        print(f'Success with batch={batch_size}! Exported to {exported_path}')
        return exported_path
    except Exception as e:
        print(f'Failed export with batch={batch_size}: {e}')
        return None

exported_file = None
for b in [8, 4, 1]:
    exported_file = try_export(b)
    if exported_file:
        break

if exported_file and os.path.exists(exported_file):
    print(f"Moving {exported_file} to {args.dest}")
    os.makedirs(os.path.dirname(args.dest), exist_ok=True)
    shutil.move(exported_file, args.dest)
    print("Done!")
else:
    print("Failed to export engine.")
    sys.exit(1)
