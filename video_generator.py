import re
from datetime import datetime, timedelta
import os
import tempfile
import shutil
from os import system, path
from lib.youtube import get_most_recent_video_name, upload_video, insert_into_playlist

DATE_FORMAT = "%Y_%m_%d"
TMP_CAPTURE_DIR = "/tmp/tomato-control-pi-capture"
PLAYLIST_ID = "PL4BgsQyEYodMayOiajRXmDkQ1NsWKccPP"

# # 1. Get the date of the most recent upload on Youtube
yt_video_name = get_most_recent_video_name(PLAYLIST_ID)
m = re.search("(\d{4}_\d{2}_\d{2})", yt_video_name)
if m is None:
    print "No YouTube video found"
    exit(1)

yt_date = datetime.strptime(m.group(), DATE_FORMAT)
# yt_date = datetime.strptime('2017-06-02', ISO_DATE_FORMAT)
print "YouTube date {}".format(yt_date)

# 2. rsync with the pi the list of folder / files
if not os.path.exists(TMP_CAPTURE_DIR) or not path.isdir(TMP_CAPTURE_DIR):
    print "Create directory {}".format(TMP_CAPTURE_DIR)
    os.makedirs(TMP_CAPTURE_DIR)

print "Rsync start ..."
system("rsync pi@10.0.1.12:tomato-control/capture/ {} -r --ignore-existing --stats".format(TMP_CAPTURE_DIR))
print "Rsync done!"


# 3. Get the most recent image folder coming from rsync
tmp_content = os.listdir(TMP_CAPTURE_DIR)
# filter out "." directories
tmp_content = [x for x in tmp_content if x[:1] != '.']
tmp_content.sort()

active_pi_capture = datetime.strptime(tmp_content[-1], DATE_FORMAT)
print "Most Recent Pi Date {}".format(active_pi_capture)

# 3. logic to find which video to be created
#   if pi has a date > to the YT video
#       if only 1 newer folder -> STOP
dayDelta = (active_pi_capture - yt_date ).days
print "Day delta: {}".format(dayDelta)
if dayDelta < 2:
    print "Not enough days delta to do anything"
    exit(0)

# Process each missing day
target_date = yt_date
for inc in range(0, dayDelta-1):
    target_date += timedelta(days=1)
    target_date_str = target_date.strftime(DATE_FORMAT)
    print "================================================"
    print "Process {}".format(target_date)
    target_dir = path.join(TMP_CAPTURE_DIR, target_date_str)
    if not path.isdir(target_dir):
        print "ERROR missing directory {}".format(target_dir)
        continue
        # exit(1)

    # 4. Copy the capture directory
    tmpdirname = tempfile.mkdtemp()
    dir_content = os.listdir(target_dir)
    dir_content.sort()

    # We copy and rename the file as need by ffmepg
    for counter, img in enumerate(dir_content):
        src = path.join(target_dir, img)
        dest = path.join(tmpdirname, "img-{}.jpg".format(counter+1))
        print 'file {} -> {}'.format(src, dest)
        shutil.copyfile(src, dest)

    # Run ffmpeg
    video_file = path.join(tmpdirname, "{}.mp4".format(target_date_str))
    cmd = "ffmpeg -framerate 24 -i {}/img-%d.jpg {}".format(tmpdirname, video_file)
    system(cmd)

    # 6. upload to youtube
    video_id = upload_video(video_file, target_date_str)
    insert_into_playlist(PLAYLIST_ID, video_id)

    # 7. remove the tmp files
    shutil.rmtree(tmpdirname)
    print "Video process with success! Now, let's do the next one!"

print 'Done!'
