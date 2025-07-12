import cv2         
import os          
import matplotlib.pyplot as plt                   
import pytesseract                         
import numpy as np
import subprocess
import tempfile 


clip_path = r"VIDEO PATH HERE"            #Insert the full path to the clip here
clip = cv2.VideoCapture(clip_path)    
print(f"Checking file: {clip_path}")
print(f"File exists: {os.path.exists(clip_path)}")
print(f"File readable: {os.access(clip_path, os.R_OK)}")    

def getplayername():
    return input("Name detected in kill feed: ").strip().lower()

def makeFolders():                  
    projectFolder = os.path.join(os.getcwd(), "SiegeMontageOutputs")        
    os.makedirs(projectFolder, exist_ok=True )
    framesFolder = os.path.join(projectFolder, "extracted_frames")          #Optional
    os.makedirs(framesFolder, exist_ok=True)         
    textFile = os.path.join(projectFolder, "extracted_text.txt")            #optional
    killFeed = os.path.join(projectFolder, "kill_times.txt")                 #optional 
    clipsFolder = os.path.join(projectFolder, "kill_clips")
    os.makedirs(clipsFolder, exist_ok=True)

    return projectFolder, framesFolder, textFile, killFeed, clipsFolder    


def getFrames(clip, framesFolder, textFile, killFeed):
    print("Starting frame extraciton.")
    killtimeslist = []
    currentframe = 0
    x_start, y_start, x_end, y_end = 1450, 200, 1700, 335             #Cordinates for standdard aspect ratio, Needs to be changed if using another aspect ratio. 
    fps = clip.get(cv2.CAP_PROP_FPS)
    total_frames = int(clip.get(cv2.CAP_PROP_FRAME_COUNT))
    skip_seconds = 4                                                  #Change to get better kill feed readings. 
    skip_frames = int(fps * skip_seconds)

    while currentframe<total_frames:
    
        clip.set(cv2.CAP_PROP_POS_FRAMES, currentframe)

        ret, frame = clip.read()

        if ret:
            frame = frame[y_start:y_end, x_start:x_end]
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 
            (thresh, blackAndWhiteImage) = cv2.threshold(gray_frame, 195, 255, cv2.THRESH_BINARY) 
            resized_frame = cv2.resize(blackAndWhiteImage, (0,0), fx=2.0, fy=2.0, interpolation= cv2.INTER_LINEAR) 
            
            #Uncomment the following to save frames to debug.
            ''' 
            name = os.path.join(framesFolder, f' frame {currentframe}.jpg')
            print('Creating...' + name)
            cv2.imwrite(name, resized_frame)                              
            '''

            text = pytesseract.image_to_string(resized_frame, config= '--psm  7 '
            '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')   
            clean_text = text.strip().lower()

            #Uncomment the following to save the extracted text and times of the kills.
            '''
            with open(textFile, 'a') as extractedText:              
                print(str(currentframe) + clean_text , file=extractedText )   

            with open(killFeed, 'a') as killtimes:   
                if player_name in clean_text:   
                    print(str(clip.get(cv2.CAP_PROP_POS_MSEC)) , file=killtimes) 
            '''

            currentframe += skip_frames  

            if player_name in clean_text:
                killtimeslist.append(str(clip.get(cv2.CAP_PROP_POS_MSEC)))

        else:
            break

    clip.release()
    print("Frame extraction done.")
    return killtimeslist

def getClips(video_path, killtimeslist, clips_folder):
    print("extracting clips")
    i = 1
    listofclips = []
    for kill_time_ms in killtimeslist: 
        
        seconds = float(kill_time_ms) /1000
        start_Clip = str(max(0, seconds - 4))
        end_clip = str(seconds + 4)
        clipname = f'clip_{i}.mp4' 

        output = os.path.join(clips_folder, clipname) 
        listofclips.append(output) 

        subprocess.run(['ffmpeg', '-i', video_path, '-ss', start_Clip, '-to', end_clip, '-c:v', 'libx264', '-preset', 'fast','-crf', '22', '-g', '30',
                        '-keyint_min', '30','-force_key_frames', 'expr:gte(n,0)', '-x264opts', 'no-scenecut', 
                         '-vsync','cfr','-c:a', 'aac', '-b:a', '192k', output]
                        , capture_output=True, text=True)
        i+=1 
    print("clips done.")
    return listofclips 


def concatClips(listofclips):
    print("Concating clips...")
    temp = tempfile.NamedTemporaryFile(mode='w+t', delete=False)         #makes visible temp file that we can write to
    for video in listofclips:  
        absolutepath = os.path.abspath(video)
        temp.writelines(f"file '{absolutepath}'\n") 
    temp.flush()
    temp.close() 
    subprocess.run(['ffmpeg', '-f', 'concat', '-safe' ,'0', '-i', temp.name, '-c' ,'copy' ,'outputConcat.mp4'])
    os.remove(temp.name)
    print("Done concating")
    return

projectFolder, framesFolder, textFile, killFeed, clipsFolder = makeFolders()
player_name = getplayername()

killtimeslist= getFrames(clip, framesFolder, textFile, killFeed) 

listofclips = getClips(clip_path, killtimeslist, clipsFolder)




concatQuestion= input('Would you like to concat the clips? Y/N:').strip().lower()   
if concatQuestion == 'y':
    concatClips(listofclips)
else:
    print('Skipping Concatenation')
