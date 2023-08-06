import h5py as h5
import numpy as np
import os

def readArray(fileType, directory, tag, arrayType):
	array = []
	for fileName in os.listdir(directory + "/" + fileType.lower() + "_" + tag + "/"):
		if tag in fileName:
			file = h5.File(directory + "/" + fileType.lower() + "_" + tag + "/" + fileName,'r')
			if len(array) != 0:
				array = np.append(array,file[arrayType],axis=0)
			else:
				array = file[arrayType]
	return array

# def readArray(fileType, directory, tag, arrayType, sample=random, sampleSize=0):
# 	array = []
# 	for fileName in os.listdir(directory + "/" + fileType.lower() + "_" + tag + "/"):
# 		if tag in fileName:
# 			file = h5.File(directory + "/" + fileType.lower() + "_" + tag + "/" + fileName,'r')
# 			if len(array) != 0:
# 				array = np.append(array,file[arrayType],axis=0)
# 			else:
# 				array = file[arrayType]
# 	if sample = "random":
# 		partNum = len(array)
# 		#Create indices to sample from
# 		randomSample = np.random.choice(np.linspace(0,partNum-1,partNum),sampleSize,replace=0).astype(int)
# 		array=array[randomSample,:]
# 	return array	

#Sampling here isn't as useful because we need the sample of both coords and vels to line up

#los is line of sight vector
def projectionMatrix(los):
	if not (np.dot(los,[1,0,0]) in [0,1]): #Make sure LOS vector is not along x,y,z axis
		L1=np.array([1,0,0])
		L2=np.array([0,0,1])
	else:
		L1=np.array([1,1,0])
		L2=np.array([0,1,1])

	L1=np.subtract(L1,(np.dot(L1,los)*los))
	L1=L1/np.linalg.norm(L1)

	
	L2=np.subtract(np.subtract(L2,(np.dot(L2,L1)*L1)),(np.dot(L2,los)*los))
	L2=L2/np.linalg.norm(L2)
	
	array = np.concatenate(([L1], [L2]))
	return array