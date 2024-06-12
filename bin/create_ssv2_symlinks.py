"""For the state-change subset, create SSv2 symlinks in ViLMA data folder."""
import os
from glob import glob
import argparse


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
    args = parser.parse_args()

    data = load_json(args.annotation)

    # Filter out samples of SSv2 dataset
    dataset = "something-something-v2"
    data = {k:v for k, v in data.items() if v["dataset"] == dataset}
    print("Number of samples in SSv2 dataset:", len(data))

    # Create symlinks
    for k in data:
        v = data[k]
        dataset_idx = v["dataset_idx"]

        # Find video in the source directory
        glob_pattern = os.path.join(args.src_dir, f"videos/*/{dataset_idx}.*")
        paths = glob(glob_pattern)
        assert len(paths) == 1
        src_path = paths[0]

        # Define the destination path
        dst_path = os.path.join(args.dst_dir, os.path.basename(src_path))

        # Create symlink (if not exists and overwrite is True)
        if not os.path.exists(dst_path) or args.overwrite:
            os.symlink(src_path, dst_path)
            # print(f"Created symlink: {dst_path}")
        else:
            print(f"Symlink already exists: {dst_path}")
