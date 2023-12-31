# CODE THAT USES THE PRETRAINED CNN MODEL FOR GESTURE RECOGNITION

import cv2
import imutils
import serial
import numpy as np
from sklearn.metrics import pairwise
import time
from keras.datasets import mnist
from keras.models import Sequential
from keras.models import model_from_json
from keras.layers import Dense
from keras.layers import Dropout
from keras.utils import np_utils
import tkinter
import winsound
import tkinter as tk
import glob

bg = None
global loaded_model
imageSize = 50


# Function - To find the running average over the background

# def executeThis():
#    print("Gesture 0")


def run_avg(image, accumWeight):
    global bg
    if bg is None:
        bg = image.copy().astype("float")
        return

    cv2.accumulateWeighted(image, bg, accumWeight)


# Function - To segment the region of hand in the image
def segment(image, threshold=30):
    global bg
    # find the absolute difference between background and current frame
    diff = cv2.absdiff(bg.astype("uint8"), image)
    cv2.imshow("diff = grey - bg", diff)
    cv2.imshow("grey", image)
    # threshold the diff image so that we get the foreground
    thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)[1]
    (_,cnts,h) = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(cnts) == 0:
        return
    else:
        segmented = max(cnts, key=cv2.contourArea)
        return (thresholded, segmented)


# Function - here's where the main recognition work happens
def count(thresholded, segmented):
    thresholded = cv2.resize(thresholded, (imageSize, imageSize))
    thresholded = thresholded.reshape(1, 1, imageSize, imageSize).astype('float32')
    thresholded = thresholded / 255
    prob = loaded_model.predict(thresholded)
    if (max(prob[0]) > .99995):
        return loaded_model.predict_classes(thresholded)
    return


# Main function
if __name__ == "__main__":

    # load the structure of the model
    json_file = open('C:/Users/sai pranav/Desktop/trainedModel.json', 'r')
    loaded_model_json = json_file.read()
    json_file.close()
    loaded_model = model_from_json(loaded_model_json)

    # load weights into new model
    loaded_model.load_weights("C:/Users/sai pranav/Desktop/modelWeights.h5")
    print("\n\n\n\nLoaded model from disk\n\n\n\n")
    loaded_model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    accumWeight = 0.5

    # get the reference to the webcam
    camera = cv2.VideoCapture(0)

    # region of interest (ROI) coordinates
    top, right, bottom, left = 10, 350, 225, 590

    # initialize num of frames
    num_frames = 0

    # calibration indicator
    calibrated = False
    #
    #    window = tkinter.Tk()
    # keep looping, until interrupted
    while (True):
        # get the current frame
        (grabbed, frame) = camera.read()

        # resize the frame
        frame = imutils.resize(frame, width=700)

        # flip the frame so that it is not the mirror view
        frame = cv2.flip(frame, 1)

        # clone the frame
        clone = frame.copy()

        # get the height and width of the frame
        (height, width) = frame.shape[:2]

        # get the ROI
        roi = frame[top:bottom, right:left]

        # convert the roi to grayscale and blur it
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        # to get the background, keep looking till a threshold is reached
        # so that our weighted average model gets calibrated
        if num_frames < 30:
            run_avg(gray, accumWeight)
            if num_frames == 1:
                print(">>> Please wait! Program is calibrating the background...")
            elif num_frames == 29:
                print(">>> Calibration successfull. ...")
        else:
            # segment the hand region
            hand = segment(gray)
            time.sleep(.2)

            # check whether hand region is segmented
            if hand is not None:

                (thresholded, segmented) = hand
                # draw the segmented region and display the frame
                cv2.drawContours(clone, [segmented + (right, top)], -1, (0, 0, 255))

                # count the number of fingers
                fingers = count(thresholded, segmented)
                # ser=serial.Serial('com3',9600)
                # print(fingers)
                #============ Change 2 =============================#
                '''Changing Conditional Statement to be consitent with Encoding of Neural Network'''
                if (fingers == 1):
                    print(5)
                    cv2.putText(clone, "[5]", (200, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 35), 2)
                else:
                    print(0)
                    cv2.putText(clone, str(fingers), (200, 80), cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 35), 2)
                # show the thresholded image

                cv2.imshow("Thesholded", thresholded)

        # draw the segmented hand
        cv2.rectangle(clone, (left, top), (right, bottom), (0, 255, 0), 2)

        # increment the number of frames
        num_frames += 1

        # display the frame with segmented hand
        cv2.imshow("Video Feed", clone)

        # observe the keypress by the user
        keypress = cv2.waitKey(1) & 0xFF

        # if the user has pressed "q", then stop looping
        if keypress == ord("q"):
            break

# free up memory
camera.release()
cv2.destroyAllWindows()