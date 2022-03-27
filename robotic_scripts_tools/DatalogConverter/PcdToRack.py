from open3d import *
import os
import glob
import argparse
import numpy as np
import enlighten

from main.defines import ScanPoint, BoundingBox, Position3d
from tools.datalog import Scan3dData

# todo: parse as argument
img_diff_ms = 500


# convert a pcd file to rack scan3d recording - todo: include binary mode
def pcdToScan3d(instance, input_path, output_path, loop_num=1, scan_num=640, scan_point_num=480, max_range=30000):
    # create dummy data --> initialize to 0
    # todo: make this parametrizable with command line arguments
    pos = Position3d.Position3d(x=0, y=0, z=0, phi=0.0, psi=0.0, rho=0.0)
    bounding_box = BoundingBox.BoundingBox(x1=0, x2=0, y1=0, y2=0, z1=0, z2=0, pos=pos, pos_valid=0, on=0)
    scan_mode = 771
    scan_hardware = 0
    sector_num = 0
    sector_index = 0
    compressed = 0
    scan3d_data = Scan3dData.Scan3dData(recording_time=0, duration=1, max_range=max_range, scan_num=scan_num,
                                        scan_point_num=scan_point_num, scan_mode=scan_mode, scan_hardware=scan_hardware,
                                        sector_num=sector_num,
                                        sector_index=sector_index, ref_pos=pos, bounding_box=bounding_box,
                                        point_num=scan_num * scan_point_num,
                                        compressed=compressed, dataset_num=0)

    # scan point params
    type = 0
    segment = 0

    # find pcl files
    pcl_files = glob.glob("%s/*.pcd" % (input_path))
    print(pcl_files)

    # progress indication
    progress_manager = enlighten.get_manager()
    loop_progress = progress_manager.counter(total=loop_num, desc="Loop",
                                             unit='loops')
    pcd_progress = progress_manager.counter(total=len(pcl_files), desc="PointClouds",
                                            unit='pcds')
    point_progress = progress_manager.counter(total=scan_num * scan_point_num, desc="Points",
                                              unit='points')

    # create dat file
    scan3d_dat = (("%s/scan3d_0.dat") % (output_path))
    os.makedirs(os.path.dirname(scan3d_dat), exist_ok=True)
    file = open(scan3d_dat, "x", newline="\n")

    # write header
    scan3d_data.writeAsciiHeader(file, instance)
    scan3d_file_num = 1

    # write output data loop_num times
    for loops in range(0, loop_num, 1):
        pcd_progress.count = 0
        for pcd in pcl_files:
            # read the point cloud
            cloud = io.read_point_cloud(pcd)

            # set scan3d data properties
            scan3d_data.recording_time = img_diff_ms * scan3d_file_num
            scan3d_data.dataset_num = scan3d_file_num

            # create .3d subfile
            subfile_name = ("%s/scan3d_%d_%d.3d") % (output_path, instance, scan3d_file_num)
            subf = open(subfile_name, "x", newline="\n")

            # dimension check
            if (len(cloud.points) != scan3d_data.point_num):
                print("dimension mismatch -- check pcd pointnum (%d), scan_point_num * scan_num (%d)" % \
                      (len(cloud.points), scan3d_data.point_num))
                exit(-1)

            # convert the cloud
            points = np.asarray(cloud.points)
            cloud_array = reversed(points)

            # write the output data
            cnt = 0
            point_progress.count = 0
            for i in cloud_array:
                cnt = cnt + 1
                x = np.asarray(i)

                dist = np.sqrt(x[0] * x[0] + x[1] * x[1] + x[2] * x[2]) * 1.000
                scan_point = ScanPoint.ScanPoint(x=x[2] * 1000, y=-x[0] * 1000, z=-x[1] * 1000, dist=dist,
                                                 type=type, segment=segment, intensity=dist)
                scan_point.writeAscii(subf)
                subf.write("\n")
                point_progress.update()

            subf.close()

            scan3d_data.writeAscii(file)

            print("(%f %%) - cloud %d of %d" % (
                100 * scan3d_file_num / (loop_num * len(pcl_files)), scan3d_file_num, loop_num * len(pcl_files)))
            scan3d_file_num += 1

            pcd_progress.update()

        loop_progress.update()
    file.close()
    print("done")


parser = argparse.ArgumentParser(description="Create a scan3d recording file based on pcd point cloud")
parser.add_argument('--input', '-i', help="input file folder, containing *.pcd cloud files")
parser.add_argument('--output', '-o', help="output folder, this will contain the rack dataplayer files")
parser.add_argument('--loop', '-l', help="loop X times to make the datastream file longer")

args = parser.parse_args()

if args.input is not None:
    input_path = args.input
else:
    input_path = "."

if args.output is not None:
    output_path = args.output
else:
    output_path = "%s/3D-RACK" % (input_path)

if args.loop is not None and int(args.loop) > 0:
    n_loops = int(args.loop)
else:
    n_loops = 1

print(output_path)

try:
    os.makedirs(output_path)
    print("Directory ", output_path, " Created ")
except FileExistsError:
    print("Directory ", output_path, " already exists")

pcdToScan3d(0, input_path, output_path, n_loops)
