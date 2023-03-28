import cv2
import numpy as np
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import RPi.GPIO as GPIO
import time

kit = MotorKit()

GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)


# Known face data for detecting distance
Known_distance = 21.25  # centimeters: distance to face
Known_width = 13.5  # centimeters: width of face

# Colors for line drawing
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# defining the fonts
fonts = cv2.FONT_HERSHEY_COMPLEX


# Motor location
Z_AXIS = 180
Z_AXIS_LIMITS = [0, 360]

X_AXIS = 90
Z_AXIS_LIMITS = [0, 180]


# Open_CV Face Detector
face_detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")


# focal length finder function
def Focal_Length_Finder(measured_distance, real_width, width_in_rf_image):

    # finding the focal length
    focal_length = (width_in_rf_image * measured_distance) / real_width
    return focal_length


# distance estimation functionb
def Distance_finder(Focal_Length, real_face_width, face_width_in_frame):

    distance = (real_face_width * Focal_Length) / face_width_in_frame

    # return the distance
    return distance


# This set of functions deal with video feed.


def get_faces(image):
    # converting color image to gray scale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # detecting face in image
    faces = face_detector.detectMultiScale(gray_image, 1.3, 5)

    return faces


def crop_face(face, image):
    x, y, w, h = face[0], face[1], face[2], face[3]
    # print(face)
    y = int(round(y * 0.75))
    h = int(round(h * 0.5))
    # print(y)
    # print(h)

    crop = image[y : y + h, x : x + w]
    cv2.imshow("crop", crop)
    return crop


def identify_target(image):

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_value[0], hsv_value[1])
    cv2.imshow("orange", mask)

    count_orange = np.count_nonzero(mask)
    # print(count_orange/mask.size)
    if (count_orange / mask.size) >= 0.25:
        return 1
    else:
        return 0


# The following functions are for controlling the mechanics


def move_motors(z_axis, x_axis):

    # move the z_axis,
    if z_axis > 0:
        for _ in range(z_axis):
            kit.stepper1.onestep(direction=stepper.FORWARD)
    elif z_axis < 0:
        for _ in range(z_axis, 0):
            kit.stepper1.onestep(direction=stepper.BACKWARD)

    # move the x_axis, up and down
    if x_axis > 0:
        for _ in range(x_axis):
            kit.stepper2.onestep(direction=stepper.FORWARD)
    elif x_axis < 0:
        for _ in range(x_axis, 0):
            kit.stepper2.onestep(direction=stepper.BACKWARD)

    return


def fire():
    GPIO.output(24, True)
    time.sleep(1)
    GPIO.output(24, False)
    print("fired")
    return


def aim(face, image):

    x, y, w, h = face[0], face[1], face[2], face[3]
    print("aiming")

    # cv2.rectangle(image, (x, y), (x+w, y+h), GREEN, 2)

    # finding the distance by calling function
    # Distance distance finder function need
    # these arguments the Focal_Length,
    # Known_width(centimeters),
    # and Known_distance(centimeters)
    distance = Distance_finder(Focal_length_found, Known_width, w)

    ix = capWidth / 2
    rix = round(ix * 0.10)
    x = (w / 2) + x
    # print(f'ix: {ix}    rix: {rix}      x: {x}')
    if x > (ix + rix):
        # rn = round((x-ix-rix)/10)
        move_motors(-1, 0)
        print("greater")
    elif x < (ix - rix):
        # rn = round((x-ix-rix)/10)
        move_motors(1, 0)
        print("less")
    else:
        fire()

    return


# reference_image from directory for face detection distance
ref_image = cv2.imread("refb.jpg")

# find the face width(pixels) in the reference_image
ref_image_face_width = get_faces(ref_image)[0][2]

# get the focal by calling "Focal_Length_Finder"
# face width in reference(pixels),
# Known_distance(centimeters),
# known_width(centimeters)
Focal_length_found = Focal_Length_Finder(
    Known_distance, Known_width, ref_image_face_width
)

print(Focal_length_found)

# show the reference image
# cv2.imshow("ref_image", ref_image)

# set up hsv values
hsv_value = np.load("hsv_value.npy")


# initialize the camera object/video feed
cap = cv2.VideoCapture(0)
print(cap.set(3, 1280))
print(cap.set(4, 720))
# print(cap.get(3))
# capWidth = int(round(cap.get(3))) # get float of video width then make it into an int
capWidth = 1280


# looping through frames/video feed
while True:

    # grab single frame from video feed
    _, frame = cap.read()

    target = []
    faces = get_faces(frame)
    for face in faces:
        x, y, w, h = face[0], face[1], face[2], face[3]
        cv2.rectangle(frame, (x - 10, y - 10), (x + w, y + h), RED, 2)
        cframe = crop_face(face, frame)
        if identify_target(cframe) == 1:
            # print(face)
            # print("face")
            target = face
            GPIO.output(27, True)
            break
    if len(target) == 0:
        GPIO.output(24, False)

    # print(target)
    if len(target) > 0:
        aim(target, frame)
        # x,y,w,h = target[0],target[1],target[2],target[3]

        # cv2.rectangle(frame, (x, y), (x+w+round((y+h)*.5), y+h+round((y+h)*.5)), GREEN, 2)

    # quit the program if you press 'q' on keyboard
    if cv2.waitKey(1) == ord("q"):
        break

    cv2.imshow("frame", frame)

    """ # check if the face is zero then not
    # find the distance
    if face_width_in_frame != 0:
       
        # finding the distance by calling function
        # Distance distance finder function need
        # these arguments the Focal_Length,
        # Known_width(centimeters),
        # and Known_distance(centimeters)
        Distance = Distance_finder(
            Focal_length_found, Known_width, face_width_in_frame)
 
        # draw line as background of text
        cv2.line(frame, (30, 30), (230, 30), RED, 32)
        cv2.line(frame, (30, 30), (230, 30), BLACK, 28)
 
        # Drawing Text on the screen
        #cv2.putText(
        #    frame, f"Distance: {round(Distance,2)} CM", (30, 35),
        #  fonts, 0.6, GREEN, 2)

        # Move stepper motors to aim camera/weapon
        Aim()
 
    # show the frame on the screen """


# closing the camera
cap.release()

# closing the the windows that are opened
cv2.destroyAllWindows()
