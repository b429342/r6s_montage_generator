import cv2         #used to get frames 
import os          #allows to search directory 
import matplotlib.pyplot as plt                     #'as' helps us shorten the name
import pytesseract                         #used to extract text
import numpy as np
import subprocess
import ffmpeg 
import tempfile 

clip_path = r"C:\Users\David Da Masta\Videos\Radeon ReLive\Tom Clancy's Rainbow Six Siege\Tom Clancy's Rainbow Six Siege_2025.06.26-03.27.mp4"     #stores the clip is located
clip = cv2.VideoCapture(clip_path)    #gets the actual clip 
print(f"Checking file: {clip_path}")
print(f"File exists: {os.path.exists(clip_path)}")
print(f"File readable: {os.access(clip_path, os.R_OK)}")    

def getplayername():
    return input("Name detected in kill feed: ").strip().lower()

def makeFolders():                  #COMMENT OUT THE CREATION OF FOLDERS THAT AREN'T THE CLIPS FOLDER, THE OTHERS ARE FOR DEBUGGING
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
    killtimeslist = []
    currentframe = 0                                       #makes sure it starts at the first frame
    x_start, y_start, x_end, y_end = 1450, 200, 1700, 335  #cords for the killfeed
    fps = clip.get(cv2.CAP_PROP_FPS)
    total_frames = int(clip.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_seconds = 4              
    skip_frames = int(fps * skip_seconds)

    while currentframe<total_frames:                                     #Makes sure loop stops when video is over. 
        clip.set(cv2.CAP_PROP_POS_FRAMES, currentframe)           #sets clip to next frame     

        ret, frame = clip.read()                           #tries to read next frame

        if ret:                                            #if it gets frame:
            frame = frame[y_start:y_end, x_start:x_end]    #crops the frame to only get the killfeed
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #Grayscales the frame     
            (thresh, blackAndWhiteImage) = cv2.threshold(gray_frame, 195, 255, cv2.THRESH_BINARY)        #black and whites the frame 
            resized_frame = cv2.resize(blackAndWhiteImage, (0,0), fx=2.0, fy=2.0, interpolation= cv2.INTER_LINEAR)  #resizing using scaling to make bigger 

            #following should be used to debug and see the frames. 
            #name = os.path.join(framesFolder, f' frame {currentframe}.jpg')  #names it, ensures it's printed in the frames folder
            #print('Creating...' + name)                                    #print to terminal that it's being made, used to debug 

            #cv2.imwrite(name, resized_frame)                             #writes frame to our exrtracted frames folder 
            
            text = pytesseract.image_to_string(resized_frame, config= '--psm  7 '                  #gets text from image w/ psm 7 and whitelisted characters
            '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')   
            clean_text = text.strip().lower()                                      #removes white spaces and forces lowercase 

            #with open(textFile, 'a') as extractedText:              
                #print(str(currentframe) + clean_text , file=extractedText )                    #prints text to file 

            currentframe += skip_frames                                                      #skip amount of frames calculated above      

            #with open(killFeed, 'a') as killtimes:     #comment out, this is for debugging       
                #if player_name in clean_text:   
                    #print(str(clip.get(cv2.CAP_PROP_POS_MSEC)) , file=killtimes) 

            if player_name in clean_text:                                             #adds kill to to list so folder doesn't need to be made. 
                killtimeslist.append(str(clip.get(cv2.CAP_PROP_POS_MSEC)))           


        else:
            break                                                         #when no more frames to read it stops. 

    clip.release()
    print("frames saved.")
    return killtimeslist                                                #list is made inside this function so for it to be used elsewhere it needs to be returned. 


def getClips(video_path, killtimeslist, clips_folder):        #IF CLIPS AREN'T DELETED THEN IT NO WORK!!!!
    print("extracting clips")
    i = 1
    listofclips = []
    for kill_time_ms in killtimeslist: 
        
        seconds = float(kill_time_ms) /1000
        start_Clip = str(max(0, seconds - 4))
        end_clip = str(seconds + 4)
        clipname = f'clip_{i}.mp4'                     #Adds every clip name to a list so we can append.  

        output = os.path.join(clips_folder, clipname)  #names the clip and makes sure it goes to the clips folder
        listofclips.append(output) 

        subprocess.run(['ffmpeg', '-i', video_path, '-ss', start_Clip, '-to', end_clip, '-c:v', 'copy', '-c:a', 'copy', output], capture_output=True, text=True)

        i+=1        #adding 1 to i
    print("clips done.")
    return listofclips                                  #Lets us use this list in our appending function

def concatClips(listofclips):
    print("Concating clips...")
    temp = tempfile.NamedTemporaryFile(mode='w+t', delete=False)         #makes visible temp file that we can write to
    for video in listofclips:                                           #for every clip we make, we add it to a file so we can concat it. 
        absolutepath = os.path.abspath(video)
        temp.writelines(f"file '{absolutepath}'\n") 
    temp.flush()
    temp.close() 
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe' ,'0', '-i', temp.name, '-c' ,'copy' ,'outputConcat.mp4'])        #concat all the clips in the temp file. 
    os.remove(temp.name)
    print("Done concating")
    return

projectFolder, framesFolder, textFile, killFeed, clipsFolder = makeFolders()    #capturing locations as variables.
player_name = getplayername()

killtimeslist= getFrames(clip, framesFolder, textFile, killFeed) 

listofclips = getClips(clip_path, killtimeslist, clipsFolder)

answer= input('Would you like to concat the clips? Y/N:').strip().lower()   #see if user wants to concat
if answer == 'y':
    concatClips(listofclips)
else:
    print('Skipping Concatenation')
