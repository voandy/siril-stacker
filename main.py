import os
import yaml
from sort import symlink_files
from sort import verify_lights
from sort import symlink_master_biases_and_darks


def main():
    with open('config.yaml', encoding="UTF-8") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    work_dir = config['directories']['working_directory']
    master_bias_dir = config['directories']['biases_directory']
    darks_dir = config['directories']['darks_directory']

    sorted_dir = os.path.join(work_dir, 'sorted')
    symlink_files(work_dir, sorted_dir)

    image_directories = ([name for name in os.listdir(sorted_dir) if os.path.isdir(os.path.join(sorted_dir, name))])

    for image_directory in image_directories:
        image_type_dir = os.path.join(sorted_dir, image_directory)
        lights_dir = os.path.join(image_type_dir, 'LIGHT')

        exposure_time = verify_lights(lights_dir)
        symlink_master_biases_and_darks(image_type_dir, master_bias_dir, darks_dir, exposure_time)


if __name__ == '__main__':
    main()
