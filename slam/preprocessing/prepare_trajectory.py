import os
import shutil
import tqdm
import pandas as pd
from pathlib import Path


def force_make_dir(column_dst_dir):
    if os.path.exists(column_dst_dir):
        shutil.rmtree(column_dst_dir)
    os.makedirs(column_dst_dir)


def work_with_parser(root, parser):
    single_frame_df = parser.run()
    single_frame_df.reset_index(drop=True, inplace=True)

    image_column_prefix = 'path_to_'
    for column in single_frame_df.columns:
        if column.startswith(image_column_prefix):
            column_dst_dir = column.lstrip(image_column_prefix)
            force_make_dir(os.path.join(root, column_dst_dir))

            for index, elem in enumerate(single_frame_df[column]):
                _, file_extension = os.path.splitext(elem)
                assert os.path.exists(elem), elem
                symlink_path = os.path.join(column_dst_dir, f'{index}{file_extension}')
                os.symlink(elem, os.path.abspath(os.path.join(root, symlink_path)))
                single_frame_df.at[index, column] = symlink_path

    return single_frame_df


def work_with_estimator(root, df, estimator):
    enriched_rows = []
    for index, row in tqdm.tqdm(df.iterrows(), total=len(df), desc='{:<20}'.format(estimator.name)):
        enriched_rows.append(estimator.run(row, root))
    enriched_df = pd.DataFrame(enriched_rows)
    return enriched_df


def create_pair_indices(single_frame_df, stride):
    if 'from_index' in single_frame_df.columns:
        first_part_indices = []
        second_part_indices = []
        for index, row in single_frame_df.iterrows():
            from_indices = row.from_index
            first_part_indices.extend(from_indices)
            second_part_indices.extend([index] * len(from_indices))
    else:
        first_part_indices = range(len(single_frame_df) - stride)
        second_part_indices = range(stride, len(single_frame_df))
    assert len(first_part_indices) == len(second_part_indices)
    return zip(first_part_indices, second_part_indices)


def transform_single_frame_df_to_paired(single_frame_df, pair_indices=None):
    first_part_indices, second_part_indices = zip(*pair_indices)
    first_part_df = single_frame_df.iloc[list(first_part_indices)].copy().reset_index(drop=True)
    second_part_df = single_frame_df.iloc[list(second_part_indices)].copy().reset_index(drop=True)
    second_part_df.rename(columns=lambda col: f'{col}_next', inplace=True)
    return pd.concat((first_part_df, second_part_df), axis=1)


def prepare_trajectory(root,
                       parser,
                       single_frame_estimators=None,
                       pair_frames_estimators=None,
                       stride=1):
    assert stride >= 1

    if not isinstance(root, Path):
        root = Path(root)
    root.mkdir(parents=True, exist_ok=True)

    if single_frame_estimators is None:
        single_frame_estimators = []
    if pair_frames_estimators is None:
        pair_frames_estimators = []

    single_frame_df = work_with_parser(root.as_posix(), parser)

    for estimator in single_frame_estimators:
        single_frame_df = work_with_estimator(root.as_posix(), single_frame_df, estimator)

    pair_indices = create_pair_indices(single_frame_df, stride)

    paired_frame_df = transform_single_frame_df_to_paired(single_frame_df, pair_indices)

    for estimator in pair_frames_estimators:
        paired_frame_df = work_with_estimator(root.as_posix(), paired_frame_df, estimator)

    return paired_frame_df
