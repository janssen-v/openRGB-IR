# File: irc.py
# Description: IR Cut Filter
# Created: 2023/05/22 06:18
# Author: Vincentius Janssen (janssen.vincentius@gmail.com)

import numpy as np
import math
from scipy.signal import convolve2d
from scipy.ndimage import zoom
from .basic_module import BasicModule
from .helpers import pad, split_bayer, reconstruct_bayer, shift_array


class IRC(BasicModule):
    
    def __init__(self, cfg):
        super().__init__(cfg)
        self.RESOLUTION = (self.cfg.hardware.raw_height, self.cfg.hardware.raw_width)
        self.cut_coef = self.params.cut_coef
        self.clip_coef = self.params.clip_coef
        self.KERNEL_SIZE = (4,4)


        self.r_indices = (
            (0, 2), (2, 0)
        )

        self.g_indices = (
            (0, 1), (0, 3), 
            (1, 0), (1, 2),
            (2, 1), (2, 3),
            (3, 0), (3, 2)
        )

        self.b_indices = (
            (0, 0), (2, 2)
        )

        self.ir_indices = (
            (1, 1), (1, 3),
            (3, 1), (3, 3)
        )

        self.color_kernel = {
            "R" : self.r_indices,
            "G" : self.g_indices,
            "B" : self.b_indices,
            "IR": self.ir_indices
        }

    def truth_table(self, block):
        v_repetitions = math.floor(self.RESOLUTION[0] / self.KERNEL_SIZE[0])
        h_repetitions = math.floor(self.RESOLUTION[1] / self.KERNEL_SIZE[1])
        truth_table = np.tile(block, (v_repetitions, h_repetitions))
        return truth_table

    def filter_by_color(self, source, color):
        indices = self.color_kernel[color]
        kernel_truth_table = np.zeros(self.KERNEL_SIZE, dtype=bool)
        for row, col in indices:
            kernel_truth_table[row][col] = True
        return np.where(self.truth_table(kernel_truth_table), source, 0)

    def remove_channel(self, source, color):
        indices = self.color_kernel[color]
        kernel_truth_table = np.zeros(self.KERNEL_SIZE, dtype=bool)
        for row, col in indices:
            kernel_truth_table[row][col] = True
        return np.where(self.truth_table(kernel_truth_table), 0, source)

    def getIndices(self, color):
        indices = self.color_kernel[color]
        kernel_truth_table = np.zeros(self.KERNEL_SIZE, dtype=bool)
        for row, col in indices:
            kernel_truth_table[row][col] = True
        mask = np.where(self.truth_table(kernel_truth_table), 1, 0)
        return np.argwhere(mask == 1)

    # Copy IR into a new array
    # Replace IR with interpolated R
    # Replace R with interpolated B

    def execute(self, data):
        bayer = data['bayer'].astype(np.uint32)
        #np.savetxt('output/unmod.txt', bayer, delimiter=', ', fmt='%1d')
        
        ir_subarray = bayer[1::2, 1::2]
        
        # Upscale the subarray (currently nearest neighbour for speed)
        ir_nn = np.repeat(np.repeat(ir_subarray, 2, axis=0), 2, axis=1)
        
        # Upscale the subarray (bicubic interpolation)
        #ir_nn = zoom(ir_subarray, 2, order=3)


        #np.savetxt('output/upscaled_ir.txt', ir_nn, delimiter=', ', fmt='%1d')
        
        #data['bayer_ir'] = ir_subarray
        #data['bayer_og'] = bayer.astype(np.uint16)
        data['ir'] = ir_nn.astype(np.uint16)
        
        ir_nn = np.clip(ir_nn, 0, np.max(bayer)/self.clip_coef)
    
                
        data['bayer'] = (np.clip(bayer-(ir_nn * self.cut_coef), 0, np.max(bayer))).astype(np.uint16)