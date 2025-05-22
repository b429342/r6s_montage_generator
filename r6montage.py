import cv2         #used to get frames 
import os          #allows to search directory 
import matplotlib.pyplot as plt                     #'as' helps us shorten the name
import pytesseract                         #used to extract text
import numpy as np

clip = cv2.VideoCapture("C:\\Users\\David Da Masta\\Videos\\Captures\\Rainbow Six 2025-04-13 22-05-42.mp4")    #name of clip = the video from that file. Neds to use " and \\


def getplayername():
    return input("Name detected in kill feed: ").strip().lower()

def getFrames(clip):       #method to get frames from a clip.
    try:                               
        if not os.path.exists('extractedFrames'):           #making the folder that the frames go to
            os.makedirs('extractedFrames')
    except OSError:
        print('Error creating directory extractedFrames')   #if it can't then show error

    currentframe = 0                                       #makes sure it starts at the first frame
    x_start, y_start, x_end, y_end = 1450, 200, 1700, 335  #cords for the killfeed

   
    


    while True:                                            #infinite loop 
        ret, frame = clip.read()                           #that tries to get the next frame

        if ret:                                            #if it gets frame:
            frame = frame[y_start:y_end, x_start:x_end]    #crops the frame to only get the killfeed
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Grayscales the frame     
            (thresh, blackAndWhiteImage) = cv2.threshold(gray_frame, 195, 255, cv2.THRESH_BINARY)        #black and whites the frame 
            resized_frame = cv2.resize(blackAndWhiteImage, (0,0), fx=2.0, fy=2.0, interpolation= cv2.INTER_LINEAR)  #resizing using scaling to make bigger 

            #following should be used to debug and see the frames. 
            name = './extractedFrames/frame' + str(currentframe) + '.jpg'  #names it 
            print('Creating...' + name)                                    #print to terminal that it's being made, used to debug 

            cv2.imwrite(name, resized_frame)                             #writes frame to our exrtracted frames folder 
            

            text = pytesseract.image_to_string(resized_frame, config= '--psm  7 '                  #gets text from image w/ psm 7 and whitelisted characters
            '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')   
            clean_text = text.strip().lower()                                      #removes white spaces and forces lowercase 

            with open('extractedText', 'a') as extractedText:              
                print(str(currentframe) + clean_text , file=extractedText )                    #prints text to file 

            skip_seconds = 4              
            currentframe += int(clip.get(cv2.CAP_PROP_FPS))* skip_seconds     #no matter the fps, it skips x seconds       
            clip.set(cv2.CAP_PROP_POS_MSEC, currentframe * 1000 / clip.get(cv2.CAP_PROP_FPS))    #sets clip to x seconds ahead      


            with open('kill_times.txt', 'a') as killtimes:          
                if player_name in clean_text:    
                    print('kill at ' + str(clip.get(cv2.CAP_PROP_POS_MSEC)) , file=killtimes) 

                
        else:
            break                                                         #when no more frames to read it stops. 

    clip.release()
    print("done") 


player_name = getplayername()


getFrames(clip) 


input_folder = "extractedFrames"         #this is where ocr pulls frames from 
output_log = "kill_times.txt"            #file that has the kill times in it.