
import os,sys
import numpy as np

# model dir
projdir = sys.argv[1] 
# data dir
datadir = sys.argv[2] 
trainData = np.arange(1)+1
valData =  np.array([2,])

layerSize = [100,512,512,512,512,259,259]
layerType = ["input", "feedforward_logistic", "feedforward_logistic", "feedforward_logistic", "feedforward_logistic", "feedforward_identity", "sse"]
layerName = ["input", "fl1", "fl2", "bl1", "bl2", "output", "postoutput"]
layerBias = [-1, 1.0, 1.0, 1.0, 1.0, 1.0, -1]

if os.path.isdir(os.path.dirname(projdir)):
    pass
else:
    os.mkdir(os.path.dirname(projdir))

if os.path.isdir(projdir):
    pass
else:
    os.mkdir(projdir)

# printint the config.cfg
filePtr = open(projdir+os.path.sep+'config.cfg_tmp','w')
filePtr.write("max_epochs_no_best   = 5\n")
filePtr.write("max_epochs           = 40\n")
filePtr.write("learning_rate        = 3e-5\n")
filePtr.write("network              = " + projdir+os.path.sep+'network.jsn\n')
filePtr.write("train                = true\n")

filePtr.write("train_file           = ")
filePtr.write(datadir+os.path.sep+'data.nc'+str(trainData[0]))
for x in trainData[1:]:
    filePtr.write(','+datadir+os.path.sep+'data.nc'+str(x))
filePtr.write("\n")

filePtr.write("val_file           = ")
filePtr.write(datadir+os.path.sep+'data.nc'+str(valData[0]))
for x in valData[1:]:
    filePtr.write(','+datadir+os.path.sep+'data.nc'+str(x))
filePtr.write("\n")

filePtr.write("weights_dist         = normal\nweights_normal_sigma = 0.1\nweights_normal_mean  = 0\nstochastic           = true\n")
filePtr.write("validate_every       = 1\nparallel_sequences   = 1\ninput_noise_sigma    = 0.1\nshuffle_fractions    = true\n")
filePtr.write("shuffle_sequences    = false\nmomentum = 0\nautosave  = true\n")
filePtr.close()



filePtr = open(projdir+os.path.sep+'network.jsn_tmp','w')
filePtr.write("{\n\t\"layers\": [\n")
for idx, layer in enumerate(layerSize):
    filePtr.write("\t\t{\n")
    filePtr.write("\t\t\t\"size\": %d,\n" % (layer))
    filePtr.write("\t\t\t\"name\": \"%s\",\n" % (layerName[idx]))
    if layerBias[idx]>0:
        filePtr.write("\t\t\t\"bias\": %f,\n" % (layerBias[idx]))
    filePtr.write("\t\t\t\"type\": \"%s\"\n" % (layerType[idx]))
    if idx==len(layerSize)-1:
        filePtr.write("\t\t}\n")
    else:
        filePtr.write("\t\t},\n")
filePtr.write("\t]\n}\n")
filePtr.close()
