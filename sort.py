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
    ras = []
    decs = []

    for subdir, _, files in os.walk(lights_dir):
        for file in files:
            if file.endswith('.fits'):
                with fits.open(os.path.join(subdir, file)) as fits_file:
                    try:
                        exposure_time = int(fits_file[0].header['EXPTIME'])
                        ra = float(fits_file[0].header['RA'])
                        dec = float(fits_file[0].header['DEC'])

                        exposure_times.append(exposure_time)
                        ras.append(ra)
                        decs.append(dec)
                    except KeyError as e:
                        print('Exposure time, RA or DEC no present in file: ' + os.path.join(subdir, file))
                        raise ValidationException(e)
            else:
                continue

    try:
        assert all(exposure_time == exposure_times[0] for exposure_time in exposure_times), 'Not all exposure times are equal. Exiting script.'
        assert max(ras) - min(ras) < 3, 'Right Ascention range greater than 3 degrees. Exiting script'
        assert max(decs) - min(decs) < 3, 'Declination range greater than 3 degrees. Exiting script'
    except AssertionError as e:
        print('Validation failed.')
        raise ValidationException(e)

    return exposure_times[0]


def symlink_master_biases_and_darks(image_type_dir, master_bias_dir, darks_dir, exposure_time):
    process_path = os.path.join(image_type_dir, 'PROCESS')
    master_bias_path = os.path.join(master_bias_dir, 'bias_stacked.fit')
    master_dark_path = os.path.join(darks_dir, str(exposure_time) + 'S', 'dark_stacked.fit')

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
