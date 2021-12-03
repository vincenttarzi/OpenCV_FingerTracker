# OpenCV_FingerTracker

This project utilizes Python OpenCV and Python Mouse libraries to create a real-time hand/finger tracker using the user's default webcam.

To use this application:
  1. Navigate to the "Finger Tracking and Detection" directory
  2. Run the script with "python FingerDetection.py"
  3. Place your hand in front of the camera such that your open palm covers all 9 green rectangles (this is essential for correctly separating your hand from the background)
  4. Press "z"
  
 Now that the application is running, you will be able to move your mouse around by just using your hand.
 
 A few more things:
  The software will track how many fingers you are holding up at a time and will use that number to make gestures with the mouse.
  
    - Zero fingers: With a closed fist, you will be able to move the mouse around
    - One finger: When held up for 1 second, the left mouse button will click once
    - Two fingers: When held up for 1 second, the right mouse button will click once
    - Four fingers: When held up, the mouse will scroll up
    - Five fingers: When held up, the mouse will scroll down
    
 To exit the program, press escape, or close out of the shell you are using by making a one finger gesture on the close window button!
 
 DEMO: https://drive.google.com/file/d/1d9jvwYnqnIQZjXOHTQOAFccT8WzGtJ5E/view?usp=sharing
 
 NOTES:
  - Making fine mouse movements with this program is difficult, as the center of mass of the hand histogram will always have some wiggle. It is recommended to use this in applications where the user wants to move the mouse to act as a pointer in general areas, as well as make simple mouse gestures (e.g. a PowerPoint presentation)
  - Parameters that can be tuned:
    
    - mouse.move duration can be increased or decreased. Increasing this will cause the program to slow down but make fewer mouse movements. Decreasing this will cause more jitter.
    - Gesture timers: Each gesture is run on a timer. Mouse clicks can be changed from 1 second. Scroll speed can be increased or decreased by decreasing or increasing the wheel timers respectively.
    - Window padding: To make it easier to reach the corners of your screen, I cut the camera window such that (0,0) is about 10-20% closer to the center from its original position in the very top left. This is especially needed for the bottom of the screen as it is difficult to point to the bottom of the screen without running out of space for the camera to recognize.
