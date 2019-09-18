import argparse
import os

import __init_path__
import env

from slam.preprocessing import prepare_dataset, get_default_dataset_parser

if __name__ == '__main__':
    parser = get_default_dataset_parser()
    parser.add_argument('--dataset_root', type=str,
                        default=os.path.join(env.DATASET_PATH, 'EuRoC')),
    parser.add_argument('--output_dir', type=str, required=True)
    args = parser.parse_args()

    prepare_dataset(dataset_type='EuRoC',
                    dataset_root=args.dataset_root,
                    output_root=args.output_dir,
                    target_size=(120, 160),
                    optical_flow_checkpoint=args.of_checkpoint,
                    stride=args.stride,
                    depth_checkpoint=args.depth_checkpoint if args.depth else None,
                    indices_root=args.indices_root,
                    matches_threshold=args.matches_threshold)
