
import cv2
import argparse
import numpy as np

import os
import h5py

class Video:

	def __init__(self, video_file):
		self.path=video_file
		self.name = video_file.split('/')[-1].split('.')[0]
		self.extension = video_file.split('/')[-1].split('.')[1]
		#print self.name

		self.cap = cv2.VideoCapture(self.path)
		self.frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

		if self.frames==0:
			print ('ERROR: VIDEO NOT FOUND')
			return
		else:
			self.fps=self.cap.get(cv2.cv2.CAP_PROP_FPS)
			self.width=self.cap.get(cv2.cv2.CAP_PROP_FRAME_WIDTH)
			self.height=self.cap.get(cv2.cv2.CAP_PROP_FRAME_HEIGHT)
			"""
			print('FRAMES PER SECOND:', self.fps )
			print('FRAMES IN VIDEO:', self.frames )
			print('VIDEO WIDTH:',self.width)
			print('VIDEO HEIGHT:',self.height)
			"""

		self.cap.release()

	def get_frames(self,frames_rate):

		# frames_rate = frames per second sampled / 0 = 100% FPS
		if(frames_rate == 0 or frames_rate == None ):
			offset =1;
		else :
			offset = np.rint(self.fps)/ frames_rate


		print ('offset = ' , offset)

		self.cap = cv2.VideoCapture(self.name)

		frame_id = 0
		folder= self.name.split('.')[0]

		if os.path.exists(folder) == 0:
				print ('Folder Created : ', folder)
				os.mkdir(folder)


		while (frame_id<self.frames):
			self.cap.set(1,frame_id);
			ret, frame = self.cap.read()
			# 000001.jpg
			frame_name =  folder + '/%06d' % (frame_id)	  + '.jpg'
			cv2.imwrite(frame_name, frame)
			frame_id=frame_id+offset

		self.cap.release()


	def display_vsumm(self):

			frames_random = np.sort(np.random.randint(self.frames, size=15))

			print (frames_random)

			self.cap = cv2.VideoCapture(self.name)

			for frame_id in frames_random:
				print (frame_id)
				self.cap.set(1,frame_id);
				ret, frame = self.cap.read()

				frame_name =  'Frame%d' % (frame_id)	  + '.jpg'
				cv2.imwrite(frame_name, frame)
				cv2.imshow('image',frame)
				cv2.waitKey(0)
				cv2.destroyAllWindows()

			self.cap.release()

	#Modified for print results
	def open_h5(self,file,video_name='video_21',key='gtscore',offset=1):

		dataset = h5py.File(file, 'r')

		num_videos = len(dataset.keys())

		print(dataset.keys())

		keyframes = dataset[video_name][key][...]

		if(key == 'gtscore' ):
			offset = int(self.frames/keyframes.size)
		else :
			offset = 1


		self.cap = cv2.VideoCapture(self.name)

		frame_id = 0
		folder='vsumm' + self.name.split('.')[0]

		if os.path.exists(folder) == 0:
				print ('Folder Created : ', folder)
				os.mkdir(folder)


		#for i in dataset['video_21']['gtscore']:
		for i in dataset[video_name][key]:

			if  i == 1:
				self.cap.set(1,frame_id)
				ret, frame = self.cap.read()
				frame_name =  folder + '/%d' % (frame_id)	  + '.jpg'
				cv2.imwrite(frame_name, frame)

			frame_id=frame_id+offset

		dataset.close()
		self.cap.release()

	def results_to_video(self,file,video_name,key,offset=1):

		dataset = h5py.File(file, 'r')

		num_videos = len(dataset.keys())

		print(dataset.keys())

		file_name='Sumarry_Air_Force'

		vid_writer = cv2.VideoWriter(
			file_name,
			cv2.VideoWriter_fourcc(*'MP4V'),
			self.fps,
			(int(self.width),int( self.height )),
    	)
		offset = 1

		self.cap = cv2.VideoCapture(self.name)


		folder='vsumm' + self.name.split('.')[0]

		if os.path.exists(folder) == 0:
				print ('Folder Created : ', folder)
				os.mkdir(folder)

		frame_id = 0

		for i in dataset[video_name][key]:

			if  i == 1:
				self.cap.set(1,frame_id)
				ret, frame = self.cap.read()
				#frame_name =  folder + '/%d' % (frame_id)	  + '.jpg'
				#cv2.imwrite(frame_name, frame)
				vid_writer.write(frame)
			frame_id += 1

		dataset.close()
		self.cap.release()
		vid_writer.release()



#/*********************************************************************************************

import video
import os

if __name__ == '__main__':

    directory = './database'

    """
    for dirname, dirnames, filenames in os.walk(directory):
        # print path to all filenames.
        for filename in filenames:
            #print(os.path.join(dirname, filename))
            actual_video=video.video(os.path.join(dirname, filename))
            actual_video.get_frames(0) #frames per second sampled
    """
    #From video to video summary
    #actual_video=video.video('Air_Force_One.mp4')
    #actual_video.results_to_video('result.h5','video_1','machine_summary')

    #From video to frames of gtscore
    #actual_video=video.video("v21.mpg")
    #actual_video.open_h5('eccv16_dataset_ovp_google_pool5.h5')

    #Sample the video to frames
    #actual_video=video.video("v21.mpg")
    #actual_video.get_frames(2) #frames per second sampled

    #From Results.h5 to Frames
    #actual_video=video.video('Air_Force_One.mp4')
    #actual_video.open_h5('result.h5','video_1','machine_summary')
