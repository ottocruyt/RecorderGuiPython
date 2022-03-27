import os;
from PIL import Image, ImageOps;
import argparse;
import cv2;
import numpy as np

from tools import CameraTool, VideoTool
from tools.datalog import CameraData

parser = argparse.ArgumentParser(description='Convert Rack Camera datalog to image file')
parser.add_argument('path', metavar='path',
                    help='path of the datalog folder (containing "camera_[instace].dat"')
parser.add_argument('--instance', metavar='instance', type=int, default=0,
                    help='instance number of the camera module (e.g. 1 for "camera_1.dat"')
parser.add_argument('--video', action="store_true",
                    help='use video flag to generate a video (avi)')

args = parser.parse_args()
path = args.path
instance = args.instance
video = args.video
datpath = path + "/scan3d_" + str(instance) + ".dat"

print("opening: " + datpath)
f = open(datpath, "r")

# read the header line
print(f.readline())
print(f.readline())

vid = []
width_i = 0
height_i = 0
rec_time_start = -1
rec_time_end = -1
nimg = 0
video_tool = VideoTool.VideoTool()

# parse the data
camera_data = CameraData.CameraData()
while (camera_data.readAscii(f)):
    camera_data.castData()
    if rec_time_start == -1:
        rec_time_start = camera_data.recording_time
    rec_time_end = camera_data.recording_time
    rawPath = os.path.dirname(f.name) + "/camera_" + str(instance) + "_" + str(camera_data.camera_file_num) + ".raw"

    f2 = open(rawPath, 'rb');
    data = f2.read()

    width_i = camera_data.width
    height_i = camera_data.height
    img = Image.frombytes("L", (width_i, height_i), data)
    edited = ImageOps.autocontrast(img, cutoff=3)
    if (video):
        cvimg = np.asarray(edited)
        vid.append(cv2.cvtColor(cvimg, cv2.COLOR_GRAY2BGR))
    edited.save(os.path.dirname(f.name) + "/camera_" + str(instance) + "_" + str(camera_data.camera_file_num) + ".png")
    f2.close()
    nimg += 1
f.close()

# write video
if (video):
    vid_path = path + "/camera_" + str(instance) + ".avi"
    video_tool.writeVideo(path, vid, rec_time_start, rec_time_end, width_i, height_i)
