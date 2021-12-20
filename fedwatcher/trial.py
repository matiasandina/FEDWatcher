from src.VideoFeedClipper import VideoFeedClipper
import os
import time
import datetime

# init
fps = 20.0
clipper = VideoFeedClipper(output_folder=os.getcwd(),fps=fps)
iter = 0
print("Entering while loop")
print(datetime.datetime.now())
while iter < 500:
	clipper.run(showframe=True)
	time.sleep(1/fps) 
	if iter == 250:
		print("recording")
		clipper.trigger_recording()
	iter = iter + 1
	print(iter, end="\r")
clipper.stop()