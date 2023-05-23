# File: jbf.py
# Description: Joint Bilateral Guided Filtering (IR)
# Created: 2022/05/23 07:57
# Author: Vincentius Janssen (janssen.vincentius@gmail.com)

import numpy as np
from scipy.ndimage import gaussian_filter
from .basic_module import BasicModule, register_dependent_modules


@register_dependent_modules(['irc', 'csc'])
class JBF(BasicModule):
    def execute(self, data):
        
        #filtered_guide = gaussian_filter(data['y_image'], 1.0)
        filtered_guide = gaussian_filter(data['y_image'], 1.0)
        guide_map = filtered_guide - data['ir']
        output = data['ir'] + guide_map
        data['ir'] = output.astype(np.uint8)