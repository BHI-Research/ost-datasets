#!/usr/bin/env python

#To run python main.py -videos ../../../datasets/OVP/database -users ../../../datasets/OVP/UserSummary_CSV/


"""
H5 structure
-Video 1
---video_name : string video name without extension
---user_frames : users vs frames picks with frame ID
---frames : number of total frames in the video
---fps : frames per second from video/codec
---video_extension : format of video
---video_path : path address for recover the video
---user_summary :  frames from users in format 0-1, 
"""

import argparse
import os
import numpy as np
import magic
import h5py
import video
import csv

CSV_DELIMETER = ','

#/*********************************************************************************************    
def read_args():


	parser = argparse.ArgumentParser(description='H5 Dataset Generator - Video to H5 - UTN FRBB')

	parser.add_argument('-i', '--input', type=str,  help="Folder with videos and summaries")
	parser.add_argument('-users', '--users', type=str,  help="Folder with users summaries")
	parser.add_argument('-videos', '--videos', type=str,  help="Folder with videos ")

	parser.add_argument('-o', '--output', type=str,  help="File name for the h5 output")

	return parser.parse_args()

#/*********************************************************************************************    
def get_three (input):

	for dirname, dirnames, filenames in os.walk(input):	
		return dirname, dirnames
	return 0

#/*********************************************************************************************    
def get_videos_names (input):

	videos = []
	for dirname, dirnames, filenames in os.walk(input):	
		for filename in filenames:	
			if "video" in magic.from_file(os.path.join(dirname,filename), mime=True) :
				videos.append(filename)
	return videos



#/*********************************************************************************************    
def csv_to_matrix(file):

    file= file + '.csv'
   
    output = np.array(list(csv.reader(open(file, "rb"), delimiter="\t")))
    

  

    return output


#/*********************************************************************************************    
def detect_input_type (input):

	count_videos= 0
	
	video_folder = ""
	root ,folder_three = get_three(input)
	
	for dirname, dirnames, filenames in os.walk(input):	
		
		for filename in filenames:
			
			if "video" in magic.from_file(os.path.join(dirname,filename), mime=True) and not video_folder:
				count_videos+=1 # filename is a video
		if count_videos > 3:
			video_folder=dirname
			print ("Videos detected :  ",count_videos)
			count_videos = 0
		
	
	if len(folder_three) != 2:
		print ("2 folders was expected ", len(folder_three) , " obtained ")
	else:

		if folder_three[0] == video_folder.split('/')[-1]:
			
			print ("Users folder : ", root + folder_three[1])
			print ("Video folder : ", video_folder)
			return video_folder,root + folder_three[1]

		else :
		
			print ("Users folder : ", root + folder_three[0])
			print ("Video folder : ", video_folder)
			return video_folder,root + folder_three[0], 

#/*********************************************************************************************    
def users_frames_to_list(input):
	
	print (input + '.csv')
	file_csv = csv.reader(open(input + '.csv', "r"), delimiter=",")
	if not file_csv:
		print ("CSV File not found : ", input)
	output = np.array(list(file_csv))
	


	return  list_to_array(output,np.int32)
	

#/*********************************************************************************************    
def list_to_array (input_list,dt):

	max_size=0;
	for content in input_list :
		if len(content) > max_size:
			max_size = len(content)	

	result = np.zeros((len(input_list),max_size), dtype=dt)

	for j in range(len(input_list)):
		for i in range(len(input_list[j])):
			result[j][i]=input_list[j][i]

	return result
	
#/*********************************************************************************************    
def user_picks_expand (input,expansion):


	result = np.zeros((len(input),expansion), dtype=np.int32)

	for j in range(len(input)):
		for i in range(len(input[j])):	
			if i==0 and	input[j][i] == 0: #Frame 0 is keyframe
				result[j][input[j][i]]=1
			elif input[j][i] != 0:	
				result[j][input[j][i]]=1
	
	return result 

#/*********************************************************************************************    
def expand_zeros(input,expansion):

	#print (len(input),expansion)
	result = np.zeros((len(input),expansion), dtype=np.int32)
	#print (expansion)
	#print (input.shape)
	if expansion < len(input[0]):
		print ("FATAL ERROR USER FRAMES > VIDEO FRAMES !!! \t !!! \t !!!")



	for j in range(len(input)):
		for i in range(len(input[j] )):	
			if i < len(input):
				if input[j][i]==1:
					result[j][i]=1
				else:
					result[j][i]=0

	
	return result 

	
