import isp

if __name__ == "__main__":
    bright_path = 'raw/bright/1_1.RAW'
    dark_path = 'raw/dark/1_1.RAW'
    speed = 'configs/speed.yaml'
    quality = 'configs/quality.yaml'
    
    mode = speed
    
    print('Processing d65 color chart...')
    isp.colorChecker(mode)
    
    print('Processing demo raw (bright/1_1)...')
    isp.process(bright_path, 'bright', mode)
    
    print('Processing demo raw (dark/1_1)...')
    isp.process(dark_path, 'dark', mode)
    