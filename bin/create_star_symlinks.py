"""For the state-change subset, create SSv2 symlinks in ViLMA data folder."""
import os
from glob import glob
import argparse
from tqdm import tqdm


def load_json(path):
    import json
    with open(path, "r") as f:
        return json.load(f)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--src_dir", type=str, required=True)
    parser.add_argument("--dst_dir", type=str, required=True)
    parser.add_argument("--annotation", type=str, required=True)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    data = load_json(args.annotation)

    # Filter out samples of STAR dataset
    dataset = "star"
    data = {k:v for k, v in data.items() if v["dataset"] == dataset}
    print("Number of samples in STAR dataset:", len(data))

    # Create symlinks
    for k in tqdm(data, desc="Creating symlinks"):
        v = data[k]
        dataset_idx = v["video_file"]

        # Find video in the source directory
        glob_pattern = os.path.join(args.src_dir, f"{dataset_idx}.mp4")
        paths = glob(glob_pattern)
        assert len(paths) == 1
        src_path = paths[0]
        assert os.path.exists(src_path)

        # Define the destination path
        dst_path = os.path.join(args.dst_dir, os.path.basename(src_path))

        # Create symlink (if not exists and overwrite is True)
        if not os.path.exists(dst_path) or args.overwrite:
            os.symlink(src_path, dst_path)
            # print(f"Created symlink: {dst_path}")
        else:
            print(f"Symlink already exists: {dst_path}")
        
        if args.debug:
            print("Debug mode: stop after creating the first symlink.")
            break
