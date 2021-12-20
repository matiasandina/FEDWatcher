# import the necessary packages
from src.KeyClipWriter import KeyClipWriter
from imutils.video import VideoStream
import argparse
import datetime
import imutils
import time
import cv2
import os


class VideoFeedClipper(object):
	"""docstring for VideoFeedClipper"""
	def __init__(self, buffer=100, timeout=1.0, usePiCamera=False, width=320, output_folder=None, fps=20.0):
		# store the maximum buffer size of frames to be kept
		# in memory along with the sleep timeout during threading
		self.bufSize = buffer
		self.timeout = timeout
		self.usePiCamera = usePiCamera
		self.width = width
		self.timestamp_format = '%Y-%m-%dT%H-%M-%S'	
		if output_folder is None: raise Exception("output_folder cannot be `None`.")
		self.output_folder = output_folder	
		# TODO: should we create output folder beforehand?
		self.fps=fps
		self.running = False

		# initialize the video stream and allow the camera sensor to
		# warmup
		print("[INFO] warming up camera...")
		# initialize videostream
		self.vs = VideoStream(usePiCamera=self.usePiCamera).start()
		time.sleep(2.0)
		# initialize key clip writer
		self.kcw = KeyClipWriter(bufSize=self.bufSize)
		consecFrames = 0


	def run(self, showframe):
		# TODO: implement while loop with fps control here instead of on the outside?
		# get the original frame
		self.frame = self.vs.read()
		# get the timestamp, keep the datetime format here			
		self.timestamp = datetime.datetime.now()
		# reshape it to desired resolution
		# this fixes the issue of nasty resolution when not using PiCamera
		self.frame = imutils.resize(self.frame, width = self.width)
		# update the key frame clip buffer
		self.update_kwc()
		if showframe:
			# making a copy to show a red rectangle without affecting the original 
			# comes with a bit of a performance hit.
			# But the major hit in performance is showing the video itself
			# to_show = self.frame.copy()
			#if self.kcw.recording:
			#	to_show = cv2.rectangle(self.frame.copy(), (5, 5), (25, 25), (0, 0, 255), -1)
			cv2.imshow("frame", self.frame)#to_show)
			cv2.waitKey(1)

	def update_kwc(self):
		# put frames to queue as tupple
		self.kcw.update((self.frame, self.timestamp))

	def trigger_recording(self):
		# Start recording
		# we first update the queues so when we start we can get the resolution from
		# self.frames[0].shape
		# This can be changed by passing resolution as a number
		init_timestamp = datetime.datetime.now().strftime(self.timestamp_format)
		# TODO: extension hardcoded here.
		video_filename = f"{init_timestamp}_video_clip.avi"
		timestamp_filename = f"{init_timestamp}_timestamp.csv"
		video_path = os.path.join(self.output_folder, video_filename)
		timestamp_path = os.path.join(self.output_folder, timestamp_filename)
		# TODO: codec hardcoded here
		self.kcw.start(
			timestampPath = timestamp_path, 
			videoPath = video_path, 
			fourcc=cv2.VideoWriter_fourcc(*'XVID'), 
			fps=self.fps)

	def finish_kwc(self):
		# kill the kwc object nicely
		self.kcw.finish()

	def stop(self):
		if self.kcw.recording:
			self.finish_kwc()
		# finish video and kill videostream
		cv2.destroyAllWindows()
		self.vs.stop()