#https://stackoverflow.com/questions/75794919/how-to-segment-and-transcribe-an-audio-from-a-video-into-timestamped-segments
#requires ffmpeg downloaded and added to user env var "Path"

#import whisper
import whisper_timestamped as whisper
import sys
import json
import cv2
import pytesseract
import math

def preProcessFrame(image):
    #source: https://stackoverflow.com/a/60161328
    # Grayscale, Gaussian blur, Otsu's threshold
    #image = cv2.imread('1.png')
    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # blur = cv2.GaussianBlur(gray, (3,3), 0)
    # thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    image = cv2.resize(image,None,fx=3,fy=3)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (3,3), 0)
    image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    contours, hierarchy = cv2.findContours(image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    #image = cv2.drawContours(image, contours, -1, color=(0, 0, 0), thickness=cv2.FILLED) #makes entire image black
    image = cv2.bitwise_not(image) #flips black and white
    #the following three steps significantly reduce output quality as of now
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)
    # image = 255 - image

    # from: https://stackoverflow.com/questions/33095476/is-there-a-build-in-function-to-do-skeletonization
    #image = cv2.ximgproc.thinning(image) #works but takes long and OCR doesnt work on text yet
    return image

    # # Morph open to remove noise and invert image
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    # opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
    # invert = 255 - opening
    # return invert

def processFrame(capture, frameNum, showFrame = False):
    capture.set(cv2.CAP_PROP_POS_FRAMES, frameNum - 1) #i-1 is how module behaves per https://stackoverflow.com/a/47867180
    res, frame = capture.read()
    if res:
        image = preProcessFrame(frame)
        #data = pytesseract.image_to_data(image, lang='eng', config='--psm 6', output_type=pytesseract.Output.DICT)
        data = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
    if showFrame:
        cv2.imshow('afterPreProcess', image)
        cv2.waitKey()
    return data

fileName = sys.argv[1]
secondsMarker = 0
if len(sys.argv) >=3:
    secondsMarker = int(float(sys.argv[2]))
output = []
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

#start video capture
capture = cv2.VideoCapture(fileName, 0)
fps = capture.get(cv2.CAP_PROP_FPS)
frameCount = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

if not secondsMarker:
    audio = whisper.load_audio(fileName)
    model = whisper.load_model("base")
    result = whisper.transcribe(model, audio, language="en")
    #print(result["text"])
    segments = result["segments"]
   # endAudio = 0.0
    #i = 0
    for segment in segments:
        output.append({"start": segment["start"], "end": segment["end"], "audioText": segment["text"]})

    for entry in output:
        timeStamp = math.floor(float(entry["end"])) 
        frameNum = timeStamp * fps
        data = processFrame(capture, frameNum)
        entry["videoText"] = data
        entry["frameNum"] = frameNum
        entry["timeStamp"] = timeStamp

else:
    frameNum = round(secondsMarker * fps)
    data = processFrame(capture, frameNum, True)
    output.append({"start": secondsMarker, "videoText": data})

#output to file
outFile = open("output.json","w")
json.dump(output, outFile, indent = 6)
outFile.close()

# #loop through each frame
# frameText = []
# for i in range(0, frameCount, 10):
#     capture.set(cv2.CAP_PROP_POS_FRAMES, i - 1) #i-1 is how module behaves per https://stackoverflow.com/a/47867180
#     res, frame = capture.read()
#     if res:
#         image = preProcessFrame(frame)
#         #data = pytesseract.image_to_data(image, lang='eng', config='--psm 6', output_type=pytesseract.Output.DICT)
#         data = pytesseract.image_to_string(image, lang='eng', config='--psm 6')
#         frameText.append(data)
# print(frameText)

# Close the window
capture.release()

# De-allocate any associated memory usage
cv2.destroyAllWindows()