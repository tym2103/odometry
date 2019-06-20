import unittest
import __init_path__
import env
import os
from pathlib import Path
from odometry.preprocessing.parsers import (KITTIParser,
                                            TUMParser,
                                            RetailBotParser,
                                            DISCOMANParser)
from odometry.preprocessing import estimators as est
from odometry.preprocessing.prepare_trajectory import prepare_trajectory

env.DATASET_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'minidataset')


class TestDatasets(unittest.TestCase):

    def prepare_estimators(self, height, width):

        weights_dir_path = Path(env.PROJECT_PATH)/'weights'
        weights_file = 'pwcnet.ckpt-595000'
        self.assertTrue(list(weights_dir_path.glob(weights_file + '*')))
        optical_flow_checkpoint = (weights_dir_path/weights_file).as_posix()

        weights_file = 'model-199160'
        self.assertTrue(list(weights_dir_path.glob(weights_file + '*')))
        depth_checkpoint = (weights_dir_path/weights_file).as_posix()

        quaternion2euler_estimator = est.Quaternion2EulerEstimator(input_col=['q_w', 'q_x', 'q_y', 'q_z'],
                                                                   output_col=['euler_x', 'euler_y', 'euler_z'])

        struct2depth_estimator = est.Struct2DepthEstimator(input_col='path_to_rgb',
                                                           output_col='path_to_depth',
                                                           sub_dir='depth',
                                                           checkpoint=depth_checkpoint,
                                                           height=height,
                                                           width=width)

        input_col = ['euler_x', 'euler_y', 'euler_z', 't_x', 't_y', 't_z']
        input_col.extend([col + '_next' for col in input_col])
        output_col = input_col
        global2relative_estimator = est.Global2RelativeEstimator(input_col=input_col, output_col=output_col)

        pwcnet_estimator = est.PWCNetEstimator(input_col=['path_to_rgb', 'path_to_rgb_next'],
                                               output_col='path_to_optical_flow',
                                               sub_dir='optical_flow',
                                               checkpoint=optical_flow_checkpoint,
                                               height=height,
                                               width=width)

        single_frame_estimators = [quaternion2euler_estimator, struct2depth_estimator]
        pair_frames_estimators = [global2relative_estimator, pwcnet_estimator]

        return single_frame_estimators, pair_frames_estimators

    def assert_df(self, df, trajecotry_dir, num_files):

        self.assertTrue(len(df['path_to_rgb']) == (num_files - 1), )
        for path in df['path_to_rgb']:
            self.assertTrue(os.path.isfile(os.path.join(trajecotry_dir, path)))
        self.assertTrue(os.path.isfile(os.path.join(trajecotry_dir, df['path_to_rgb_next'].iloc[-1])))

        self.assertTrue(len(df['path_to_depth']) == (num_files - 1))
        for path in df['path_to_depth']:
            self.assertTrue(os.path.isfile(os.path.join(trajecotry_dir, path)))
        self.assertTrue(os.path.isfile(os.path.join(trajecotry_dir, df['path_to_depth_next'].iloc[-1])))

        self.assertTrue(len(df['path_to_optical_flow']) == (num_files - 1))
        for path in df['path_to_optical_flow']:
            self.assertTrue(os.path.isfile(os.path.join(trajecotry_dir, path)))

    def test_tum(self) -> None:
        print('Started TUM test')

        trajectory_dir = 'tum'
        dir = os.path.join(env.DATASET_PATH, 'tum_rgbd_flow/data/rgbd_dataset_freiburg2_coke')
        height, width = 480, 640
        num_files = 7
        parser = TUMParser(trajectory_dir, src_dir=dir)

        single_frame_estimators, pair_frames_estimators = self.prepare_estimators(height=height, width=width)
        df = prepare_trajectory(trajectory_dir,
                                parser=parser,
                                single_frame_estimators=single_frame_estimators,
                                pair_frames_estimators=pair_frames_estimators,
                                stride=1)

        self.assert_df(df, trajectory_dir, num_files=num_files)

    def test_discoman(self) -> None:
        print('Started DISCOMAN test')

        trajectory_dir = 'discoman'
        json_path = os.path.join(env.DATASET_PATH, 'renderbox/iros2019/dset/output/deprecated/000001/0_traj.json')
        height, width = 120, 160
        parser = DISCOMANParser(trajectory_dir, json_path=json_path)
        num_files = 5

        single_frame_estimators, pair_frames_estimators = self.prepare_estimators(height=height, width=width)
        df = prepare_trajectory(trajectory_dir,
                                parser=parser,
                                single_frame_estimators=single_frame_estimators,
                                pair_frames_estimators=pair_frames_estimators,
                                stride=1)

        self.assert_df(df, trajectory_dir, num_files=num_files)

    def test_kitti(self) -> None:
        print('Started KITTI test')
        trajectory_dir = 'kitti'
        trajectory_id = '00'
        height, width = 94, 300
        dataset_root = os.path.join(env.DATASET_PATH, 'KITTI_odometry_2012/dataset/sequences')
        parser = KITTIParser(trajectory_dir, trajectory_id=trajectory_id, dataset_root=dataset_root)
        num_files = 10

        single_frame_estimators, pair_frames_estimators = self.prepare_estimators(height=height, width=width)
        df = prepare_trajectory(trajectory_dir,
                                parser=parser,
                                single_frame_estimators=single_frame_estimators,
                                pair_frames_estimators=pair_frames_estimators,
                                stride=1)

        self.assert_df(df, trajectory_dir, num_files=num_files)

    def test_retailbot(self) -> None:
        print('Started RetailBot test')

        trajectory_dir = 'retailbot'
        dir = os.path.join(env.DATASET_PATH, 'retail_bot/meetingroom_04_rgbd_ir_imu_pose')
        height, width = 480, 640
        parser = RetailBotParser(trajectory_dir, src_dir=dir)
        num_files = 2

        single_frame_estimators, pair_frames_estimators = self.prepare_estimators(height=height, width=width)
        df = prepare_trajectory(trajectory_dir,
                                parser=parser,
                                single_frame_estimators=single_frame_estimators,
                                pair_frames_estimators=pair_frames_estimators,
                                stride=1)

        self.assert_df(df, trajectory_dir, num_files=num_files)