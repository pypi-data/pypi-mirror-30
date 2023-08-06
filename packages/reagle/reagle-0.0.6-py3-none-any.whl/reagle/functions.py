import h5py as h5
import astropy
import numpy as np
import os

def readArray(fileType, directory, tag, arrayType):
	array = np.array([])
	for fileName in os.listdir(directory + "/" + fileType.lower() + "_" + tag + "/"):
		if tag in fileName:
			file = h5.File(directory + "/" + fileType.lower() + "_" + tag + "/" + fileName,'r')
			if len(array) != 0:
				array = np.append(array,file[arrayType],axis=0)
			else:
				array = np.array(file[arrayType])
	return array

def projectionMatrix(los,printA=False):
	L1=np.array([0,1,0])
	L2=np.array([0,0,1])
	if not np.dot(los,[1,0,0]) in [1,-1]:
		if  np.dot(los,[0,1,0]) in [1,-1]:
				L1=np.array([1,0,0])
				L2=np.array([0,0,1])
		elif np.dot(los,[0,0,1]) in [1,-1]:
				L1=np.array([1,0,0])
				L2=np.array([0,1,0])
		else:
			L1=np.subtract(L1,(np.dot(L1,los)*los))
			L1=L1/np.linalg.norm(L1)
			L2=np.subtract(L2,(np.dot(L2,L1)*L1))
			L2=np.subtract(L2,(np.dot(L2,los)*los))
			L2=L2/np.linalg.norm(L2)

	array = np.concatenate(([L1], [L2],[[0,0,0]]))
	if printA:
		print(array)
	return array

def velocityCube(obsv, directory, tag, fileType='SNAPSHOT')
	#obsv, the point to observe from as a 3-list
	position = readArray(fileType, directory, tag, '/PartType0/Coordinates')
	velocities = readArray(fileType, directory, tag, '/PartType0/Velocity')

	centre = position.mean(axis=0)

	lineOfSight = np.subtract(obsv,centre)
	lineOfSight = lineOfSight/np.linalg.norm(lineOfSight)

	radialVel = np.matmul(velocities,lineOfSight)

	projectionMatrix = projectionMatrix(lineOfSight)

	posShifted = np.subtract(position,obsv)
	projection = np.matmul(posShifted,projectionMatrix.T)

	return [projection,radialVel,projectionMatrix,lineOfSight,centre]






#los is line of sight vector
# def projectionMatrix(los):
# 	if not (np.dot(los,[1,0,0]) in [0,1]): #Make sure LOS vector is not along x,y,z axis
# 		L1=np.array([1,0,0])
# 		L2=np.array([0,1,0])
# 	else:
# 		L1=np.array([1,1,0])
# 		L2=np.array([0,1,1])
# 		print("On axis")

# 	L1=np.subtract(L1,(np.dot(L1,los)*los))
# 	L1=L1/np.linalg.norm(L1)

	
# 	L2=np.subtract(L2,(np.dot(L2,L1)*L1))
# 	L2=np.subtract(L2,(np.dot(L2,los)*los))
# 	L2=L2/np.linalg.norm(L2)
	
# 	array = np.concatenate(([L1], [L2],[[0,0,0]]))
# 	return array