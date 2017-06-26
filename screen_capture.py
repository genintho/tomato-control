import os
from os import system, path
from time import sleep


ROOT_DIR = "/tmp/screen"

print "Start loop"

if not os.path.exists(ROOT_DIR) or not path.isdir(ROOT_DIR):
    print "Create active directory {}".format(ROOT_DIR)
    os.makedirs(ROOT_DIR)

i = 1
while 1:
    print i
    system("screencapture -t jpg -x {}/screen-{}.jpg".format(ROOT_DIR, i))
    i = i + 1
    sleep(5)




