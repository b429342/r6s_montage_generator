import cv2         #used to get frames 
import os          #allows to search directory 
import matplotlib.pyplot as plt                     #'as' helps us shorten the name
import pytesseract                         #used to extract text
import numpy as np
import subprocess
import ffmpeg 

clip_path = "C:\\Users\\David Da Masta\\Videos\\Captures\\Rainbow Six 2025-04-13 22-05-42.mp4"     #stores the clip is located
clip = cv2.VideoCapture(clip_path)    #gets the actual clip 
print(f"Checking file: {clip_path}")
print(f"File exists: {os.path.exists(clip_path)}")
print(f"File readable: {os.access(clip_path, os.R_OK)}")    

def getplayername():
    return input("Name detected in kill feed: ").strip().lower()

def makeFolders():
    projectFolder = os.path.join(os.getcwd(), "SiegeMontageOutputs")        
    os.makedirs(projectFolder, exist_ok=True )         #shows error if false when making this directory
    framesFolder = os.path.join(projectFolder, "extracted_frames")   #makes dedicated frames folder in the parent folder
    os.makedirs(framesFolder, exist_ok=True)         
    textFile = os.path.join(projectFolder, "extracted_text.txt")  #creates folder to see ocr text
    killFeed = os.path.join(projectFolder, "kill_times.txt")   #folder for only the kill times. 
    clipsFolder = os.path.join(projectFolder, "kill_clips")
    os.makedirs(clipsFolder, exist_ok=True)

    return projectFolder, framesFolder, textFile, killFeed, clipsFolder    #return paths to use later


def getFrames(clip, framesFolder, textFile, killFeed):       #method to get frames from a clip. Takes in the clip and all the needed folders and files

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
            name = os.path.join(framesFolder, f' frame {currentframe}.jpg')  #names it, ensures it's printed in the frames folder
            print('Creating...' + name)                                    #print to terminal that it's being made, used to debug 

            cv2.imwrite(name, resized_frame)                             #writes frame to our exrtracted frames folder 
            
            text = pytesseract.image_to_string(resized_frame, config= '--psm  7 '                  #gets text from image w/ psm 7 and whitelisted characters
            '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')   
            clean_text = text.strip().lower()                                      #removes white spaces and forces lowercase 

            with open(textFile, 'a') as extractedText:              
                print(str(currentframe) + clean_text , file=extractedText )                    #prints text to file 

            skip_seconds = 4              
            currentframe += int(clip.get(cv2.CAP_PROP_FPS))* skip_seconds     #no matter the fps, it skips x seconds       

            with open(killFeed, 'a') as killtimes:          
                if player_name in clean_text:   
                    print(str(clip.get(cv2.CAP_PROP_POS_MSEC)) , file=killtimes) 

            clip.set(cv2.CAP_PROP_POS_MSEC, currentframe * 1000 / clip.get(cv2.CAP_PROP_FPS))    #sets clip to x seconds ahead      

        else:
            break                                                         #when no more frames to read it stops. 

    clip.release()
    print("frames saved.")


def getClips(video_path, kill_times_file, clips_folder):
    print("extracting clips")
    i = 1
    with open (kill_times_file, 'r') as k:
        kill_times_ms = [ float(line.strip()) for line in k if line.strip() ]  #for every line in the kill times that is stripped we get the float of that. 

    for kill_time_ms in kill_times_ms: 
        
        seconds = int(kill_time_ms) /1000
        start_Clip = str(max(0, seconds - 5))
        end_clip = str(seconds + 5)
        
        output = os.path.join(clips_folder, f' clip_{i}.mp4')  #names the clip and makes sure it goes to the clips folder
        
        subprocess.run(['ffmpeg', '-i', clip_path, '-ss', start_Clip, '-to', end_clip, '-c:v', 'copy', '-c:a', 'copy', output], capture_output=True, text=True)


        i+=1        #adding 1 to i
    
    print("clips done.")


projectFolder, framesFolder, textFile, killFeed, clipsFolder = makeFolders()    #capturing locations as variables.
player_name = getplayername()

getFrames(clip, framesFolder, textFile, killFeed) 

getClips(clip_path, killFeed, clipsFolder)