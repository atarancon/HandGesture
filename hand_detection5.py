\
import cv2
import time
#from Image import *
from webcam import WebcamVideoStream
from detections2 import Detection
from servoControl import Servo
from systemControl import System

class HandTracker:

    def __init__(self):
        self.webcam = WebcamVideoStream()
        self.webcam.start()
        self.detection = Detection()
        #self.servoYaw = Servo(205,409,0)
        #self.servoPitch = Servo(205,409,4)
        #self.servoYaw.neutralPos()
        #self.servoPitch.neutralPos()

        self.system = System()
        self.system.servoSetAllNeutral()
        #lights instances

        #hand gesture status
        self.is_okay  = False
        self.is_vhand = False
        self.is_phand = False
        self.is_palm  = False
        self.is_fist  = False

        #get location of hand when tracking
        self.x_axis = 0.0
        self.y_axis = 0.0

        #get tracker location
        self.yprime_axis = 0
        self.xprime_axis = 0

        #get middle of frame
        self.x_center = (self.webcam.camera().get(cv2.CAP_PROP_FRAME_WIDTH))/2;
        self.y_center = (self.webcam.camera().get(cv2.CAP_PROP_FRAME_HEIGHT))/2;


    def _start_up(self):

        while  self.is_okay == False:
        # get image from webcam
            image = self.webcam.read()
            print("WAITING FOR OK SIGN")

        # look for the OK sign to start up
            self.is_okay = self.detection.is_item_detected_in_image('data/ok_cascade_48x30.xml', image.copy(), 4 )

            if self.is_okay:
             # recognized OK Sign
                print("OK GESTURE Detected ")
                self.system.turnOnGreen()
                #self._delay(700)
                #self.system.turnOffGreen()
                self.is_okay = False
            # move to modes stage
                self._modes()
            else:
                self.system.blinkRed()

            if cv2.waitKey(1) == 27 :
                self._shut_down()
                break


    def _modes (self):
        self.system.turnOffGreen()
        # Look to recognize a gesture
        while True:
        # get image from webcam
            image = self.webcam.read()

        #different classifier for different modes
            self.is_phand = self.detection.is_item_detected_in_image('data/phand_cascade.xml', image, 30 )
#phand_cascade
            self.is_fist =self.detection.is_item_detected_in_image('data/fist.xml', image, 4 )
#fist.xml
            self.is_vhand =self.detection.is_item_detected_in_image('data/vhand_cascade.xml', image,4 )
#vhand_cascade
            self.is_palm =self.detection.is_item_detected_in_image('data/goodpalm.xml', image ,20)
