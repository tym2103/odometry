import __init_path__

import os
from functools import partial

import __init_path__
import env

from scripts.odometry.confidence_trainer import ConfidenceTrainer
from slam.models import construct_multiscale_model


class MultiscaleWithConfidenceTrainer(ConfidenceTrainer):

    def set_model_args(self):
        self.construct_model_fn = partial(construct_multiscale_model,
                                          return_confidence=True)
        self.lr = 0.001
        self.loss = 'huber'
        self.scale_rotation = 50

    def set_dataset_args(self):
        self.x_col = ['path_to_optical_flow']
        self.y_col = ['euler_x', 'euler_y', 'euler_z', 't_x', 't_y', 't_z']
        self.image_col = ['path_to_optical_flow']
        self.load_mode = ['flow_xy']
        self.preprocess_mode = ['flow_xy']


if __name__ == '__main__':

    parser = MultiscaleWithConfidenceTrainer.get_parser()
    args = parser.parse_args()

    trainer = MultiscaleWithConfidenceTrainer(**vars(args))
    trainer.train()
