# File: rgbir.py
# Description: RGBIR2BGGR
# Created: 2023/05/20 04:18
# Author: Vincentius Janssen (janssen.vincentius@gmail.com)

import numpy as np
import math
from .basic_module import BasicModule
from .helpers import pad, split_bayer, reconstruct_bayer, shift_array


class RGBIR(BasicModule):
    
    def __init__(self, cfg):
        super().__init__(cfg)
        self.RESOLUTION = (self.cfg.hardware.raw_height, self.cfg.hardware.raw_width)

    #RESOLUTION = (1944, 2592)
    KERNEL_SIZE = (4,4)

    r_indices = (
        (0, 2), (2, 0)
    )

    g_indices = (
        (0, 1), (0, 3), 
        (1, 0), (1, 2),
        (2, 1), (2, 3),
        (3, 0), (3, 2)
    )

    b_indices = (
        (0, 0), (2, 2)
    )

    ir_indices = (
        (1, 1), (1, 3),
        (3, 1), (3, 3)
    )

    color_kernel = {
        "R": r_indices,
        "G": g_indices,
        "B": b_indices,
        "IR": ir_indices
    }

    KERNEL_INDICES = {
        "r" : r_indices, # this becomes blue later
        "g" : g_indices, 
        "b" : b_indices,
        "ir" : ir_indices # this becomes red later
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
        #np.columns stack truthtable get base table
        mask = np.where(self.truth_table(kernel_truth_table), 1, 0)
        return np.argwhere(mask == 1)

    def isOdd(self, num):
        return num % 2 != 0

    def lOblique(self, array, x, y):
        numValid = 2    
        # Case: Left or top cutoff
        if x == 0 or y == 0:
            numValid -= 1
            Rl = 0
            Rr = array[y+1][x+1]
            return (Rl + Rr) / numValid
        # Case: Right or bottom cutoff
        elif x == self.RESOLUTION[1]-1 or y == self.RESOLUTION[0]-1:
            numValid -= 1
            Rl = array[y-1][x-1]
            Rr = 0
            return (Rl + Rr) / numValid
        # Case: No cutoff
        else:
            Rl = array[y-1][x-1]
            Rr = array[y+1][x+1]
            return (Rl + Rr) / numValid
        
    def rOblique(self, array, x, y):
        numValid = 2
        # Case: Bottom and right cutoff
        if x == self.RESOLUTION[1]-1 and y == self.RESOLUTION[0]-1:
            Rl = array[y-1][x-3]
            Rr = array[y-3][x-1]
            return (Rl + Rr) / 4
        # Case: Bottom cutoff
        elif y == self.RESOLUTION[0]-1:
            numValid -= 1
            Rl = 0
            Rr = array[y-1][x+1]
            return (Rl + Rr) / numValid
        # Case: Right cutoff
        elif x == self.RESOLUTION[1]-1:
            numValid -= 1
            Rl = array[y+1][x-1]
            Rr = 0
            return (Rl + Rr) / numValid
        # Case: No cutoff
        else:
            Rl = array[y+1][x-1]
            Rr = array[y-1][x+1]
            return (Rl + Rr) / numValid


    # Interpolate Red Values
    def oblique(self, array, x, y):
        if self.isOdd((x+y)/2):
            return self.rOblique(array, x, y)
        else:
            return self.lOblique(array, x, y)

    # Interpolate Blue Values
    def cross(self, array, x, y):
        numValid = 4
        
        # Case: Left cutoff
        if x == 0:
            numValid -= 1
            Bl = 0
            Br = array[y][x+2]
        # Case: Right cutoff
        elif x >= self.RESOLUTION[1]-2:
            numValid -= 1
            Bl = array[y][x-2]
            Br = 0
        # Case: No cutoff
        else:
            Bl = array[y][x-2]
            Br = array[y][x+2]
            
        # Case: Top cutoff
        if y == 0:
            numValid -= 1
            Bt = 0
            Bd = array[y+2][x]
        # Case: Bottom cutoff
        elif y >= self.RESOLUTION[0]-2:
            numValid -= 1
            Bt = array[y-2][x]
            Bd = 0
        # Case: No cutoff
        else:
            Bt = array[y-2][x]
            Bd = array[y+2][x]

        return (Bl + Br + Bt + Bd) / numValid

    # Process
    # Copy IR into a new array
    # Replace IR with interpolated R
    # Replace R with interpolated B

    def execute(self, data):
        bayer = data['bayer'].astype(np.int32)
        #np.savetxt('output/unmod.txt', bayer, delimiter=', ', fmt='%1d')
        
        for y, x in self.getIndices("IR"):
            #print("operating on ", x, y)
            bayer[y][x] = math.floor(self.oblique(bayer, x, y))
        for y, x in self.getIndices("R"):
            #print("operating on ", x, y)
            bayer[y][x] = math.floor(self.cross(bayer, x, y))
        
        #np.savetxt('output/test.txt', bayer, delimiter=', ', fmt='%1d')
        
        data['bayer'] = bayer