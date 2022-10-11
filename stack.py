import sys
import os

from pysiril.siril import *
    
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
    app.Execute('stack r_pp_light rej 3 3 -norm=addscale -output_norm -out=' + output_dir + '\\STACKED\\' + image_type)
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
        print('\n**** ERROR *** ' +  str(e) + '\n')    
        
    app.Close()
    del app
