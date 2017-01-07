import numpy as np
import sys, os
import scipy
from scipy import io
try:
    from binaryTools import readwriteC2 as funcs
except ImportError:
    try:
        from binaryTools import readwriteC2_220 as funcs
    except ImportError:
        try:
            from ioTools import readwrite as funcs
        except:
            assert 1==0,"Can't find ioTools, please add ~/CODE/pyTools to PYTHONPATH"

sys.path.append(os.path.dirname(sys.argv[1]))
cfg = __import__(os.path.basename(sys.argv[1])[:-3])


def SplitData(fileScp,      fileDir2,  fileDir, 
              outputName,   outDim,    outputDelta, 
              flagUseDelta, datamv,    stdT=0.000001):
    
    filePtr = open(fileDir+os.path.sep+'gen.scp', 'w')
    if len(datamv) > 0 and os.path.isfile(datamv):
        print "External Mean Variance file will be used to normalize the data"
        datamv = io.netcdf_file(datamv)
        m = datamv.variables['outputMeans'][:].copy()
        v = datamv.variables['outputStdevs'][:].copy()
        v[v<stdT] = 1.0
        assert m.shape[0]==sum(outDim), "Incompatible dimension"
    else:
        m = np.zeros([sum(outDim)])
        v = np.ones([sum(outDim)])
    
    for file in fileScp:
        if os.path.isfile(fileDir2 + os.path.sep + file) and file[-3:]=='htk':
            filePtr.write(fileDir2+os.path.sep+file+'\n')
            # the output of CURRENNT is big-endian
            data = funcs.read_htk(fileDir2 + os.path.sep + file, end='b')
            assert data.shape[1]==sum(outDim), "Dimension of "+ file +" is not"+ sum(outDim)
            data = data*v+m
            
            # extract the data from the htk output of CURRENNT 
            for index, outname in enumerate(outputName):
                sIndex = sum(outDim[:index])
                eIndex = sum(outDim[:index+1])
                
                if (flagUseDelta=='0' or flagUseDelta==0) and outputDelta[index]>1:
                    # Assume [static, delta, delta-delta]
                    eIndex = sIndex + (eIndex-sIndex)/outputDelta[index]
					
                dataOut = data[:, sIndex:eIndex]
                outname = fileDir + os.path.sep + file[:-4] + os.path.extsep + outname
                funcs.write_raw_mat(dataOut, outname)
            print "Writing acoustic data: "+ file[:-4]
        elif file[-3:]=='htk':
            print "Couln'd find file %s"+file
    filePtr.close()

if __name__ == "__main__":
    """ Split the generated .htk into multiple files
    """
    outDim       = cfg.outDim
    outputName   = cfg.outputName
    outputDelta  = cfg.outputDelta
    fileDir      = sys.argv[2]
    flagUseDelta = sys.argv[3]
    
    if len(sys.argv)==5:
        # if case that I just want to utilize the .htk from fileDir2
        # .htk in fileDir2 will be split as written into fileDir
        fileDir2 = sys.argv[4]
    else:
        fileDir2 = fileDir
    
    datamv = sys.argv[5]
    assert os.path.isdir(fileDir), "can't not find " + fileDir
    files  = os.listdir(fileDir2)
    assert len(outDim)==len(outputName), "Output dim has unequal dimension as output Name"
    assert len(outDim)==len(outputDelta), "Output dim has unequal dimension as output Delta"
    
    if 'inMask' in dir(cfg) and 'outMask' in dir(cfg):
        assert len(cfg.outMask) == len(cfg.outputName), "outMask uncompatible"
        tempoutDim = []
        for dim in cfg.outMask:
            if len(dim)>0:
                tempoutDim.append(dim[1] - dim[0])
        if len(tempoutDim)>0:
            outDim = tempoutDim
    
    SplitData(files, fileDir2, fileDir, outputName, outDim, outputDelta, flagUseDelta, datamv)
