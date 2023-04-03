import os
import sys
import shutil
import yaml
from sort import ValidationException, symlink_files, verify_lights, symlink_master_biases_and_darks
from stack import ProcessingException, stack_image_type, register_stacked_frames


def main():
    resolution = sys.argv[1]

    with open('config.yaml', encoding='UTF-8') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    input_dir = config['directories']['input_directory']
    output_dir = config['directories']['output_directory']
    library_dir = config['directories']['library']

    try:
        sorted_dir = os.path.join(output_dir, 'SORTED')
        symlink_files(input_dir, sorted_dir)

        image_directories = ([name for name in os.listdir(sorted_dir) if os.path.isdir(os.path.join(sorted_dir, name))])

        for image_directory in image_directories:
            image_type_dir = os.path.join(sorted_dir, image_directory)

            fits_header = verify_lights(os.path.join(image_type_dir, 'LIGHT'))
            symlink_master_biases_and_darks(resolution, image_type_dir, library_dir, fits_header)
            stack_image_type(image_type_dir, output_dir)

        register_stacked_frames(output_dir)
    except ValidationException as e:
        print('Validation failed. Exiting script')
        print(e)
        exit(1)
    except ProcessingException as e:
        print('Processing exception occured. Exiting scipt')
        print(e)
        exit(1)
    except Exception as e:
        print('Unhandled exception was raised.')
        print(e)
        exit(1)
    finally:
        shutil.rmtree(sorted_dir, ignore_errors=True)
        shutil.rmtree(os.path.join(output_dir, 'STACKED'), ignore_errors=True)


if __name__ == '__main__':
    main()
