# Python3 Program for Recording Audio and Video
The python3 program included here is used to record audio and video from a computer attached camera.  There are many application programs that do this easily.  A tkinter program to do this is some times requested.  This program is a simple threaded example that can be scavenged for code.  We hope it is helpful.

![record-audio-video](https://github.com/user-attachments/assets/6d9de141-b466-4ab5-bb4f-d1afefc9a3e4)

This is a very simple system.  It is entirely written in python and has a GUI interface.  All of that  can be modified it to do whatever one wants - easy.

This system is built using the Open Computer Vision module (cv2), python3 threading, and the tkinter GUI package.  The program also uses the linux portaudio libraries and ffmpeg for post processing.

Install these libraries after installing python3:

1. pip3 install opencv-python
2. sudo apt-get install python3-tk
3. sudo apt-get install portaudio19-dev
4. pip3 install pyaudio
5. sudo apt install ffmpeg

The following is a sample invocation of the system:

 python3 record-audio-video.py
 
 ffmpeg_audio_video_linux.sh video.avi audio.wav 

This will produce a combined audio and video file, xvideo.mp4.

I hope this helps.  You are on your own – but you already knew that.

Doug Blewett

doug.blewett@gmail.com
