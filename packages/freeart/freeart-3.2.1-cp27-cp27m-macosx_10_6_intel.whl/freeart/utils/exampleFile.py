from freeart.configuration import fileInfo, structs, config, h5ConfigIO
import numpy


def generateTxAllIntegrated():
    outFileTx = 'txReconsIntegrated.h5'

    fp = structs.TxSinogram.TX_SINOGRAM_DATASET
    sinogram = structs.TxSinogram(
        fileInfo=fileInfo.H5MatrixFileInfo(filePath=fp),
        data=numpy.arange(100).reshape(10, 10))
    sinogram.saveTo(outFileTx)

    fp = structs.I0Sinogram.I0_DATASET
    infoFileI0 = fileInfo.H5MatrixFileInfo(filePath=fp)
    I0 = structs.I0Sinogram(data=numpy.arange(100).reshape(10, 10),
                            fileInfo=infoFileI0)
    I0.saveTo(outFileTx)
    txConf = config.TxConfig(sinogram=sinogram,
                             projections='2:6',
                             minAngle=0,
                             maxAngle=1.2,
                             dampingFactor=1.,
                             I0=I0)

    writer = h5ConfigIO.H5ConfigWriter()
    writer.write(outFileTx, txConf)

def generateTxAllOut():
    outFileTx = 'txReconsExternal.h5'

    sinogram = structs.TxSinogram(
        fileInfo=fileInfo.EDFMatrixFileInfo(filePath='sinoTx.edf'),
        data=numpy.arange(100).reshape(10, 10))
    sinogram.save()

    infoFileI0 = fileInfo.EDFMatrixFileInfo(filePath='I0.edf')
    I0 = structs.I0Sinogram(data=numpy.arange(100).reshape(10, 10),
                            fileInfo=infoFileI0)
    I0.save()
    txConf = config.TxConfig(sinogram=sinogram,
                             projections='2:6',
                             minAngle=0,
                             maxAngle=1.2,
                             dampingFactor=1.,
                             I0=I0)

    writer = h5ConfigIO.H5ConfigWriter()
    writer.write(outFileTx, txConf)

if __name__ == '__main__':
    generateTxAllIntegrated()
    generateTxAllOut()