import tkinter as tk
import time
import argparse
import os
import cv2
from icecream import ic
from camera import CameraManager
import signal
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Program that opens the camera and saves the video in the current working directory."
                    " If you want to exit the cam you have to press the ESCape button or 'q' to quit!!!"
    )
    parser.add_argument("-g", action="store_true", help="Run the program in GUI format")
    parser.add_argument("-o", dest="output",   type=str, nargs='?', default="./", help="URI of the output video")
    parser.add_argument("-l", dest="looping_value", type=int, nargs='?', default=1, 
        help="Number of times to capture video (the default value is 1, if you insert -1 it loops indefinitely until 'q' is pressed)"
    )
    parser.add_argument("-d", dest="duration_vid", type=int, nargs='?', default=10,
        help="Number of seconds of video to capture"
    )
    parser.add_argument("-cd",dest="countdown", type=int, nargs='?', default=0, help="Number of seconds to wait before starting the camera"
    )
    parser.add_argument("--src", dest="camera", type=int, nargs='?', default=0, help="Number of the camera to capture"
    )

    args = parser.parse_args()
    cr = CameraRecorder(args.g,args.output,args.looping_value,args.duration_vid,args.countdown,args.camera)
    cr.start()


   

    


class CameraRecorder():
    def __init__(self,gui,output,looping_value,duration_vid,countdown,camera):
        self.gui = gui
        self.output = output 
        self.looping_value = looping_value
        self.duration_vid = duration_vid
        self.countdown = countdown
        self.camera = camera
        self.camera_manager = None
        self.last_frame = None

        signal.signal(signal.SIGINT, self.on_signal)

    def start(self):

        t1 = time.time()

        self.start_camera()
        if self.gui:
           self.start_gui()
        else:
            self.start_cli()
        
        t2 = time.time()
        ic(f"Executed in {t2 - t1} seconds")
        cv2.destroyAllWindows()

    def start_camera(self):
        self.camera_manager = CameraManager(self.output, self.looping_value, self.duration_vid, self.countdown, self.camera)
        self.camera_manager.on_start = self.on_camera_start
        self.camera_manager.on_stop = self.on_camera_stop
        self.camera_manager.on_error = self.on_camera_error
        self.camera_manager.on_frame_ready = self.on_camera_frame

        self.camera_manager.start_camera()


    def start_gui(self):
        #gino = guil.VideoRecorder()
        #gino.run()
        root = tk.Tk()
        app = guis.CameraGUI(root)
        root.mainloop()

    def start_cli(self):
        while self.camera_manager.is_running():
            if self.last_frame is not None:
                cv2.imshow('Camera', self.last_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                ic('key Q')
                self.camera_manager.close_camera()
                break
            elif key == 27:
                ic('key ESC')
                self.camera_manager.restart_camera()


    def on_camera_start(self):
        ic("Starting the camera up ...")

    def on_camera_stop(self):
        #cv2.destroyAllWindows()
        ic("Stopping the camera ...")
        

    def on_camera_error(self,message: str):
        ic(message)
        

    def on_camera_frame(self,frame):
        #ic("Starting the camera up ...")
        self.last_frame = frame
        #cv2.imshow('Camera', frame)
    
    def on_signal(self, sig, frame):
        print('You pressed Ctrl+C!')
        if self.camera_manager is not None:
            self.camera_manager.close_camera()

        sys.exit(0)



if __name__ == '__main__':
    main()