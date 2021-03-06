from picamera import PiCamera
import os
from os import system, path
import time
from time import sleep


# TODO param
# Set the timezone, relevant for the picture name!
os.environ["TZ"] = "US/Pacific"

ROOT_DIR = "capture/"

print "Start loop"
while 1:
    today = time.strftime("%Y_%m_%d")
    now = time.strftime("%H_%M_%S")
    active_dir = path.join(ROOT_DIR, today)

    if not os.path.exists(active_dir) or not path.isdir(active_dir):
        print "Create active directory {}".format(active_dir)
        os.makedirs(active_dir)

    camera = PiCamera()  # Create instance
    sleep(3)
    image_path = path.join(active_dir, "{}-{}.jpg".format(today, now))
    tmp_image_path = path.join(active_dir, "tmp_{}-{}.jpg".format(today, now))
    print "Capture  image {}".format(image_path)
    # TODO param
    camera.rotation = 180
    camera.capture(image_path)
    camera.close()  # Destroy camera to save power
    print "Optimize image {}".format(image_path)
    system("convert -strip -quality 85% {} {}".format(image_path, tmp_image_path))
    os.remove(image_path)
    os.rename(tmp_image_path, image_path)
    # TODO param
    sleep(2)
