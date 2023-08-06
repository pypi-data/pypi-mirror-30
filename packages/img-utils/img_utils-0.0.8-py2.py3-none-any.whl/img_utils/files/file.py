import glob
import os


def images_in_dir(images_dir, file_types=('*.png', '*.jpg', '*.jpeg', '*.gif')):
    file_names = []
    for ext in file_types:
        file_names.extend(glob.glob(os.path.join(images_dir, ext)))
    return sorted(file_names)


def filename(file_path):
    return file_path.split(os.sep)[-1]


def file_ext(file_name):
    idx = file_name.rindex(os.extsep)
    return file_name[0:idx]
