import h5py as h5
import astropy
import numpy as np
import os

def readArray(fileType, directory, tag, arrayType):
	array = np.array([],dtype=float)
	for fileName in os.listdir(directory + "/" + fileType.lower() + "_" + tag + "/"):
		if tag in fileName:
			file = h5.File(directory + "/" + fileType.lower() + "_" + tag + "/" + fileName,'r')
			if len(array) != 0:
				array = np.append(array,file[arrayType],axis=0)
			else:
				array = np.array(file[arrayType],dtype=float)
	return array

def projectionMatrix(los):
	
	L1=np.array([0,1,0],dtype=float)
	L2=np.array([0,0,1],dtype=float)
	if 0 in np.sum([los,L1,L2],axis=0):
		L2=np.array([1,0,0],dtype=float)

	if not np.dot(los,[1,0,0]) in [1,-1]:
		if  np.dot(los,[0,1,0]) in [1,-1]:
				L1=np.array([1,0,0],dtype=float)
				L2=np.array([0,0,1],dtype=float)
		elif np.dot(los,[0,0,1]) in [1,-1]:
				L1=np.array([1,0,0],dtype=float)
				L2=np.array([0,1,0],dtype=float)
		else:
			L1=np.subtract(L1,(np.dot(L1,los)*los))
			L1=L1/np.linalg.norm(L1)
			L2a=np.subtract(L2,(np.dot(L2,L1)*L1))
			L2=np.subtract(L2a,(np.dot(L2,los)*los))
			L2=L2/np.linalg.norm(L2)

#This is a super dodgy way of achieving something for making a rotation animation I did
	if los[0] > 0 and los[2] >= 0:
		if L2[0] <= 0:
			L2 = -1*L2
	if los[0] > 0 and los[2] < 0:
		if L2[0] > 0:
			L2 = -1*L2
	if los[0] <= 0 and los[2] < 0:
		if L2[0] > 0:
			L2 = -1*L2
	if los[0] < 0 and los[2] > 0:
		if L2[0] < 0:
			L2 = -1*L2

	array = np.concatenate(([L1], [L2],[[0,0,0]]))
	return array

def velocityCube(obsv, directory, tag, fileType='SNAPSHOT', offset=[0,0,0],indices=[-1]):
	if not (indices[0]<1):
		position = readArray(fileType, directory, tag, '/PartType0/Coordinates')[indices]
		velocities = readArray(fileType, directory, tag, '/PartType0/Velocity')[indices]
	else:
		position = readArray(fileType, directory, tag, '/PartType0/Coordinates')
		velocities = readArray(fileType, directory, tag, '/PartType0/Velocity')

	centre = np.add(position.mean(axis=0),offset)

	lineOfSight = np.subtract(centre,obsv)
	lineOfSight = np.array(lineOfSight/np.linalg.norm(lineOfSight),dtype=float)	
	los = lineOfSight

	radialVel = np.matmul(velocities,lineOfSight)

	projMat = projectionMatrix(lineOfSight)

	posShifted = np.subtract(position,obsv)
	projection = np.matmul(posShifted,projMat.T)

	return [projection,radialVel,projMat,lineOfSight,centre]

def inregion(data,centre,sides,offset=[0,0,0]):
	indices= np.asarray(np.where((data[:,0] >= centre[0]-sides[0]+offset[0]) & (data[:,0] <= centre[0]+sides[0]+offset[0]) & (data[:,1] >= centre[1]-sides[1]+offset[1]) & (data[:,1] <= centre[1]+sides[1]+offset[1]) & (data[:,2] >= centre[2]-sides[2]+offset[2]) & (data[:,2] <= centre[2]+sides[2]+offset[2])))
	dataIn = data[indices[0],:]

	return [dataIn,indices]


#Uses the fact that a higher density region will tend to be the centre of mass the more it takes up a region
#ie. Finds a local minimum of the centre of mass
def findCentre(data,guess,dimensions,tolerance,iterMax=1e+4):#dimensions same as sides in above
	centre=data.mean(axis=0)

	offset=guess
	previous=centre
	iterations = 0
	while (all(i >= tolerance for i in np.absolute(np.subtract(offset,previous))) and iterations < iterMax):
		previous=offset
		[galaxyPos,indices]=inregion(data,centre,dimensions,offset=offset)
		offset=np.subtract(galaxyPos.mean(axis=0),centre)
		iterations += 1
	return offset