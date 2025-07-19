"""
https://github.com/blewett/python-record-audio-video/tree/main
record-audio-video.py: Original work Copyright (C) 2025 by Blewett

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Softxware, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is a simple system for capturing on screen activities.  This is
used for producing video from on screen demo displays.  This does not
capture audio.  Better video demos add the audio after the demo has
been created.  One might use a program like "audacity" to narrate
demos.  Capture the narration while playing the video - always a better
result than driving and talking.  Add the audio using a program like
"openshot".

Load cv2:
 pip3 install opencv-python

Load tkinter:
 apt-get install python3-tk

Load ffmpeg and ffprobe
 sudo apt install ffmpeg

Load portaudio:
 sudo apt-get install portaudio19-dev
 pip3 install pyaudio

and other words like that.

"""
import threading
import pyaudio
import wave
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import time
import cv2

global timer_entry_field
global start_time

"""
should one want to do this in a function rather than inline

def timer_task():
    global start_time
    global timer_entry_field

    elapsed = str(int(time.time() - start_time))

    try:
        timer_entry_field.delete(0, "end")
        timer_entry_field.insert(0, elapsed)
    except:
        pass
"""

class RepeatingTimerThread(threading.Thread):
    def __init__(self, interval, function, *args, **kwargs):
    #def __init__(self, interval, function):
        super().__init__()
        self.interval = interval
        #self.function = function
     
        self.args = args
        self.kwargs = kwargs
     
        self.stop_event = threading.Event()
        self.running = False


    def run(self):
        # print("[timer] started...")
        global start_time
        global timer_entry_field

        self.running = True

        start_time = time.time()

        while not self.stop_event.is_set():
            # self.function(*self.args, **self.kwargs)
            if self.running == False:
                break

            elapsed = str(int(time.time() - start_time))
            try:
                timer_entry_field.delete(0, "end")
                timer_entry_field.insert(0, elapsed)
            except:
                pass

            self.stop_event.wait(self.interval)


    def stop(self):
        self.running = False
        self.stop_event.set()


class AudioRecordingThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.chunk = 1024
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.frames = []
        print()
        print("Ignore the following audio selection messages")
        print()
        self.p = pyaudio.PyAudio()
        print()
        print("end of ignored audio selection messages")
        print()

        self.stream = None
        self.running = False

    def load(self, string_name):
        self.string_name = string_name
        self.stream = self.p.open(format=self.format,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  frames_per_buffer=self.chunk)

    def run(self):
        # print("[audio] Recording started...")
        self.running = True

        while self.running:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # Save audio to WAV
        self.output_filename = "audio" + self.string_name + ".wav"
        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        # print(f"[audio] Recording saved to {self.output_filename}")


    def stop(self):
        self.running = False


class VideoRecordingThread(threading.Thread):
    def __init__(self, fps=10.0, resolution=(640, 480), device_index=0):
        super().__init__()
        
        self.fps = fps
        self.resolution = resolution
        self.device_index = device_index
        self.cap = None
        self.out = None

        self.cap = cv2.VideoCapture(self.device_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.running = False

    def load(self, string_name):
        self.output_filename = "video"+ string_name + ".avi"
        self.out = cv2.VideoWriter(self.output_filename, self.fourcc, 
                                   self.fps, self.resolution)
        #ret, frame = self.cap.read()


    def run(self):
        # print("[video] Recording started...")
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if ret != True:
                break

            self.out.write(frame)
            # Recordingtime.sleep(1 / self.fps)

        self.cleanup()

    def stop(self):
        self.running = False

    def cleanup(self):
        if self.cap is not None:
            self.cap.release()
        if self.out is not None:
            self.out.release()


class RecorderApp:
    def __init__(self, root):
        global timer_entry_field

        self.root = root
        self.root.title("Video Recorder")

        self.data_frame = ttk.LabelFrame(root)
        self.data_frame.grid(row=0, column=1, padx=5, pady=5)
        
        self.label = ttk.Label(self.data_frame, text="Aprox. secs:")
        self.label.grid(row=0, column=0, padx=5, pady=5, sticky='w')

        self.timer_entry_field = ttk.Entry(self.data_frame, width=10)
        self.timer_entry_field.grid(row=0, column=1, padx=5, pady=5, sticky='e')
        timer_entry_field = self.timer_entry_field
        timer_entry_field.delete(0, "end")
        timer_entry_field.insert(0, "stopped")

        self.data_frame_start = ttk.LabelFrame(root)
        self.data_frame_start.grid(row=2, column=1, padx=5, pady=5)
        
        self.start_button = ttk.Button(self.data_frame_start, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=0, column=1, padx=5, pady=5)

        self.stop_button = ttk.Button(self.data_frame_start, text="Stop Recording", command=self.stop_recording, state='disabled')
        self.stop_button.grid(row=1, column=1, padx=5, pady=5)

        self.video_thread = None
        self.audio_thread = None
        self.string_name = "some string"


    def start_recording(self):
        if self.video_thread and self.video_thread.is_alive():
            print("[video]", "Already recording!")
            return

        if self.audio_thread and self.audio_thread.is_alive():
            print("[audio]", "Already recording!")
            return

        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')

        self.timer_entry_field.delete(0, "end")
        self.timer_entry_field.insert(0, "0")
        self.timer = RepeatingTimerThread(1, None)

        #
        # Create a timer that calls my_function every 1 second
        #
        # self.timer = RepeatingTimerThread(1, timer_task)
        self.timer.start()
        self.string_name = time.strftime("-%d-%m-%Y-%H-%M-%S")

        self.audio_thread = AudioRecordingThread()
        self.audio_thread.load(self.string_name)

        self.video_thread = VideoRecordingThread(fps=20.0, resolution=(640,480))
        self.video_thread.load(self.string_name)

        self.video_thread.start()
        self.audio_thread.start()



    def stop_recording(self):
        #
        # audio recorder
        #
        if self.audio_thread:
            self.audio_thread.stop()
            #self.audio_thread.join()

        if self.video_thread:
            self.video_thread.stop()
            #self.video_thread.join()


        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.timer_entry_field.delete(0, "end")
        self.timer_entry_field.insert(0, "stopped")

        self.timer.stop()
        self.timer.running = False


def on_closing():
    # if messagebox.askokcancel("Exit?", "Do you want to exit this program?"):

    for thread in threading.enumerate():
        try:
            thread.running = False
        except:
            pass

    root.destroy()


if __name__ == "__main__":
    # check for the camera
    camera_number = 0
    try:
        cap = cv2.VideoCapture(camera_number)
    except:
        pass

    if (cap.isOpened() == False): 
        print()
        print("audio-video-record.py cannot open the camera: " + str(camera_number))
        print()
        exit(0)

    cap.release()

    root = tk.Tk()
    app = RecorderApp(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
