#!/usr/bin/env python

import os
import os.path as osp
import json

import numpy as np
import click
from tqdm import tqdm

from vl_bench.utils import process_path


def create_example_0_index_1_diff_full_video(
    data_dir,
    entry,
    normalized=False,
    **kwargs,
):
    """
    Generates examples from full videos / full counts.
    Foil Method: -1 and +1
    Template: 0-index
    """
    method = "0-index-1-diff-full-video"
    subset = {}
    annotations_dir = 'normalized_annotations' if normalized else 'annotations'

    # read annotations
    timestamps = np.load(osp.join(
        data_dir, annotations_dir, entry['prefix'] + '.npy'))
    count = len(timestamps)

    # create the true caption from the template
    template = entry['templates'][0]
    caption = template.replace('<number>', str(count))

    start_time, end_time = 0, int(timestamps[-1])
    item_id = f'{method}-{entry["id"]}-{start_time}-{end_time}'

    foils, foiling_methods, classes_foils = [], [], []

    # -1 foil
    foils.append(template.replace('<number>', str(count-1)))
    foiling_methods.append('-1')
    classes_foils.append(count-1)

    # +1 foil
    foils.append(template.replace('<number>', str(count+1)))
    foiling_methods.append('+1')
    classes_foils.append(count+1)

    subset[item_id] = {
        'dataset': 'QUVA',
        'original_split': 'test',
        'dataset_idx': entry['id'],
        'youtube_id': None,
        'video_file': entry['prefix'] + '.mp4',
        'start_time': start_time,
        'end_time': end_time,
        'time_unit': 'pts',
        'caption': caption,
        'foils': foils,
        'foiling_methods': foiling_methods,
        'template': template,
        'classes': count,
        'classes_foils': classes_foils,
        'normalized': normalized,
    }

    return subset


def create_examples_0_index_1_diff_n_count(
    data_dir,
    entry,
    use_digits=True,
    n_count=0,
    normalized=False,
    **kwargs,
):
    """
    Generates examples with n repetitions, specified by n_count arg.
    Foil Method: -1 and +1
    Template: 0-index
    """
    assert n_count > 0

    digits_or_spelling = "use-digits" if use_digits else "use-spelling"
    method = f"0-index-1-diff-n-count-{digits_or_spelling}"
    subset = {}
    annotations_dir = 'normalized_annotations' if normalized else 'normalized'

    # read annotations
    timestamps = np.load(osp.join(
        data_dir, annotations_dir, entry['prefix'] + '.npy'))
    total_count = len(timestamps)
    
    for i in range(0, total_count-n_count+1):
        assert i+n_count-1 < len(timestamps)
        count = n_count
        start_time = int(timestamps[i])
        end_time = int(timestamps[i+n_count-1])
        item_id = f'{method}-{entry["id"]}-{start_time}-{end_time}'

        # create the true caption from the template 
        template = entry['templates'][0]
        caption = template.replace('<number>', str(n_count))

        foils, foiling_methods, classes_foils = [], [], []

        # -1 foil
        foils.append(template.replace('<number>', str(count-1)))
        foiling_methods.append('-1')
        classes_foils.append(n_count-1)

        # +1 foil
        foils.append(template.replace('<number>', str(count+1)))
        foiling_methods.append('+1')
        classes_foils.append(count+1)

        subset[item_id] = {
            'dataset': 'QUVA',
            'original_split': 'test',
            'dataset_idx': entry['id'],
            'youtube_id': None,
            'video_file': entry['prefix'] + '.mp4',
            'start_time': start_time,
            'end_time': end_time,
            'time_unit': 'pts',
            'caption': caption,
            'foils': foils,
            'foiling_methods': foiling_methods,
            'template': template,
            'classes': count,
            'classes_foils': classes_foils,
            'normalized': normalized,
        }

    return subset


METHODS = {
    '0-index-1-diff-full-video': create_example_0_index_1_diff_full_video,
    '0_index_1_diff_n_count': create_examples_0_index_1_diff_n_count,
}


@click.command()
@click.option(
    '--input-file',
    type=click.Path(file_okay=True, exists=True, resolve_path=True),
    required=True,
)
@click.option(
    '--output-file',
    type=click.Path(writable=True, file_okay=True, resolve_path=True),
    required=True,
)
@click.option(
    '--data-dir',
    type=click.Path(dir_okay=True, exists=True, resolve_path=True),
    required=True,
)
@click.option(
    '--method',
    type=click.Choice(choices=METHODS.keys()),
    default='0-index-1-diff-full-video',
    required=True,
)
@click.option(
    '--seed',
    type=int,
    default=42,
)
@click.option(
    '--n-count',
    type=int,
    default=0,
)
@click.option(
    '--normalized/--unnormalized',
    default=True,
)
def main(
    input_file,
    output_file,
    data_dir,
    method,
    seed,
    n_count,
    normalized,
):
    input_file = process_path(input_file)
    output_file = process_path(output_file)
    data_dir = process_path(data_dir)

    with open(input_file, 'r') as f:
        raw_data = json.load(f)

    data = {}
    for _, item in tqdm(raw_data.items()):
        subset = METHODS[method](
            data_dir,
            item,
            n_count=n_count,
            normalized=normalized,
        )
        data.update(subset)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)



if __name__ == "__main__":
    main()