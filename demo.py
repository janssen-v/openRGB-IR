import os
import os.path as op

import cv2
import numpy as np
import skimage.io

from pipeline import Pipeline
from utils.yacs import Config


OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def demo_test_raw():
    cfg = Config('configs/test.yaml')
    pipeline = Pipeline(cfg)

    #bayer = np.load('raw/d65.npy')
    
    raw_path = 'raw/dark/1_1.RAW'
    bayer = np.fromfile(raw_path, dtype='uint16', sep='')

    bayer = bayer.reshape((cfg.hardware.raw_height, cfg.hardware.raw_width))

    data, _ = pipeline.execute(bayer)

    output_path = op.join(OUTPUT_DIR, 'test.png')
    output = cv2.cvtColor(data['output'], cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output)

if __name__ == '__main__':
    print('Processing test raw...')
    demo_test_raw()
