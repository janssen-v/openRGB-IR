import os
import os.path as op
import getopt
import sys

import cv2
import numpy as np

from pipeline import Pipeline
from utils.yacs import Config


OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)

def colorChecker(cfg_path = 'configs/quality.yaml'):
    d65 = np.load('raw/d65.npy')
    cfg = Config(cfg_path)
    pipeline = Pipeline(cfg)
    d65 = d65.reshape((cfg.hardware.raw_height, cfg.hardware.raw_width))
    data, _ = pipeline.execute(d65)
    
    # RGB output
    output_path = op.join(OUTPUT_DIR, 'd65.png')
    output = cv2.cvtColor(data['output'], cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output)
    
    # Conditional IR output
    if 'ir' in data:
        output_ir = cv2.normalize(data['ir'], dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        output_path_ir = op.join(OUTPUT_DIR, 'd65_ir.png')
        cv2.imwrite(output_path_ir, output_ir)


def process(raw_path, output_name='test', cfg_path = 'configs/quality.yaml'):
    cfg = Config(cfg_path)
    pipeline = Pipeline(cfg)
    bayer = np.fromfile(raw_path, dtype='uint16', sep='')
    bayer = bayer.reshape((cfg.hardware.raw_height, cfg.hardware.raw_width))
    data, _ = pipeline.execute(bayer)
    
    # RGB output
    output_path = op.join(OUTPUT_DIR, output_name+'.png')
    output = cv2.cvtColor(data['output'], cv2.COLOR_RGB2BGR)
    cv2.imwrite(output_path, output)
    
    # Conditional IR output
    if 'ir' in data:
        output_ir = cv2.normalize(data['ir'], dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        output_path_ir = op.join(OUTPUT_DIR, output_name+'_ir.png')
        #output_ir = cv2.equalizeHist(output_ir)
        cv2.imwrite(output_path_ir, output_ir)


if __name__ == '__main__':
    
    # Remove 1st argument from the
    # list of command line arguments
    argumentList = sys.argv[1:]
    
    # Options
    options = "s: c: o:"
    
    # Long options
    long_options = ["Source", "Config", "Output"]
    
    try:
        # Parsing argument
        arguments, values = getopt.getopt(argumentList, options, long_options)
        
        
        # checking each argument
        if len(arguments) > 0:
            source_file = ''
            output_name = 'processed'
            config = 'configs/quality.yaml'
            for currentArgument, currentValue in arguments:
        
                if currentArgument in ("-s", "--Source"):
                    source_file = currentValue
                elif currentArgument in ("-c", "--Config"):
                    config = currentValue
                elif currentArgument in ("-o" or "--Output"):
                    output_name = currentValue
            
            if source_file != '':
                print(("Loading source file (% s)") % (source_file))
                print (("Loading config file (% s)") % (config))
                print (("Save output to /output/% s.png") % (output_name))
                print()
                process(source_file, output_name, config)
            else:
                print("No source file provided")
                print("Usage: isp.py -s <source_file>")
            
        else:
            print("No arguments provided")
            print("Usage: isp.py -s <source_file> -c <config_file> -o <output_name>")
            print("Example: isp.py -s <source_file> -c configs/quality.yaml -o default")
            print("Output will be saved as png in ./output/default.png")
            sys.exit(2)
            
    
    except getopt.error as err:
        # output error, and return with an error code
        print (str(err))