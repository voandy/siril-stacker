import os
import shutil

from pysiril.siril import *
from astropy.io import fits


class ProcessingException(Exception):
    pass


def master_flat(app, flat_dir, process_dir):
    app.Execute('cd ' + flat_dir + '\n'
                'convert flat -out=' + process_dir + ' -fitseq' + '\n'
                'cd ' + process_dir  + '\n'
                'preprocess flat -bias=bias_stacked' + '\n'
                'stack pp_flat rej 3 3 -norm=mul')
    

def light(app, light_dir, process_dir, output_dir, image_type):
    app.Execute('cd ' + light_dir)
    app.Execute('convert light -out=' + process_dir + ' -fitseq')
    app.Execute('cd ' + process_dir)
    app.Execute('preprocess light -dark=dark_stacked -flat=pp_flat_stacked')
    app.Execute('register pp_light')
    app.Execute('stack r_pp_light rej linear 5 5 -norm=addscale -output_norm -out=' + output_dir + '\\STACKED\\' + image_type)
    app.Execute('close')

    
def stack_image_type(image_type_dir, output_dir):
    light_dir = os.path.join(image_type_dir, 'LIGHT')
    flat_dir = os.path.join(image_type_dir, 'FLAT')
    process_dir = os.path.join(image_type_dir, 'PROCESS')
    image_type = image_type_dir.split('\\')[-1]

    app = Siril()

    try:
        app.Open()
        app.Execute('set32bits')
        app.Execute('setext fit')
        master_flat(app, flat_dir, process_dir)
        light(app, light_dir, process_dir, output_dir, image_type)
    except Exception as e :
        print('Error occured when stacking images.')
        raise ProcessingException(e)
    finally:
        app.Close()
        del app


def register_stacked_frames(output_dir):
    stacked_dir = os.path.join(output_dir, 'STACKED')
    app = Siril()

    try:
        app.Open()
        app.Execute('cd ' + stacked_dir)
        app.Execute('link stacked')
        app.Execute('register stacked -prefix=registered_')
    except Exception as e:
        print('Error occured when registering stacked images.')
        raise ProcessingException(e)
    finally:
        app.Close()
        del app

    for file in os.listdir(stacked_dir):
        file_path = os.path.join(stacked_dir, file)
        if file.startswith('registered_') and file.endswith('.fit'):
            with fits.open(file_path) as fits_file:
                filter_type = fits_file[0].header['FILTER']
                shutil.copy(file_path, os.path.join(output_dir, filter_type + "_REGISTERED.fit"))
