import os
import shutil
import yaml
from sort import ValidationException, symlink_files, verify_lights, symlink_master_biases_and_darks
from stack import stack_image_type


def main():
    with open('config.yaml', encoding='UTF-8') as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    input_dir = config['directories']['input_directory']
    output_dir = config['directories']['output_directory']
    master_bias_dir = config['directories']['biases_directory']
    darks_dir = config['directories']['darks_directory']

    try:
        sorted_dir = os.path.join(output_dir, 'SORTED')
        symlink_files(input_dir, sorted_dir)

        image_directories = ([name for name in os.listdir(sorted_dir) if os.path.isdir(os.path.join(sorted_dir, name))])

        for image_directory in image_directories:
            image_type_dir = os.path.join(sorted_dir, image_directory)

            exposure_time = verify_lights(os.path.join(image_type_dir, 'LIGHT'))
            symlink_master_biases_and_darks(image_type_dir, master_bias_dir, darks_dir, exposure_time)
            stack_image_type(image_type_dir, output_dir)
    except ValidationException as e:
        print('Validation failed. Exiting script')
        exit(1)
    except Exception as e:
        print('Unhandled exception was raise.')
        print(e)
        exit(1)
    finally:
        shutil.rmtree(sorted_dir, ignore_errors=True)



if __name__ == '__main__':
    main()
