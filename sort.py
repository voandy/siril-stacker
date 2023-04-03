import os
from pathlib import Path
from astropy.io import fits


class ValidationException(Exception):
    pass


def symlink_files(input_dir, sorted_dir):
    for subdir, _, files in os.walk(input_dir):
        for file in files:
            if file.endswith('.fits'):
                with fits.open(os.path.join(subdir, file)) as fits_file:
                    try:
                        filter_type = fits_file[0].header['FILTER']
                        image_type = fits_file[0].header['IMAGETYP']
                        src = os.path.join(subdir, file)
                        dst = os.path.join(sorted_dir, filter_type, image_type, file)
                        Path(os.path.join(sorted_dir, filter_type, image_type)).mkdir(parents=True, exist_ok=True)
                        os.symlink(src, dst)
                    except FileExistsError:
                        print('Destination fits file already exists. Skipping fits file: ' + os.path.join(subdir, file))
                        continue 
                    except KeyError:
                        print('Filter or image type not found. Skipping fits file: ' + os.path.join(subdir, file))
                        continue
            else:
                continue
    return


def verify_lights(lights_dir):
    exposure_times = []
    gains = []
    offsets = []

    for subdir, _, files in os.walk(lights_dir):
        for file in files:
            if file.endswith('.fits') and 'BAD' not in file:
                with fits.open(os.path.join(subdir, file)) as fits_file:
                    try:
                        fits_header = fits_file[0].header
                        exposure_times.append(int(fits_header['EXPTIME']))
                        gains.append(fits_header['GAIN'])
                        offsets.append(fits_header['OFFSET'])
                    except KeyError as e:
                        print('Required header not present in file: ' + os.path.join(subdir, file))
                        print(e.__cause__)
                        raise ValidationException(e)
            else:
                continue

    try:
        assert all(exposure_time == exposure_times[0] for exposure_time in exposure_times), 'Not all exposure times are equal. Exiting script.'
        assert all(gain == gains[0] for gain in gains), 'Not all exposure times are equal. Exiting script.'
        assert all(offset == offsets[0] for offset in offsets), 'Not all exposure times are equal. Exiting script.'
    except AssertionError as e:
        print('Validation failed.')
        raise ValidationException(e)

    return fits_header


def symlink_master_biases_and_darks(resolution, image_type_dir, library_dir, fits_header):
    exposure_time = (int(fits_header['EXPTIME']))
    gain = fits_header['GAIN']
    offset = (fits_header['OFFSET'])

    library_dir = library_dir.replace('[GAIN]', str(gain)).replace('[OFFSET]', str(offset)).replace('[RESOLUTION]', resolution)

    process_path = os.path.join(image_type_dir, 'PROCESS')
    master_bias_path = os.path.join(library_dir, 'BIASES', 'bias_stacked.fit')
    master_dark_path = os.path.join(library_dir, 'DARKS', str(exposure_time) + 'S', 'dark_stacked.fit')

    Path(process_path).mkdir(parents=True, exist_ok=True)

    try:
        os.symlink(master_bias_path, os.path.join(process_path, 'bias_stacked.fit'))
    except FileExistsError:
        print('Destination fit file already exists. Skipping fits file: ', os.path.join(process_path, 'bias_stacked.fit'))

    try:
        os.symlink(master_dark_path, os.path.join(process_path, 'dark_stacked.fit'))
    except FileExistsError:
        print('Destination fit file already exists. Skipping fits file: ', os.path.join(process_path, 'dark_stacked.fit'))

    return
