from __future__ import print_function
import argparse
import h5py
import numpy as np
import cv2
import os

from ost import prepare_folders, computeBHI, computeCUS

AUTOMATIC_SUMMARY_FRAMES_PATH   = '/data'
USER_SUMMARIES_FRAMES_BASE_PATH = '/reference'

parser = argparse.ArgumentParser("Evaluator for OST")
parser.add_argument('-a', '--automatic_summarization', type=str, required=True)
parser.add_argument('-u', '--users_summarization', type=str, required=True)
parser.add_argument('-v', '--original_video', type=str)
parser.add_argument('-e', '--epsilon', type=float, required=True)
parser.add_argument('-d', '--distance', type=int)
parser.add_argument('-m', '--method', type=str, required=True, choices=['cus', 'bhi'])
parser.add_argument('-o', '--output', type=str)

args = parser.parse_args()


def search_extension(path,name):
    for dirname, dirnames, filenames in os.walk(path):
        for file in filenames:
            if file.split('.')[0]==name:
                return '.'+file.split('.')[1]


if __name__ == '__main__':
    uFile = h5py.File(args.users_summarization, 'r')
    aFile = h5py.File(args.automatic_summarization, 'r')

    filename = "results/" + args.output + ".txt"

    file=open(filename,"w")

    dataset_f1=[]
    dataset_kp=[]

    for key in aFile.keys():
        user_summaries = uFile[key]['user_summary']
        automatic_summary = aFile[key]['user_summary'][0,:]

        print ("Processing %s .... " % (key))
        if len(automatic_summary) != len(user_summaries[0]):
            print("PROBLEM: total frames are not equal")
            print (len(automatic_summary),len(user_summaries[0]))	  

        file_ext = search_extension(args.original_video,key)

        video_file = args.original_video + key + file_ext

        path = 'results/' + args.output + '/' + key
        automatic_summary_path = path + AUTOMATIC_SUMMARY_FRAMES_PATH
        user_summary_path = path + USER_SUMMARIES_FRAMES_BASE_PATH

        prepare_folders(user_summaries, automatic_summary, video_file, automatic_summary_path, user_summary_path)

        cap = cv2.VideoCapture(video_file)
        videoLength = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        if args.method == 'cus':
            f1, kappa = computeCUS(
                args.epsilon,
                videoLength,
                user_summary_path,
                automatic_summary_path
            )
        else:
            f1, kappa = computeBHI(
                args.epsilon,
                videoLength,
                args.distance,
                user_summary_path,
                automatic_summary_path
            )

        cap.release()
        file.write(key)
        file.write("\tF1: %lf\t" % round(f1,4))
        file.write("Kp: %lf\t\n" %round(kappa,4))

        dataset_f1.append(f1)
        dataset_kp.append(kappa)

        print('Average F1:', round(f1, 2))
        print('Average Kappa:', round(kappa, 2))
        print("****************************")

    file.write("\n\tTOTAL:\t\t %lf \t %lf" % (np.mean(dataset_f1),np.mean(dataset_kp)))
    file.close()
