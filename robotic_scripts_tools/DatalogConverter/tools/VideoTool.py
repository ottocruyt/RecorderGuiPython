import cv2

from ..tools import DebugTool
import enlighten

class VideoTool:
    def writeVideo(self, vid_path, vid, rec_time_start, rec_time_end, width_i, height_i,
                   progress=None, debug_tool: DebugTool = None):
        nimg = len(vid)
        if (progress is not None):
            progress.count = 0
            progress.total = nimg

        fps = nimg * 1000 / (rec_time_end - rec_time_start)
        video_pit = cv2.VideoWriter(vid_path, cv2.VideoWriter_fourcc('I', '4', '2', '0'), fps, (width_i, height_i))
        if (debug_tool is not None):
            debug_tool.printDebug("writing avi with %dx%d (%d fps)" % (width_i, height_i, fps))
        i = 0
        for v in vid:
            video_pit.write(v)
            if (debug_tool is not None):
                debug_tool.printDebug("wrote video frame %d" % (i))
            if (progress is not None):
                progress.update()
            i += 1