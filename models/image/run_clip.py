import json
import numpy as np
import torch
import torch.nn as nn
from tqdm import tqdm
import click
from transformers import AutoProcessor, AutoModel
from vl_bench.data import Dataset_v1
from vl_bench.utils import process_path


MODELS = (
    'openai/clip-vit-large-patch14',
    'openai/clip-vit-base-patch32',
)


def sample_frame_indices(clip_len, frame_sample_rate, seg_len):
    converted_len = int(clip_len * frame_sample_rate)
    if seg_len > converted_len:
        end_idx = np.random.randint(converted_len, seg_len)
    else:
        end_idx = min(converted_len, seg_len)-1
    start_idx = end_idx - converted_len
    indices = np.linspace(start_idx, end_idx, num=clip_len)
    indices = np.clip(indices, start_idx, end_idx - 1).astype(np.int64)
    return indices


@click.command()
@click.option(
    '-i', '--input-file',
    type=click.Path(exists=True, file_okay=True),
    required=True
)
@click.option(
    '-m', '--model-name',
    type=click.Choice(choices=MODELS),
    default=MODELS[0],
)
@click.option(
    '--batch-size',
    type=int,
    default=1,
)
@click.option(
    '--device',
    type=str,
    default='cuda:0' if torch.cuda.is_available() else 'cpu',
)
@click.option(
    '--quva-dir',
    type=click.Path(exists=True, dir_okay=True),
    required=False,
)
@click.option(
    '--something-something-dir',
    type=click.Path(exists=True, dir_okay=True),
    required=False,
)
@click.option(
    '--youtube-dir',
    type=click.Path(exists=True, dir_okay=True),
    required=False,
)
@click.option(
    '-o', '--output-file',
    type=click.Path(file_okay=True),
    required=True,
)
@click.option(
    '--proficiency',
    is_flag=True,
)
def main(
    input_file,
    model_name,
    batch_size,
    device,
    quva_dir,
    something_something_dir,
    youtube_dir,
    output_file,
    proficiency,
):
    # check video datasets' dirs
    assert quva_dir is not None \
        or something_something_dir is not None \
        or youtube_dir is not None
    if quva_dir is not None:
        quva_dir = process_path(quva_dir)
    if something_something_dir is not None:
        something_something_dir = process_path(something_something_dir)
    if youtube_dir is not None:
        youtube_dir = process_path(youtube_dir)
    np.random.seed(0)

    # read data
    data = Dataset_v1(
        input_file,
        quva_dir=quva_dir,
        something_something_dir=something_something_dir,
        youtube_dir=youtube_dir,
        proficiency=proficiency,
    )

    # initialize model & processor
    processor = AutoProcessor.from_pretrained(model_name)
    model = AutoModel.from_pretrained(model_name).half().to(device)
    results = dict()
    for i, item in enumerate(tqdm(data)):
        video_len = item['video'].shape[0]
        clip_len = 8  # FIXME: hardcoded
        downsampled = item['video']
        if video_len > clip_len:
            indices = sample_frame_indices(
                clip_len=clip_len,
                frame_sample_rate=1,
                seg_len=item['video'].shape[0],
            )
            downsampled = item['video'][indices]

        inputs = processor(
            text=item['raw_texts'],
            images=list(downsampled),
            return_tensors='pt',
            padding=True,
        ).to(device)
        inputs['pixel_values'] = inputs['pixel_values'].half()

        with torch.no_grad():
            output = model(**inputs)

        scores = output.logits_per_image.softmax(dim=-1).mean(dim=0)
        scores = scores.clone().cpu().tolist()
        item_id = item['item_id']
        results[item_id] = {'scores': scores}

    with open(process_path(output_file), 'w') as f:
        json.dump(results, f, indent=4)


if __name__ == "__main__":
    main()