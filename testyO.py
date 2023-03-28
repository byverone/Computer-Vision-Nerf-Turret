#importing the module cv2 and numpy
import cv2
import numpy as np
#reading the image which is to be masked
image = cv2.imread('B.jpg')
#defining the lower bounds and upper bounds
#lower_bound = np.array([0, 0, 0])
#upper_bound = np.array([350,55,100])
#masking the image using inRange() function
#imagemask = cv2.inRange(imagergb, lower_bound, upper_bound)

#print(list(imagemask))



hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
mask = cv2.inRange(hsv,(10, 100, 20), (25, 255, 255) )
#cv2.imshow("orange", mask)

#face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
#gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#faces = face_detector.detectMultiScale(gray_image, 1.3, 5)


#displaying the resulting masked image
cv2.imwrite("BTest.jpg", mask)


