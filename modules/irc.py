# File: irc.py
# Description: IR Cut Filter
# Created: 2023/05/22 06:18
# Author: Vincentius Janssen (janssen.vincentius@gmail.com)

import numpy as np
import math
from scipy.ndimage import zoom
from .basic_module import BasicModule


class IRC(BasicModule):
    
    def __init__(self, cfg):
        super().__init__(cfg)
        self.RESOLUTION = (self.cfg.hardware.raw_height, self.cfg.hardware.raw_width)
        self.cut_coef = self.params.cut_coef
        self.clip_coef = self.params.clip_coef

    def execute(self, data):
        bayer = data['bayer'].astype(np.uint32)
        #np.savetxt('output/unmod.txt', bayer, delimiter=', ', fmt='%1d')
        
        ir_subarray = bayer[1::2, 1::2]
        
        # Upscale the subarray (currently nearest neighbour for speed)
        ir_nn = np.repeat(np.repeat(ir_subarray, 2, axis=0), 2, axis=1)
        
        # Upscale the subarray (bicubic interpolation)
        #ir_nn = zoom(ir_subarray, 2, order=3)


        #np.savetxt('output/upscaled_ir.txt', ir_nn, delimiter=', ', fmt='%1d')
        
        #idata['bayer_ir'] = ir_subarray
        #data['bayer_og'] = bayer.astype(np.uint16)
        data['ir'] = ir_nn.astype(np.uint16)
        
        ir_nn = np.clip(ir_nn, 0, np.max(bayer)/self.clip_coef)
    
                
        data['bayer'] = (np.clip(bayer-(ir_nn * self.cut_coef), 0, np.max(bayer))).astype(np.uint16)