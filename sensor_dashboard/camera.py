import datetime
import logging
import os
from os.path import isfile, join

logger = logging.getLogger(__name__)

FAKE_PICTURE = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x01\x00\x00\x00\x01\x00\x08\x03\x00\x00\x00k\xacXT\x00\x00\x00\x03PLTEz\xcb\xff\xfb\x101T\x00\x00\x013IDATx^\xed\xd0\x81\x00\x00\x00\x00\x80\xa0\xfd\xa9\x17)\x84\n\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180`\xc0\x80\x01\x03\x06\x0c\x180``\x01\x0f\x00\x01m\x05GU\x00\x00\x00\x00IEND\xaeB`\x82'


class Camera:
    def __init__(self, photo_file_dir, fake_measurements):
        self.photo_file_dir = photo_file_dir
        self.fake_measurements = fake_measurements
        if not os.path.exists(self.photo_file_dir):
            os.makedirs(self.photo_file_dir)

    def generate_new_file_path(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%dT%H-%M-%S')
        file_path = os.path.join(self.photo_file_dir, timestamp + '.png')
        return file_path

    def take_real_photo(self):
        file_path = self.generate_new_file_path()

        cmd = 'raspistill -vf -hf -o {}'.format(file_path)
        error = False
        try:
            status = os.system(cmd)
            if status:
                error = True
        except Exception:
            logger.exception('Error while taking a photo')
            error = True
        return error

    def take_fake_photo(self):
        file_path = self.generate_new_file_path()
        with open(file_path, 'wb') as f:
            f.write(FAKE_PICTURE)
        return False

    def take_photo(self):
        if self.fake_measurements:
            return self.take_fake_photo()
        else:
            return self.take_real_photo()

    def get_list_of_photo_files(self):
        file_names = []
        for f in os.listdir(self.photo_file_dir):
            if isfile(join(self.photo_file_dir, f)) and 'gitignore' not in f:
                file_names.append(f)
        return sorted(file_names)

    def delete_all_photos(self):
        for root, dirs, files in os.walk(self.photo_file_dir):
            for f in files:
                os.unlink(os.path.join(root, f))
