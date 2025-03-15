# Autonomous-24-25
## 'main' Folder:

general code can be used in all platform 

## 'corner_detection' Folder:

code for corner detection and calculating orientation of the robot

How to test corner detection:
1. Change the hardcoded image file paths in Lines 8 and 9 in `detect_our_robot.py`
2. In the command line, run `python corner_detection` or `python3 corner_detection`

## 'raspberry_pi' Folder:

specific code can be used in only raspberry_pi


## 'camera_test' Folder:

test code can be used 


## 'scripts' Folder: 

bash script for automation Note: Make sure to navigate to the 'Autonomous-24-25/scripts' directionary before use

Refer to the specific README in scripts Folder

Setting the homography matrix using `homography.py`
1. Ensure your `image_flashing` branch is up to date
2. Download some NHRL cage image from a video using the same angle; ensure you know the name of the file
3. At line 6 in `homography.py`, change the filepath stored at `test_img` to your image filepath
4. Begin selecting corners by running `python homography.py` or `python3 homography.py`; a pop-up window should appear
- Pressing "esc" will kill the window and the program
- Pressing "z" will undo the last point you selected 
5. Select the corners of the arena floor IN ORDER: TOP-LEFT, TOP-RIGHT, BOTTOM-RIGHT, BOTTOM-LEFT
6. The code should automatically write the resulting homography matrix to the matrix.txt file, which is called in warp.py

How to collect data using `process_battlefield_to_images`:
1. Ensure your `image_flashing` branch is up to date
2. Manually download an NHRL fight video using the same angle; ensure you know the name of the file
3. Upload the video to the `image_flattening` directory. Because the videos are normally 3 minutes in length, we speficy them to not be tracked by Git
4. cd into the `image_flattening` directory by running `cd image_flattening` in your terminal
5. Set the parameters of the function at the bottom of the `video_stream_crop.py` file:
- The first parameter, the filepath, should be whatever you named your .mp4 file
- The second parameter is the framerate, or how often to save a frame from the video. 1-2 frames per second should suffice
6. Extract images from the video by running `python video_stream_crop.py` or `python3 video_stream_crop.py` and wait an appropriate amount of time (generally ~3 minutes)
7. The images should be saved under `image_flattening\IMG_`; download locally and use as you see fit