#/*********************************************************************************************    
def user_picks_contract (input):

	result_partial=[]
	result=[]

	for j in range(len(input)):
		for i in range(len(input[j])):	
			if input[j][i]==1:
				result_partial.append(i)
		result.append(result_partial)
		result_partial=[]
	
	return list_to_array(result,np.int32)

#/*********************************************************************************************    
def debug_count_ones (input):

	count = 0

	print (input.shape)
	for j in range(len(input)):		
		print (len(input[j]))
		for i in range(len(input[j])):	
			#print (type(input[j][i]))
			if input[j][i] > 0:
				count +=1		
		print ("Ones detected in %d : \t %d" % (j,count))
		count=0

#/*********************************************************************************************    	
def generate_h5 (input_video,input_users,output):

	with h5py.File(output + '.h5',  "w") as file:
		videos =  get_videos_names(input_video)

		for video_name in videos:
			actual_video= video.Video(os.path.join(input_video,video_name))
			group = file.create_group(actual_video.name)				
			asciiList = [n.encode("ascii", "ignore") for n in actual_video.name]
			group.create_dataset('video_name',(len(asciiList),1),"|S3",asciiList) #For python 2 = |S3, for python 3 = <U3
			asciiList = [n.encode("ascii", "ignore") for n in actual_video.path]
			group.create_dataset('video_path',(len(asciiList),1),"|S3",asciiList)
			asciiList = [n.encode("ascii", "ignore") for n in actual_video.extension]
			group.create_dataset('video_extension',(len(asciiList),1),"|S3",asciiList)
			group.create_dataset('fps',(1,),'f',actual_video.fps)
			group.create_dataset('frames',(1,),'i',actual_video.frames)			
			user_frames=users_frames_to_list(os.path.join(input_users,actual_video.name))
			
			#print (user_frames)
			if np.amax(user_frames) > 1 : #is csv with frame ID
				if actual_video.frames < np.amax(user_frames):
					print (actual_video.name, "\t" , actual_video.frames, "\t" , np.amax(user_frames),"\t",actual_video.fps, "\tPROBLEM!!!!!!!\tPROBLEM!!!!!!!" )
				else :
					print (actual_video.name, "\t" , actual_video.frames, "\t" , np.amax(user_frames),"\t",actual_video.fps)
					group.create_dataset('user_frames', (user_frames.shape),'i', user_frames)
					user_summary=user_picks_expand(user_frames,actual_video.frames)
					group.create_dataset('user_summary', (user_summary.shape),'i', user_summary)

			else: #is csv without frame ID, vector_len = video_frames
				if actual_video.frames*0.2 < len(user_frames[0]): #Summe dataset case
					print (actual_video.name, "\t" , actual_video.frames, "\t" , len(user_frames[0]),"\t",actual_video.fps)
					#debug_count_ones(user_frames)
					#print (actual_video.name)
					#user_summary=expand_zeros(user_frames,actual_video.frames)
					#user_summary=
					#debug_count_ones(user_frames)

					group.create_dataset('user_summary', (user_frames.shape),'i', user_frames)
					user_frames_with_ID=user_picks_contract(user_frames)
					group.create_dataset('user_frames', (user_frames_with_ID.shape),'i', user_frames_with_ID)
				else:
					print (actual_video.name, "\t" , actual_video.frames, "\t" , len(user_frames[0]),"\t",actual_video.fps, "\tPROBLEM!!!!!!!\tPROBLEM!!!!!!!" )

			
		
			
			

if __name__ == '__main__':


	#python main.py -i ../../../datasets/OVP/  -> Only for a path with two folders users csv and videos

	#python main.py -videos ../../../datasets/OVP/database -users ../../../datasets/OVP/UserSummary_CSV/

	args = read_args()

	if not args.output:
		args.output = 'OutputH5'

	if not args.input:
		if args.users and args.videos:			
			print ("ok!")
		else:
			print ("Error : need more args")
	else:
		args.videos,args.users = detect_input_type(args.input)
	
	
	generate_h5(args.videos,args.users,args.output)
	print ("Done ! ")