#goodpalm

        #check which hand gesture detected

            #Fist hand gesture
            if self.is_fist:
               self.system.blinkGreen()
               self.is_fist = False
               print("Fist detected, See if it moved" )
               self.x_axis= self.detection.x_axis
               self.y_axis=self.detection.y_axis
               self._keepCenter(self.x_axis,self.y_axis)
            #Phand gesture
            if self.is_phand:
               self.system.blinkGreen()
               self.is_phand = False
               print("Phand detected, See if it moved" )
               self.x_axis= self.detection.x_axis
               self._moveFocus(self.x_axis)
            #Vhand gesture
            if self.is_vhand:
               self.system.blinkGreen()
               self.is_vhand = False
               print("Vhand detected, See if it moved" )
               self.x_axis= self.detection.x_axis
               self._powerLight()
            #Palm gesture
            if self.is_palm:
               self.system.blinkGreen()
               self.is_palm = False
               print("Palm detected, See if it moved" )
               self.x_axis= self.detection.x_axis
               self._changeLight(self.x_axis)
            #Escape from program
            if cv2.waitKey(1) == 27 :
                self._modes()
                break
        return

    def _powerButton(self):
        #turn on/off L.E.D

        return

    def _keepCenter(self , x_axis ,y_axis):
        self.system.turnOnLaser()
        flag = True
        x = 50
        while x != 0:
        # get image from webcam
            image = self.webcam.read()

        #different classifier for different modes
            self.is_fist = self.detection.is_item_detected_in_image('data/fist.xml', image, 5)

        #check which hand gesture detected

            if self.is_fist:
                self.system.blinkGreen()
                x = 50
                self.is_fist = False
                #Get new position x and y positions
                self.xprime_axis= self.detection.x_axis
                self.yprime_axis=self.detection.y_axis

                #If the new position is different from the intial position take the absoute value to find the difference
                if ((self.xprime_axis != self.x_axis  or  self.yprime_axis != self.y_axis) and (flag == True)):
                            dx = self.xprime_axis - self.x_axis
                            dx = abs(dx)

                            dy = self.yprime_axis - self.y_axis
                            dy = abs(dy)

                            print("x_axis: " , self.x_axis , " y_axis: " , self.y_axis)
                            print("Fist MOVED xprime_axis: " , self.xprime_axis , "Fist moved yprime_axis: " , self.yprime_axis)
                            print("dx: ", dx , "dy: ", dy)

                            #if above threshold for movement
                            if( dx >= 15 or dy >= 15 ):

                                #Hand Ready to be Tracked
                                flag = False
                #If the new position is not equal to the center of the screen continue
                if ((self.xprime_axis != self.x_center  or  self.yprime_axis != self.y_center) and (flag == False)):

                            print("Fist centering Going on")

                            # Calculate how far away from the center
                            dx = self.xprime_axis - self.x_center
                            dx = abs(dx)

                            dy = self.yprime_axis - self.y_center
                            dy = abs(dy)

                            print("Fist MOVED CENTERX_axis: " , self.x_center , "Fist moved CENTERY_axis: " , self.y_center)
                            print("Fist MOVED xprime_axis: " , self.xprime_axis , "Fist moved yprime_axis: " , self.yprime_axis)
                            #if above threshold for movement
                            if( dx >= 15 or dy >= 15 ):
                                print("Movement of Motors")
                                self._moveMotors(self.xprime_axis,self.yprime_axis,dx,dy)

            else:
                print("No Gesture Detected")
                self.system.blinkRed()
                x = x-1


            if cv2.waitKey(1) == 27 :
                self._shut_down()
                break

        print("___________****TIME OUT*****__________")
        self.system.blinkRed()
        self.system.blinkRed()
        self.system.turnOffLaser()
        self._start_up()
        return

    def _moveFocus(self , x_axis):
        flag = True
        x = 50
        while x != 0:
        # get image from webcam
            image = self.webcam.read()

        #different classifier for different modes
            self.is_phand = self.detection.is_item_detected_in_image('data/phand_cascade.xml', image, 5 )

        #check which hand gesture detected

            if self.is_phand:
                x = 50
                self.is_phand = False
                #Get the new x position
                self.xprime_axis= self.detection.x_axis
                #If the new x position is different from the intial position take the absoute value to find the difference
                if ((self.xprime_axis != self.x_axis) and (flag == True)):
                            dx = self.xprime_axis - self.x_axis
                            dx = abs(dx)

                            print("x_axis: " , self.x_axis)
                            print("Phand MOVED xprime_axis: " , self.xprime_axis)
                            print("dx: ", dx)

                            #if above threshold for movement
                            if( dx >= 15):

                                #Hand Ready to be Tracked
                                flag = False

                #If the new position is not equal to the center of the screen continue
                if ((self.xprime_axis != self.x_center) and (flag == False)):

                            print("Phand centering Going on")

                            # Calculate how far away from the center
                            dx = self.xprime_axis - self.x_center
                            dx = abs(dx)

                            print("Phand MOVED CENTERX_axis: " , self.x_center)
                            print("Phand MOVED xprime_axis: " , self.xprime_axis)
                            #if above threshold for movement
                            if( dx >= 15):
                                print("Adjust Focus")
                                self._moveSpotSize(self.xprime_axis,dx)

            else:
                print("No Gesture Detected")
                x = x-1


            if cv2.waitKey(1) == 27 :
                self._shut_down()
                break

        print("___________****TIME OUT*****__________")
        self.system.blinkRed()
        self._start_up()
        return

    def _changeLight(self , x_axis):
        flag = True
        x = 50
        while x != 0:
        # get image from webcam
            image = self.webcam.read()

        #different classifier for different modes
            self.is_palm  = self.detection.is_item_detected_in_image('data/goodpalm.xml', image, 12 )

        #check which hand gesture detected

            if self.is_palm:
                self.system.blinkGreen()
                x = 50
                self.is_vhand = False
                #Get new x position
                self.xprime_axis= self.detection.x_axis
                #If the new position is different from the intial position take the absoute value to find the difference
                if ((self.xprime_axis != self.x_axis) and (flag == True)):
                            dx = self.xprime_axis - self.x_axis
                            dx = abs(dx)

                            print("x_axis: " , self.x_axis)
                            print("Palm MOVED xprime_axis: " , self.xprime_axis)
                            print("dx: ", dx)

                            #if above threshold for movement
                            if( dx >= 15):

                                #Hand Ready to be Tracked
                                flag = False

                #If the new position is not equal to the center of the screen continue
                if ((self.xprime_axis != self.x_center) and (flag == False)):

                            print("PALM centering Going on")

                            #Calculate how far away from the center
                            dx = self.xprime_axis - self.x_center
                            dx = abs(dx)

                            print("PALM MOVED CENTERX_axis: " , self.x_center)
                            print("Palm MOVED xprime_axis: " , self.xprime_axis)
                            #if above threshold for movement
                            if( dx >= 15):
                                print("Adjust Light Intensity")
                                self._changeBrightness(self.xprime_axis, dx)

            else:
                print("No Gesture Detected")
                x = x-1


            if cv2.waitKey(1) == 27 :
                self._shut_down()
                break

        print("___________****TIME OUT*****__________")
        self.system.blinkRed()
        self._start_up()
        return

    def _powerLight(self):

        if(self.system.lampLight.curpos != 0):
	        print(" LIGHT OFF")
	        self.system.lampLight.setMin()
        else:
                print(" LIGHT ON")
                self.system.lampLight.setMax()

        return

    def _moveMotors(self,xpos,ypos, dx, dy):
        xcounter = 0
        ycounter = 0

        #If the new position is to the left of the center
        if(xpos < self.x_center):
            #Increase the motor
            #print("")
            if( xcounter < dx):
                #MOTOR INCREASE FUNCTION
              #  print("")
                self.system.servoYaw.increaseRate(5)
                #time.sleep(0.005)
                xcounter = xcounter+1

        #If the new position is to the right of the center
        elif( xpos > self.x_center):
            #Decrease the motor
            #print("")
            if( xcounter < dx):
                #MOTOR DECREASE FUNCTION
                #print("")
                self.system.servoYaw.decreaseRate(5)
                #time.sleep(0.005)
                xcounter = xcounter+1

        #If the new position is above the center
        if((ypos < self.y_center) and (ypos != -1)):
            #Increase the MOTOR
            if( ycounter < dy):
                #print("")
                #MOTOR INCREASE FUNCTION
                self.system.servoPitch.increaseRate(5)
                #time.sleep(0.005)
                ycounter = ycounter+1

        #If the new position is below the centering
        elif((ypos > self.y_center) and (ypos != -1)):
            #print("")
            #Decrease the Motor
            if( ycounter < dy):
                #MOTOR DECREASE FUNCTION
                #print("")
                self.system.servoPitch.decreaseRate(5)
                #time.sleep(0.005)
                ycounter = ycounter+1


        return

    def _moveSpotSize(self,xpos, dx):
        xcounter = 0
        #If the new position is to the left of the center
        if(xpos < self.x_center):
        #Increase the motor
        #print("")
            if( xcounter < dx):
            #MOTOR INCREASE FUNCTION
            #  print("")
                self.system.lampSpot.decreaseRate(5)
                xcounter = xcounter+1

        #If the new position is to the right of the center
        elif( xpos > self.x_center):
            #Decrease the motor
            #print("")
            if( xcounter < dx):
            #MOTOR DECREASE FUNCTION
            #print("")
                self.system.lampSpot.increaseRate(5)
                xcounter = xcounter+1


        return

    def _changeBrightness(self,xpos, dx):
        xcounter = 0
        #If the new position is to the left of the center
        if(xpos < self.x_center):
        #Increase the motor
        #print("")
            if( xcounter < dx):
            #MOTOR INCREASE FUNCTION
                print("Change Brightness: INCREASE")
                self.system.lampLight.increaseRate(150)
                print("CURRENT POS: " + str(self.system.lampLight.curpos))
                xcounter = xcounter+1

        #If the new position is to the right of the center
        elif( xpos > self.x_center):
            #Decrease the motor
            #print("")
            if( xcounter < dx):
            #MOTOR DECREASE FUNCTION
                print("Change Brighness: DECREASE")
                self.system.lampLight.decreaseRate(150)
                print("CURRENT POS DECREASE: " + str(self.system.lampLight.curpos))
                xcounter = xcounter+1


        return

    def _delay(self, count):
         while(count > 0):
             count-=1
         return

    #stops webcam and return camera
    def _shut_down (self):
        self.webcam.stop()
        self.webcam.stream.release()

    def main(self):
        # setup and run OpenGL
        return

# run instance of Hand Tracker
handTracker = HandTracker()
handTracker._start_up()

cv2.destroyAllWindows()
