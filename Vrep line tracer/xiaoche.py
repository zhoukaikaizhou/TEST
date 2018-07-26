# -*- coding: utf-8 -*-
try:
    import vrep
except:
    print('--------------------------------------------------------------')
    print('"vrep.py" could not be imported. This means very probably that')
    print('either "vrep.py" or the remoteApi library could not be found.')
    print('Make sure both are in the same folder as this file,')
    print('or appropriately adjust the file "vrep.py"')
    print('--------------------------------------------------------------')
    print('')

import time
import sys
import ctypes

print('Program started')
vrep.simxFinish(-1)
clientID = vrep.simxStart('127.0.0.1', 19997, True, True, 5000, 5)

if clientID != -1:
    print('Connected to remote API server')
else:
    print('Failed connecting to remote API server')
    sys.exit('Program Ended')

nominalLinearVelocity = 0.3
wheelRadius = 0.027
interWheelDistance = 0.119

res, objs = vrep.simxGetObjects(clientID, vrep.sim_handle_all, vrep.simx_opmode_blocking)
if res == vrep.simx_return_ok:
    print('Number of objects in the scene: ', len(objs))
else:
    print('Remote API function call returned with error code: ', res)

time.sleep(2)

startTime = time.time()
vrep.simxGetIntegerParameter(clientID, vrep.sim_intparam_mouse_x, vrep.simx_opmode_streaming)

# Get obejects.
res, leftSensor1 = vrep.simxGetObjectHandle(clientID, "line_sensor5", vrep.simx_opmode_blocking)
res, leftSensor2 = vrep.simxGetObjectHandle(clientID, "line_sensor4", vrep.simx_opmode_blocking)
res, middleSensor1 = vrep.simxGetObjectHandle(clientID, "line_sensor3", vrep.simx_opmode_blocking)
res, middleSensor2 = vrep.simxGetObjectHandle(clientID, "line_sensor2", vrep.simx_opmode_blocking)
res, rightSensor1 = vrep.simxGetObjectHandle(clientID, "line_sensor1", vrep.simx_opmode_blocking)
res, rightSensor2 = vrep.simxGetObjectHandle(clientID, "line_sensor0", vrep.simx_opmode_blocking)
res, leftJointDynamic = vrep.simxGetObjectHandle(clientID, "left_joint", vrep.simx_opmode_blocking)  # Left wheel
res, rightJointDynamic = vrep.simxGetObjectHandle(clientID, "right_joint",
                                                  vrep.simx_opmode_blocking)  # Right wheel

if res != vrep.simx_return_ok:
    print('Failed to get sensor Handler')
    vrep.simxFinish(clientID)
    sys.exit('Program ended')





# Initialize sensors
sensorReading = [False, False, False, False, False,False]  # Left, False, Middle, Right
sensorReading[0] = (vrep.simxReadVisionSensor(clientID, leftSensor1, vrep.simx_opmode_streaming) == 1)
sensorReading[1] = (vrep.simxReadVisionSensor(clientID, leftSensor2, vrep.simx_opmode_streaming) == 1)
sensorReading[2] = (vrep.simxReadVisionSensor(clientID, middleSensor1, vrep.simx_opmode_streaming) == 1)
sensorReading[3] = (vrep.simxReadVisionSensor(clientID, middleSensor2, vrep.simx_opmode_streaming) == 1)
sensorReading[4] = (vrep.simxReadVisionSensor(clientID, rightSensor1, vrep.simx_opmode_streaming) == 1)
sensorReading[5] = (vrep.simxReadVisionSensor(clientID, rightSensor2, vrep.simx_opmode_streaming) == 1)

while time.time() - startTime < 50:
    # Try to retrieve the streamed data.
    returnCode, data = vrep.simxGetIntegerParameter(clientID, vrep.sim_intparam_mouse_x, vrep.simx_opmode_buffer)

    # Read the sensors
    sensorReading[0] = (vrep.simxReadVisionSensor(clientID, leftSensor1, vrep.simx_opmode_buffer)[1])
    sensorReading[1] = (vrep.simxReadVisionSensor(clientID, leftSensor2, vrep.simx_opmode_buffer)[1])
    sensorReading[2] = (vrep.simxReadVisionSensor(clientID, middleSensor1, vrep.simx_opmode_buffer)[1])
    sensorReading[3] = (vrep.simxReadVisionSensor(clientID, middleSensor2, vrep.simx_opmode_buffer)[1])
    sensorReading[4] = (vrep.simxReadVisionSensor(clientID, rightSensor1, vrep.simx_opmode_buffer)[1])
    sensorReading[5] = (vrep.simxReadVisionSensor(clientID, rightSensor2, vrep.simx_opmode_buffer)[1])

    # Update the sensor display
    #setLeds(display, sensorReading[0], sensorReading[1], sensorReading[2],sensorReading[3],sensorReading[4],sensorReading[5])

    # Decide about both left and right velocities.
    s = 1.0
    linearVelocityLeft = nominalLinearVelocity * s
    linearVelocityRight = nominalLinearVelocity * s

    # Trun left a little if the left sensor catches line(False), and vice versa.
    if  not sensorReading[5]:
        linearVelocityLeft = linearVelocityLeft * 1
        linearVelocityRight = linearVelocityRight * 0.1
    if not sensorReading[4]:
        linearVelocityLeft = linearVelocityLeft * 0.5
        linearVelocityRight = linearVelocityRight * 0.1
    if  not sensorReading[1]:
        linearVelocityRight = linearVelocityRight * 0.5
        linearVelocityLeft = linearVelocityLeft * 0.1
    if not sensorReading[0]:
        linearVelocityRight = linearVelocityRight * 1
        linearVelocityLeft = linearVelocityLeft * 0.1
    else:
        linearVelocityRight = linearVelocityRight * 1
        linearVelocityLeft = linearVelocityLeft * 1

    # Update both left and right velocities.
    vrep.simxSetJointTargetVelocity(clientID, leftJointDynamic, linearVelocityLeft / (s * wheelRadius),
                                    vrep.simx_opmode_oneshot)
    vrep.simxSetJointTargetVelocity(clientID, rightJointDynamic, linearVelocityRight / (s * wheelRadius),
                                    vrep.simx_opmode_oneshot)

    time.sleep(0.005)

# Stop the line tracer.
#vrep.simxSetJointTargetVelocity(clientID, leftJointDynamic, 0.0, vrep.simx_opmode_blocking)
#vrep.simxSetJointTargetVelocity(clientID, rightJointDynamic, 0.0, vrep.simx_opmode_blocking)