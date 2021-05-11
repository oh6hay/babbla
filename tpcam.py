#!/usr/bin/env python3

import cv2, os, sys, v4l2, fcntl, time, math, random
import numpy as np
import pyaudio

basename=sys.argv[1] if len(sys.argv)>1 else 'rodin'

width = 640
height = 480
FPS = 24
seconds = 1
imgs = []
for i in range(0,5):
    img=cv2.imread('640x480/%s%d.png'%(basename,i))
    img=cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    imgs.append(img)

devName = '/dev/video7'
if not os.path.exists(devName):
    print ("Warning: device does not exist",devName)
device = open(devName, 'wb')
height,width,channels = img.shape
format                      = v4l2.v4l2_format()
format.type                 = v4l2.V4L2_BUF_TYPE_VIDEO_OUTPUT
format.fmt.pix.field        = v4l2.V4L2_FIELD_NONE
format.fmt.pix.pixelformat  = v4l2.V4L2_PIX_FMT_BGR24
format.fmt.pix.width        = width
format.fmt.pix.height       = height
format.fmt.pix.bytesperline = width * channels
format.fmt.pix.sizeimage    = width * height * channels
print ("set format result (0 is good):{}".format(fcntl.ioctl(device, v4l2.VIDIOC_S_FMT, format)))
print("begin loopback write")

p=pyaudio.PyAudio()
bufcount=0
fpb=50
elapsed=0.0
starttime=time.time()
lastchange=0.0
def callback(in_data, frame_count, time_info, status):
    data = np.fromstring(in_data, dtype=np.float32)
    aval = np.linalg.norm(data)
    bufcount =+ 1
    elapsed = time.time() - starttime
    bps = bufcount / elapsed
    sys.stdout.write('\ra=%2.2f  l=%2.2f       \r'%(aval, math.log(1.0+aval)))
    if aval < .45:
        device.write(imgs[1])
        if random.randint(1,20) == 1:
            device.write(imgs[0])
    else:
        device.write(imgs[random.randint(2,4)])
    return (None, pyaudio.paContinue)

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=44100,
                input=True,
                output=False,
                frames_per_buffer=int(4000),
                stream_callback=callback)

stream.start_stream()
while stream.is_active():
    try:
        time.sleep(0.1)
    except:
        print('')
        break
stream.stop_stream()
stream.close()
p.terminate()
