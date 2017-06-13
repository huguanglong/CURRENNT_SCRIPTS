#!/usr/bin/python

import numpy as np
import sys, os
import scipy
from   scipy import io

try:
    from binaryTools import readwriteC2 as funcs
except ImportError:
    try:
        from binaryTools import readwriteC2_220 as funcs
    except ImportError:
        try:
            from ioTools import readwrite as funcs
        except:
            assert 1==0,"Can't find ioTools, please add path of pyTools to PYTHONPATH"

from speechTools import discreteF0 as f0funcs
            

sys.path.append(os.path.dirname(sys.argv[1]))
cfg = __import__(os.path.basename(sys.argv[1])[:-3])


def defaultOutput(dataOut, outname):
    funcs.write_raw_mat(dataOut, outname)

def f0Conversion(dataOut, outname):
    """ Convert the discrete F0 into continuous F0, if the data is lf0
    """
    fileDir           = os.path.dirname(outname)
    fileName          = os.path.basename(outname)
    fileBase, fileExt = os.path.splitext(fileName)
    if fileExt == '.lf0':
        f0Max, f0Min, f0Levels, f0Interpolated   = cfg.f0Info
        dataOut, vuv = f0funcs.f0Conversion(dataOut, f0Max, f0Min, f0Levels, 'd2c', f0Interpolated)
        if f0Interpolated:
            vuvFile  = fileDir + os.path.sep + fileBase + '.vuv'
            if os.path.isfile(vuvFile):
                vuv  = funcs.read_raw_mat(vuvFile, 1)
                dataOut[vuv<0.5] = 0.0
            else:
                print "Can't find %s for interpolated F0" % (vuvFile)
                
        defaultOutput(vuv, fileDir + os.path.sep + fileBase + '.vuv')
        defaultOutput(dataOut, outname)
    else:
        defaultOutput(dataOut, outname)
    
    

def SplitData(fileScp,      fileDir2,   fileDir, 
              outputName,   outDim,     outputDelta, 
              flagUseDelta, datamv,     outputMethod,
              stdT=0.000001):
    """ Split the generated HTK into acoustic features
    """
    
    filePtr = open(fileDir+os.path.sep+'gen.scp', 'w')
    
    if len(datamv) > 0 and os.path.isfile(datamv):
        print "External Mean Variance file will be used to de-normalize the data"
        datamv    = io.netcdf_file(datamv)
        m         = datamv.variables['outputMeans'][:].copy()
        v         = datamv.variables['outputStdevs'][:].copy()
        v[v<stdT] = 1.0
        assert m.shape[0]==sum(outDim), "Incompatible dimension"
    else:
        m = np.zeros([sum(outDim)])
        v = np.ones([sum(outDim)])
    
    for fileName in fileScp:
        fileBaseName, fileExt = os.path.splitext(fileName)
        if os.path.isfile(fileDir2 + os.path.sep + fileName) and fileExt=='.htk':
            filePtr.write(fileDir2+os.path.sep+fileName+'\n')
            # the output of CURRENNT is big-endian
            data = funcs.read_htk(fileDir2 + os.path.sep + fileName, end='b')
            assert data.shape[1]==sum(outDim), "Dimension of "+ fileName +" is not"+ sum(outDim)
            data = data*v+m
            
            # extract the data from the htk output of CURRENNT 
            for index, outname in enumerate(outputName):
                sIndex = sum(outDim[:index])
                eIndex = sum(outDim[:index+1])
                
                if (flagUseDelta=='0' or flagUseDelta==0) and outputDelta[index]>1:
                    # Assume [static, delta, delta-delta]
                    eIndex = sIndex + (eIndex-sIndex)/outputDelta[index]
					
                dataOut = data[:, sIndex:eIndex]
                outname = fileDir + os.path.sep + fileBaseName + os.path.extsep + outname
                outputMethod(dataOut, outname)
            print "Writing acoustic data: "+ fileBaseName
        elif fileExt=='.htk':
            print "Cannot find file %s" + fileName
    filePtr.close()

if __name__ == "__main__":
    """ Split the generated .htk into multiple files
    """
    outDim       = cfg.outDim
    outputName   = cfg.outputName
    outputDelta  = cfg.outputDelta
    fileDir      = sys.argv[2]
    flagUseDelta = sys.argv[3]
    
    # Additional operation
    if 'f0Info' in dir(cfg):
        print "Conversion on discrete F0 symbol"
        outputMethod = f0Conversion
    else:
        outputMethod = defaultOutput
    
    if len(sys.argv)==5:
        # if case that I just want to utilize the .htk from fileDir2
        # .htk in fileDir2 will be split and written into fileDir
        fileDir2 = sys.argv[4]
    else:
        fileDir2 = fileDir
    
    if 'inMask' in dir(cfg) and 'outMask' in dir(cfg):
        assert len(cfg.outMask) == len(cfg.outputName), "outMask uncompatible"
        tempoutDim = []
        for dim in cfg.outMask:
            if len(dim)>0:
                tempoutDim.append(dim[1] - dim[0])
        if len(tempoutDim)>0:
            outDim = tempoutDim
                
    datamv = sys.argv[5]
    assert os.path.isdir(fileDir), "Cannot not find " + fileDir
    
    files  = os.listdir(fileDir2)
    assert len(outDim)==len(outputName), "Config error: outDim outputName dimension mismatch"
    assert len(outDim)==len(outputDelta),"Config error: outDim outputDelta dimension mismatch"
    
    SplitData(files, fileDir2, fileDir, outputName, 
              outDim, outputDelta, flagUseDelta, datamv, outputMethod)
