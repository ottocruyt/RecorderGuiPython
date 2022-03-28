import os, shutil, argparse, tarfile
import numpy as np
import tkinter as tk
from tkinter import filedialog
import enlighten
from PIL import Image, ImageOps, ImageDraw
import cv2
import open3d as o3d
import matplotlib as mpl
from matplotlib import cm
from pathlib import Path
from .tools import CameraTool, FileTool, VideoTool
from .tools import DebugTool
from .tools.datalog import BinaryHeader, BinarySubHeader, ObjRecogData, Scan3dData
from .main.defines import ScanPoint, ObjRecogObj

def RecordConverter(file):
	#input param was: (raw_args=None)
	#parser = argparse.ArgumentParser(description='Convert 3D-Recog datalog to image and video file')
	#parser.add_argument('file', metavar='input.tar.gz', type=str, default="", nargs='?',
	#					help='the path to the record file that shall be converted (*.tar.gz)')
	#parser.add_argument('--instance', metavar='instance', type=int, default=0,
	#					help='instance number of the camera module (e.g. 1 for "scan3d_1.dat, default: 0)"')
	#parser.add_argument('--mode', metavar='mode', type=str, default='intensity',
	#					help='chose the value for the greyscale image: "intensity" (default), "dist", "x")')
	#parser.add_argument('--video', action="store_true",
	#					help='use video flag to generate a video (avi)')
	#parser.add_argument('--pcd', action="store_true",
	#					help='use video flag to generate 3d pointcloud files (pcd)')
	#parser.add_argument('--uncalibrated', action="store_true",
	#					help='store the files of the uncalibrated images/videos (without overlay)')
	#parser.add_argument('--obj_color', metavar='obj_color', type=str, default="red",
	#					help='color for the object overlay (default: red)')
	#parser.add_argument('--roi_color', metavar='roi_color', type=str, default="green",
	#					help='color for the roi overlay (default: green)')
	#parser.add_argument('--autocontrast_cutoff', metavar='autocontrast_cutoff', type=int, default=3,
	#					help='cutoff for the autocontrast algorythm (default: 3)')
	#parser.add_argument('--verbose', action="store_true",
	#					help='print additional debug output')

	# parse args
	#args = parser.parse_args(raw_args)
	instance = 0
	mode = "intensity"
	video = False
	pcd = False
	uncalibrated = False
	obj_color = "red"
	roi_color = "green"
	verbose = False
	autocontrast_cutoff = 3
	filename = file

	# camera related variables --> TODO: read from a camera parameter file
	angle_hor = 70
	angle_vert = 52
	height_i = 480
	width_i = 640

	# setup tools
	camera_tool = CameraTool.CameraTool(width_i, height_i, angle_hor, angle_vert)
	debug_tool = DebugTool.DebugTool(verbose)
	file_tool = FileTool.FileTool()
	video_tool = VideoTool.VideoTool()
	
	debug_tool.printDebug("file name arg: " + filename)
	debug_tool.printDebug("verbose: " + str(verbose))
	debug_tool.printDebug("autocontrast_cutoff: " + str(autocontrast_cutoff))


	if len(filename) < 1:
		root = tk.Tk()
		root.withdraw()
		root.call('wm', 'attributes', '.', '-topmost', True)
		filename = filedialog.askopenfilename()
		root.update()
		debug_tool.printDebug(filename)

	# create necesary folders
	# define output filenames
	filename_output = os.path.basename(filename)
	filename_output = os.path.splitext(os.path.splitext(filename_output)[0])[0]
	foldername_output = os.path.splitext(os.path.splitext(filename)[0])[0]

	debug_tool.printDebug(filename_output)
	if os.path.isfile(filename):
		tmp_folder = foldername_output + "_tmp"
		outpath = foldername_output

		# generate path name that is not existing
		inc = 1
		while os.path.isdir(tmp_folder):
			tmp_folder = foldername_output + "_tmp" + str(inc)
			inc += 1
		os.makedirs(tmp_folder)

		# remove outpath if it exist (clean up before recreating)
		if os.path.isdir(outpath):
			shutil.rmtree(outpath)
		os.makedirs(outpath)
	else:
		print("file doesn't exist -- abort")
		exit(-1)
		


	# untar file
	my_tar = tarfile.open(filename)
	# todo: for now the file is appended to open_files manually because we are using a different open function
	# from the tarfile library (tarfile.open('filename'))
	file_tool.open_files.append(my_tar)
	my_tar.extractall(tmp_folder)
	my_tar.close()
	file_tool.open_files.remove(my_tar)

	path = tmp_folder

	# create scan3d paths
	scan3d_datpath = path + "/scan3d_" + str(instance) + ".dat"
	scan3d_rawpath = path + "/scan3d_" + str(instance) + ".raw"

	# open scan3d files
	debug_tool.printDebug("opening: " + scan3d_datpath)
	f_dat = file_tool.openFile(scan3d_datpath, "r")
	f_raw = file_tool.openFile(scan3d_rawpath, "rb")

	# read the header lines
	debug_tool.printDebug(f_dat.readline())
	debug_tool.printDebug(f_dat.readline())

	# count number of entries in the scan3d file for progress indication
	startpos = f_dat.tell()
	datlen = 0
	for line in f_dat:
		datlen += 1
	f_dat.seek(startpos)

	# reading and collecting obj recog records
	objrecog_datfiles = []
	objrecog_path = []
	for p in Path(path).glob("objrecog_*.dat"):
		debug_tool.printDebug(str(p) + " found")
		ftmp = file_tool.openFile(p, 'r')
		debug_tool.printDebug(ftmp.readline())
		debug_tool.printDebug(ftmp.readline())
		objrecog_datfiles.append(ftmp)
		objrecog_path.append(os.path.splitext(str(p))[0])

	# set up progress indicator
	progress_manager = enlighten.get_manager()
	pixel_progress = progress_manager.counter(total=height_i * width_i, desc="Image conversion (1/%d)" % datlen,
											  unit='pixels')
	if (pcd):
		pcd_progress = progress_manager.counter(total=datlen, desc='Writing PCDs', unit='frames')
	if (video):
		vid_prepare_progress = progress_manager.counter(total=datlen, desc='Preparing Video')
	frame_progress = progress_manager.counter(total=datlen, desc='Frames', unit='frames')


	def createScan3dObjImages(f_dat, f_raw, objrecog_datfiles):
		vid = []
		vid_calib = []
		width = 0
		height = 0
		rec_time_start = -1
		rec_time_end = -1

		if pcd:
			pointcloud = o3d.geometry.PointCloud()

		binary_header = BinaryHeader.BinaryHeader()
		binary_sub_header = BinarySubHeader.BinarySubHeader()
		binary_header.read(f_raw)

		nimg = 0
		for line in f_dat:
			scan3d_data = Scan3dData.Scan3dData()
			line = line.strip()
			debug_tool.printDebug("Parsing Scan3dData: " + line)
			scan3d_data.parseAscii(line)
			scan3d_data.castData()
			if rec_time_start == -1:
				rec_time_start = scan3d_data.recording_time
			rec_time_end = scan3d_data.recording_time
			debug_tool.printDebug(line)

			width = scan3d_data.scan_num
			height = scan3d_data.scan_point_num

			binary_sub_header.read(f_raw)

			data = []
			points = np.zeros((width * height, 3))
			data_calib = np.zeros((width, height))

			p_ind = 0

			pixel_progress.count = 0
			pixel_progress.desc = "Image conversion (%d/%d)" % (nimg + 1, datlen)
			max_dat = 1
			min_dat = 4294967295

			for i in range(height):
				for j in range(width):
					scan_point = ScanPoint.ScanPoint()
					scan_point.readBinary(f_raw)
					value = getScanPointData(scan_point, mode)
					data.append(value)
					if (value > max_dat):
						max_dat = value
					if (value < min_dat):
						min_dat = value
					h, w = camera_tool.getCameraPositionFrom3DCoords(scan_point.x, scan_point.y, scan_point.z)
					if h < 0 or w < 0:
						continue
					if h >= height or w >= width:
						continue
					data_calib[w][h] = value
					points[p_ind, 0] = scan_point.x
					points[p_ind, 1] = scan_point.y
					points[p_ind, 2] = scan_point.z
					p_ind += 1
				pixel_progress.update(width)

			div = (max_dat - min_dat) / 255
			data_calib = np.where(data_calib < min_dat, min_dat, data_calib)

			img = Image.fromarray(np.transpose(((np.asarray(data) - min_dat) / div).reshape(width, height)).astype("uint8"))
			edited = ImageOps.autocontrast(img, cutoff=autocontrast_cutoff)
			img_calib = Image.fromarray(
				np.transpose(((np.asarray(data_calib) - min_dat) / div).reshape(width, height)).astype("uint8"))
			edited_calib = ImageOps.autocontrast(img_calib, cutoff=autocontrast_cutoff)
			rgbimg = Image.new("RGBA", img.size)

			# generate heatmap
			if mode == 'dist':
				cm_hot = mpl.cm.get_cmap('nipy_spectral')
				im = np.array(edited_calib)
				im = cm_hot(im)
				im = np.uint8(im * 255)
				edited_calib = Image.fromarray(im)

			rgbimg.paste(edited_calib)
			draw = ImageDraw.Draw(rgbimg)
			i = 0

			# draw objects and roi
			for obj_rec_file in objrecog_datfiles:
				objdata = ObjRecogData.ObjRecogData()
				if objdata.readAscii(obj_rec_file):
					objdata.castData()
				else:
					continue
				while objdata is not None and objdata.recording_time < int(objdata.recording_time):
					if objdata.readAscii(obj_rec_file):
						objdata.castData()
					else:
						break
				if objdata == None:
					continue
				if objdata.expecting_object:

					camera_tool.drawRoi(draw, objdata, roi_color)

					file = file_tool.openFile(objrecog_path[i] + "_" + str(objdata.object_file_num) + ".obj", 'r')

					obj = ObjRecogObj.ObjRecogObj()
					if obj.readAscii(file):
						obj.castData()

					while obj is not None and obj.pos is not None:
						camera_tool.drawObjectRect(draw, obj, obj_color)

						if obj.readAscii(file):
							obj.castData()
						else:
							break
					file_tool.closeFile(file)
				i += 1

			pixel_progress.close(True)

			# convert to video
			if video:
				if uncalibrated:
					cvimg = np.asarray(edited)
					vid.append(cv2.cvtColor(cvimg, cv2.COLOR_GRAY2BGR))
				cvimg_calib = np.asarray(rgbimg)
				vid_calib.append(cv2.cvtColor(cvimg_calib, cv2.COLOR_RGBA2BGR))
				vid_prepare_progress.update()

			# save uncalibrated if selected
			if uncalibrated:
				edited.save(outpath + "/" + filename_output  + "_" + str(scan3d_data.dataset_num) + "_uncal.png")
			rgbimg.save(outpath + "/" + filename_output  + "_" + str(scan3d_data.dataset_num) + ".png")

			# save pointcloud
			if pcd:
				pointcloud.points = o3d.utility.Vector3dVector(points)
				# o3d.visualization.draw_geometries([pointcloud])
				# o3d.visualization.RenderOption.point_size = 0.03
				o3d.io.write_point_cloud(outpath + "/" + filename_output  + "_" + str(scan3d_data.dataset_num) + ".pcd",
										 pointcloud)
				pcd_progress.update()

			nimg += 1
			frame_progress.update()

		# close files
		for f in objrecog_datfiles:
			file_tool.closeFile(f)
		file_tool.closeFile(f_dat)
		file_tool.closeFile(f_raw)

		# save video
		if video:
			video_progess = progress_manager.counter(total=len(vid_calib), desc='Writing Video (uncalibrated)',
													 unit='frames')
			if uncalibrated:
				# create path
				vid_path = outpath + "/" + filename_output + "_uncal" + ".avi"
				# convert and save video
				video_tool.writeVideo(vid_path, vid, rec_time_start, rec_time_end, width, height,
									   video_progess, debug_tool)

			# update progress
			video_progess.desc = 'Writing Video (calibrated)'
			video_progess.count = 0
			# create path
			vid_path_calib = outpath + "/" + filename_output + ".avi"

			# convert and save video
			video_tool.writeVideo(vid_path_calib, vid_calib, rec_time_start, rec_time_end,
								  width, height, video_progess, debug_tool)

			video_progess.clear(True)
			video_progess.close(True)


	def getScanPointData(scan_point, point_mode):
		if (point_mode == 'intensity'):
			return scan_point.intensity
		if (point_mode == 'dist'):
			return scan_point.dist
		if (point_mode == 'x'):
			return scan_point.x
		return scan_point.intensity


	#try:
	createScan3dObjImages(f_dat, f_raw, objrecog_datfiles)
	#except:
	#    print("errors occured - removing tmp folder")
	#    if file_tool.closeAllFiles():
	#        shutil.rmtree(tmp_folder)
	#    else:
	#        print("can't close all files -- not cleaning up tmp folder")
	#    exit(-1)
	shutil.rmtree(tmp_folder)
	#exit(0)

if __name__ == '__main__':
    RecordConverter()
