# This class handles clipping of recordings
# The original comes from here 
# https://www.pyimagesearch.com/2016/02/29/saving-key-event-video-clips-with-opencv/
# Further modifications by Matias Andina
# import the necessary packages
from collections import deque
from threading import Thread
from queue import Queue
import time
import cv2
import numpy as np
# One issue with this approach is that it might drop frames if we put the fps too high.
# In principle, even if we drop frames,
# we should be able to match frames because they come with their timestamps.

class KeyClipWriter:
	def __init__(self, bufSize=100, timeout=1.0):
		# store the maximum buffer size of frames to be kept
		# in memory along with the sleep timeout during threading
		self.bufSize = bufSize
		self.timeout = timeout
		# initialize the buffer of frames, queue of frames that
		# need to be written to file, video writer, writer thread,
		# and boolean indicating whether recording has started or not
		self.frames = deque(maxlen=bufSize)
		self.timestamps = deque(maxlen=bufSize)
		self.Q = None
		self.tsQ = None
		self.writer = None
		self.thread = None
		self.recording = False

	def update(self, frame_timestamp):
		# unpack tupple
		frame, timestamp = frame_timestamp
		# update the frames buffer
		self.frames.appendleft(frame)
		self.timestamps.appendleft(timestamp)
		# if we are recording, update the queue as well
		if self.recording:
			self.Q.put(frame)
			self.tsQ.put(timestamp)

	def start(self, timestampPath, videoPath, fourcc, fps):
		# indicate that we are recording, start the video writer,
		# and initialize the queue of frames that need to be written
		# to the video file
		self.recording = True
		self.timestampPath = timestampPath
		self.writer = cv2.VideoWriter(videoPath, fourcc, fps,
			(self.frames[0].shape[1], self.frames[0].shape[0]), True)
		self.Q = Queue()
		self.tsQ = Queue()
		# loop over the frames in the deque structure and add them
		# to the queue
		# We are iterating over frames, assuming one to one frame-timestamp match
		# in theory, we are passing tupples, so this should hold
		for i in range(len(self.frames), 0, -1):
			self.Q.put(self.frames[i - 1])
			self.tsQ.put(self.timestamps[i - 1])
		# start a thread write frames to the video file
		self.thread = Thread(target=self.write, args=())
		self.thread.daemon = True
		self.thread.start()

	def write(self):
		# keep looping
		while True:
			# if we are done recording, exit the thread
			if not self.recording:
				return
			# check to see if there are entries in the queue
			if not self.Q.empty():
				# grab the next frame in the queue and write it
				# to the video file
				frame = self.Q.get()
				self.writer.write(frame)
				ts = self.tsQ.get()
				# TODO: this could be implemented in a separate thread, but maybe not worth it?
				self.write_timestamp(timestamp=ts)
			# otherwise, the queue is empty, so sleep for a bit
			# so we don't waste CPU cycles
			else:
				time.sleep(self.timeout)

	def write_timestamp(self, timestamp):
		timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f')
		# this will write timestamps to file
		# mind that timestamp must be in a [] for numpy to like it
		with open(self.timestampPath,'a') as outfile:
			np.savetxt(outfile, [timestamp], delimiter=',', fmt='%s')

	def flush(self):
		# empty the queue by flushing all remaining frames to file
		while not self.Q.empty():
			frame = self.Q.get()
			self.writer.write(frame)
			ts = self.tsQ.get()
			self.write_timestamp(timestamp=ts)

	def finish(self):
		# indicate that we are done recording, join the thread,
		# flush all remaining frames in the queue to file, and
		# release the writer pointer
		self.recording = False
		self.thread.join()
		self.flush()
		self.writer.release()
