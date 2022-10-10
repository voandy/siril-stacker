import os
import yaml
from pathlib import Path
from astropy.io import fits

with open('config.yaml') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

workdir = config['directories']['working_directory']
master_bias_dir = config['directories']['biases_directory']
darks_dir = config['directories']['darks_directory']

for subdir, dirs, files in os.walk(workdir):
    for file in files:
        if file.endswith('.fits'):
            with fits.open(os.path.join(subdir, file)) as fits_file:
                try:
                    filter = fits_file[0].header['FILTER']
                    image_type = fits_file[0].header['IMAGETYP']
                    src = os.path.join(subdir, file)
                    dst = os.path.join(workdir, 'sorted', filter, image_type, file)
                    Path(os.path.join(workdir, 'sorted', filter, image_type)).mkdir(parents=True, exist_ok=True)
                    os.symlink(src, dst)
                except FileExistsError:
                    print('Destination fits file already exists. Skipping fits file: ' + os.path.join(subdir, file))
                    continue 
                except KeyError:
                    print('Filter or image type not found. Skipping fits file: ' + os.path.join(subdir, file))
                    continue
        else:
            continue
