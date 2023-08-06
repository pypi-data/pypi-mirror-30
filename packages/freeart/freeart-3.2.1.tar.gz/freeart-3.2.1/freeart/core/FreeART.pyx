# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
__authors__ = ["N. Vigano", "E. Taurel", "H. Payno"]
__license__ = "MIT"
__date__ = "01/08/2014"


import numpy as np
cimport numpy as np
from libcpp cimport bool

# The following lines ar to suppress warnings (Thanks Thomas)
# Look at thread https://mail.python.org/pipermail//cython-devel/2012-March/002137.html 

cdef extern from *:
    bint FALSE "0"
    void import_array()
    void import_umath()

if FALSE:
    import_array()
    import_umath() 

DTYPE_DB = np.float64
ctypedef np.float64_t DTYPE_DB_t
DTYPE_FL = np.float32
ctypedef np.float32_t DTYPE_FL_t

FLOAT_DAT = 0
DOUBLE_DAT = 1

version = "3.2.0"

from libcpp.string cimport string
from libcpp.vector cimport vector

ctypedef unsigned int uint32_t

cdef extern from "FreeART.h" namespace "FreeART":
    cdef cppclass FluoReconstruction:
        FluoReconstruction()

    cdef cppclass TxReconstruction:
        TxReconstruction()

    cdef cppclass DiffractReconstruction:
        DiffractReconstruction()

    cdef cppclass Position_FC:
        Position_FC()
        Position_FC(double,double,double)

    cdef cppclass BinVec3D[T]:
        BinVec3D()
        size_t getLength()
        size_t getWidth()
        size_t getHeight()
        T get(const size_t,const size_t,const size_t)
        void reset(const size_t,const size_t,const size_t)
        void push_back(T &)
        T & operator[](size_t)

    cdef cppclass DetectorSetUp:
        DetectorSetUp(Position_FC,double,double,double)

    cdef cppclass AnglesArray:
        AnglesArray()

    cdef cppclass SinogramsGeometry:
        SinogramsGeometry()

    cdef cppclass Sinograms3D[T]:
        Sinograms3D()

    cdef cppclass GenericSinogram3D[T]:
        GenericSinogram3D()
        size_t getSliceNb()
        size_t getRotNb()
        size_t getRayNb()
        T getPoint(const size_t,const size_t,const size_t)
        double getAngle(const size_t,const size_t)

    cdef cppclass AlgorithmIO:
        AlgorithmIO()
        void buildSinogramGeometry[T](const double *,const T *,const size_t,const size_t,const size_t,const vector[DetectorSetUp] &,Sinograms3D[T] &,SinogramsGeometry &) except+
        void buildSinogramGeometryTx[T](const double *,const T *,const size_t,const size_t,const size_t,Sinograms3D[T] &,SinogramsGeometry &) except+
        void createMatr[T](const T *,const size_t,const size_t,const size_t,BinVec3D[T] &)
        void createAnglesArray[T](const T *,const size_t,AnglesArray &)
        void prepareSinogramGeneration(const double,const double,size_t,SinogramsGeometry &)
        void prepareSinogramGeneration(AnglesArray &,SinogramsGeometry &)
        void prepareSinogramGeneration(const vector[DetectorSetUp] &,const double,const double,size_t,SinogramsGeometry &)
        void prepareSinogramGeneration(const vector[DetectorSetUp] &,AnglesArray &,SinogramsGeometry &)

    cdef cppclass SARTAlgorithm[T,V]:
        SARTAlgorithm(const Sinograms3D[T] &,SinogramsGeometry &) except +
        SARTAlgorithm(const Sinograms3D[T] &,const BinVec3D[T] &,SinogramsGeometry &) except +
        SARTAlgorithm(const Sinograms3D[T] &,const BinVec3D[T] &,bint,SinogramsGeometry &) except +
        SARTAlgorithm(const Sinograms3D[T] &,const BinVec3D[T] &,const BinVec3D[T] &,SinogramsGeometry &) except +
        SARTAlgorithm(const BinVec3D[T] &,SinogramsGeometry &) except +
        SARTAlgorithm(const BinVec3D[T] &,bint,SinogramsGeometry &) except +
        SARTAlgorithm(const BinVec3D[T] &,const BinVec3D[T] &,SinogramsGeometry &) except +
        SARTAlgorithm(const BinVec3D[T] &,const BinVec3D[T] &,const BinVec3D[T] &,SinogramsGeometry &) except +
        void doWork(const uint32_t) nogil except +
        void makeSinogram() except +
        void makeSinogram(BinVec3D[bint]) except +
        BinVec3D[T] &getPhantom()
        GenericSinogram3D[T] &getSinogram()

        void setOverSampling(uint32_t)
        void printReconsParam() const
        void setDampingFactor(T)
        void setRandSeedToZero(bint)
        void setI0(T)
        void setRayPointCalculationMethod(int)
        void setOutgoingRayAlgorithm(int)
        void setSubdivisionSelfAbsMat(uint32_t)
        void turnOffSolidAngle(bint)
        void setVoxelSize(T)
        T getVoxelSize() const
        uint32_t getOverSampling()
        void setUpperLimit(T)
        T getUpperLimit()
        void setLowerLimit(T)
        T getLowerLimit()


class ExceptionDiffraction(Exception):
    pass

###########################################################
#
#       base class with common methods
#
###########################################################

cdef class FreeARTBaseClass:
    """Top class which group Transmission and fluorescence backward and forward projections."""

    cdef SARTAlgorithm[double,TxReconstruction] *thisptrTxDb
    cdef SARTAlgorithm[float,TxReconstruction] *thisptrTxFl

    cdef SARTAlgorithm[double,FluoReconstruction] *thisptrFluoDb
    cdef SARTAlgorithm[float,FluoReconstruction] *thisptrFluoFl

    cdef int FlDb

    def __cinit__(self):
        self.thisptrTxFl = NULL
        self.thisptrTxDb = NULL
        self.thisptrFluoFl = NULL
        self.thisptrFluoDb = NULL

        self.FlDb = FLOAT_DAT

    def __dealloc__(self):
        pass

    def _checkPyExpSetUp(self,expSetUp):
        if not isinstance(expSetUp,list):
            print "arg is NOT a list"
            raise TypeError,"ExpSetUp argument is not a list"
        detCtr = 1
        for det in expSetUp:
            if not isinstance(det,tuple):
                errMsg = "Detector " + str(detCtr) + " is not defined using a tuple"
                raise TypeError,errMsg
            if len(det) != 2:
                errMsg = "Detector " + str(detCtr) + " does not use the correct definition (detcenter corrdinate, det size)"
                raise TypeError,errMsg
            if not isinstance(det[0],tuple):
                errMsg = "Detector " + str(detCtr) + " center position is not defined using a tuple"
                raise TypeError,errMsg
            if len(det[0]) != 3:
                errMsg = "Wrong detector " + str(detCtr) + " center position definition. Must be a tuple with 3 elements"
                raise TypeError,errMsg
            detCtr = detCtr + 1

    def _checkNumpyDat(self,sinoDat,sinoAngles,absorp = None,selfAbsorp = None):
        if sinoDat.dtype != np.float32 and sinoDat.dtype != np.float64:
            print "sinogram data not float32 or float64"
            raise TypeError,"Supported data type for sinogram data are numpy.float32 or numpy.float64"

        if sinoDat.flags.c_contiguous == False:
            print "Provided sinogram data are not passed using a NumPy C contiguous array"
            raise TypeError,"Provided sinogram data are not passed using a NumPy C contiguous array"

        if sinoAngles.dtype != np.float32 and sinoAngles.dtype != np.float64:
            print "sinogram angles not float32 or float64"
            raise TypeError,"Supported data type for sinogram angles are numpy.float32 or numpy.float64"

        if sinoAngles.flags.c_contiguous == False:
            print "Provided sinogram angles are not passed using a NumPy C contiguous array"
            raise TypeError,"Provided sinogram angles are not passed using a NumPy C contiguous array"

        if sinoDat.shape[0] != 1:
            print "Today, only sinogram with 1 slice is supported"
            raise TypeError,"Today only sinogram with 1 slice is supported"

        anglesNb = sinoAngles.shape[0]
        if sinoDat.ndim != 3 or sinoDat.shape[1] != anglesNb:
            print "Sinogram data incoherent with sinogram angles"
            raise TypeError,"Sinogram data incoherent with sinogram angles: Sinogram data does not have the correct projection number"

        if absorp is not None:
            if absorp.dtype != sinoDat.dtype:
                print "Sinogram data and absorption matrix with incoherent data types"
                raise TypeError,"Sinogram data type different than absorption matrix data type"

            if absorp.shape[0] != sinoDat.shape[2] or absorp.shape[1] != sinoDat.shape[2]:
                print "Sinogram size and absorption matrix size incoherent"
                raise TypeError,"Sinogram ray number incoherent with absorption matrix length or width"

            if absorp.flags.c_contiguous == False:
                print "Provided absorption matrix is not passed using a NumPy C contiguous array"
                raise TypeError,"Provided absorption matrix is not passed using a NumPy C contiguous array"
        
        if selfAbsorp is not None:
            if selfAbsorp.dtype != sinoDat.dtype:
                print "Sinogram data and self absorption matrix with incoherent data types"
                raise TypeError,"Sinogram data type different than self absorption matrix data type" 

            if selfAbsorp.shape[0] != sinoDat.shape[2] or selfAbsorp.shape[1] != sinoDat.shape[2]:
                print "Sinogram size and self absorption matrix size incoherent"
                raise TypeError,"Sinogram ray number incoherent with self absorption matrix length or width"               

            if selfAbsorp.flags.c_contiguous == False:
                print "Provided self-absorption matrix is not passed using a NumPy C contiguous array"
                raise TypeError,"Provided self-absorption matrix is not passed using a NumPy C contiguous array"

    def getPhantom(self):
        """
        :return: the last reconstructed phantom
                 In the case of the transmission this is the absorption.
                 In the case of fluorescence this is the materials densities
                 multiply by the matrix of interaction (emission rate of the element)
        """
        if self.FlDb == FLOAT_DAT:
            return self._getPhantomFl()
        else:
            return self._getPhantomDb()

    def _getPhantomDb(self):
            if self.thisptrTxDb is not NULL:
                C_phDb = self.thisptrTxDb.getPhantom()
            else:
                C_phDb = self.thisptrFluoDb.getPhantom()

            xmax = C_phDb.getLength()
            ymax = C_phDb.getWidth()
            zmax = C_phDb.getHeight()
            cdef np.ndarray[DTYPE_DB_t, ndim=3] hDb = np.zeros([xmax,ymax,zmax],dtype=DTYPE_DB)

            for x in range(xmax):
                for y in range(ymax):
                    hDb[x,y] = C_phDb.get(y,x,0)

            return hDb

    def _getPhantomFl(self):
            if self.thisptrTxFl is not NULL:
                C_phFl = self.thisptrTxFl.getPhantom()
            else:
                C_phFl = self.thisptrFluoFl.getPhantom()

            xmax = C_phFl.getLength()
            ymax = C_phFl.getWidth()
            zmax = C_phFl.getHeight()
            cdef np.ndarray[DTYPE_FL_t, ndim=3] hFl = np.zeros([xmax,ymax,zmax],dtype=DTYPE_FL)

            for x in range(xmax):
                for y in range(ymax):
                    hFl[x,y] = C_phFl.get(y,x,0)

            return hFl

    def setDampingFactor(self, dampingValue):
        """
        set the damping factor use by the ART algorithm.

        :param dampingValue: the new 'relaxation' factor
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setDampingFactor(dampingValue)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setDampingFactor(dampingValue)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setDampingFactor(dampingValue)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setDampingFactor(dampingValue)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def printReconsParam(self ):
        """
        Print the current values of the reconstruction parameters
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.printReconsParam()
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.printReconsParam()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.printReconsParam()
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.printReconsParam()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setOverSampling(self,oversampling):
        """
        Set algorithm oversampling sampling parameter

        :param oversampling: New oversampling sampling parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setOverSampling(oversampling)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setOverSampling(oversampling)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setOverSampling(oversampling)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setOverSampling(oversampling)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setI0(self, _I0):
        """
        Set the intensity of the source

        :param _I0: the new intensity of the source
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setI0(_I0)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setI0(_I0)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setI0(_I0)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setI0(_I0)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setRayPointCalculationMethod(self, rayPointCalculationMethod):
        """
        setRayPointCalculationMethod(self, rayPointCalculationMethod)

        :param rayPointCalculationMethod: The method to use to compute the beam's sample points values
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setRayPointCalculationMethod(rayPointCalculationMethod)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setRayPointCalculationMethod(rayPointCalculationMethod)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setRayPointCalculationMethod(rayPointCalculationMethod)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setRayPointCalculationMethod(rayPointCalculationMethod)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setRandSeedToZero(self, turnOff):
        """
        Set the seed to zero (used to simply ensure repeatability.

        :param turnOff: True if we want to force the solid angle to 0
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setRandSeedToZero(turnOff)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setRandSeedToZero(turnOff)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setRandSeedToZero(turnOff)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setRandSeedToZero(turnOff)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setOutgoingRayAlgorithm(self, outgoingrayPointCalculationMethod):
        """
        Set the algorithm to compute the outgoing rays.

        :param outgoingrayPointCalculationMethod: The way to get create the outgoing rays.
            The outgoing ray value computation will take into account this method AND the method from the beam calculation method.
            Possible values are : 

            * rawApproximation : in this case we are making the evaluation of the outgoing ray the faster as possible by computing for each rotation the mean value of some outgoing rays and taking it as the value of the voxel
            * createOneRayPerSamplePoint : in this version we are creating the real outgoing ray for each sample point on the incoming ray and computing the 'real' outgoing absorption of the ray by sampling voxels       
            * matriceSubdivision : this is the raw approximation case but by subdividing the voxels for the outgoing rays we are reducing the noise of the "raw" approximation.
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setOutgoingRayAlgorithm(outgoingrayPointCalculationMethod)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setOutgoingRayAlgorithm(outgoingrayPointCalculationMethod)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setOutgoingRayAlgorithm(outgoingrayPointCalculationMethod)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setOutgoingRayAlgorithm(outgoingrayPointCalculationMethod)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setSubdivisionSelfAbsMat(self, val):
        """
        setSubdivisionSelfAbsMat(self, val)

        :param val: The is the factor by which we will subdivide each cell of the selfAbsMat 

            .. warning:: this is used only in the case the outgoingrayPointCalculationMethod is set to matriceSubdivision
            .. warning:: in fact the cell will be subdivide on the two axis. So the cell will be devided by subdivisionSelfAbsMat*subdivisionSelfAbsMat
                      so if you set val = 3 this will devide the cell into 9 subcells
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setSubdivisionSelfAbsMat(val)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setSubdivisionSelfAbsMat(val)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setSubdivisionSelfAbsMat(val)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setSubdivisionSelfAbsMat(val)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def turnOffSolidAngle(self, turnOff):
        """
        Used to shutdown the SolidAngle computation. Can be used for debugging or to simplify some unit test 
        
        :param turnOffSolidAngle: If True we will force the solid angle to be 1. Otherwise we will compute the real value according to the detector definition.
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.turnOffSolidAngle(turnOff)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.turnOffSolidAngle(turnOff)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.turnOffSolidAngle(turnOff)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.turnOffSolidAngle(turnOff)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def getOverSampling(self):
        """
        :return: the algorithm over sampling parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                over = self.thisptrTxFl.getOverSampling()
            elif self.thisptrFluoFl is not NULL:
                over = self.thisptrFluoFl.getOverSampling()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                over = self.thisptrTxDb.getOverSampling()
            elif self.thisptrFluoDb is not NULL:
                over = self.thisptrFluoDb.getOverSampling()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        return over

    def getVoxelSizeInRealWorld(self):
        """
        :return: the algorithm over sampling parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                size = self.thisptrTxFl.getVoxelSize()
            elif self.thisptrFluoFl is not NULL:
                size = self.thisptrFluoFl.getVoxelSize()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                size = self.thisptrTxDb.getVoxelSize()
            elif self.thisptrFluoDb is not NULL:
                size = self.thisptrFluoDb.getVoxelSize()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        return size

    def setVoxelSize(self,size):
        """
        Set the voxel size (in cm)

        :param size: the new size to set for one voxel in the freeART reconstruction/projection
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setVoxelSize(size)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setVoxelSize(size)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setVoxelSize(size)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setVoxelSize(size)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def setUpperLimit(self,uppLimit):
        """
        Set algorithm upper limit parameter. Limit the reconstructed voxels value to tthis limit.

        :param uppLimit: New upper limit parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setUpperLimit(uppLimit)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setUpperLimit(uppLimit)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setUpperLimit(uppLimit)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setUpperLimit(uppLimit)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def getUpperLimit(self):
        """
        :return: the algorithm upper limit parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                upp = self.thisptrTxFl.getUpperLimit()
            elif self.thisptrFluoFl is not NULL:
                upp = self.thisptrFluoFl.getUpperLimit()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                upp = self.thisptrTxDb.getUpperLimit()
            elif self.thisptrFluoDb is not NULL:
                upp = self.thisptrFluoDb.getUpperLimit()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        return upp

    def setLowerLimit(self,lowLimit):
        """
        Set algorithm low limit parameter. Limit the reconstructed voxels value to this limit.
        setLowerLimit(self, over)

        :param lowLimit: New low limit parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:
                self.thisptrTxFl.setLowerLimit(lowLimit)
            elif self.thisptrFluoFl is not NULL:
                self.thisptrFluoFl.setLowerLimit(lowLimit)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:
                self.thisptrTxDb.setLowerLimit(lowLimit)
            elif self.thisptrFluoDb is not NULL:
                self.thisptrFluoDb.setLowerLimit(lowLimit)
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")

    def getLowerLimit(self):
        """
        :return: the algorithm low limit parameter
        """
        if self.FlDb == FLOAT_DAT:
            if self.thisptrTxFl is not NULL:  
                low = self.thisptrTxFl.getLowerLimit()
            elif self.thisptrFluoFl is not NULL:
                low = self.thisptrFluoFl.getLowerLimit()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        else:
            if self.thisptrTxDb is not NULL:  
                low = self.thisptrTxDb.getLowerLimit()
            elif self.thisptrFluoDb is not NULL:
                low = self.thisptrFluoDb.getLowerLimit()
            else:
                raise ExceptionDiffraction("Diffraction tomography not handled yet")
        return low

    def _checkAngles(self,angleList,minAngle,maxAngle,anglesNb):
        if angleList is not None:
            if minAngle is not None or maxAngle is not None or anglesNb is not None:
                print "Angles list AND minAngle, maxAngle or anglesNb specified"
                raise TypeError,"Angle list specified AND minAngle, maxAngle or AnglesNb specified!"
        else:
            if minAngle is None or maxAngle is None or anglesNb is None:
                print "Missing some angles definition"
                raise TypeError,"Missing some angles definition (minAngle, maxAngle,anglesNb)"
            if maxAngle < minAngle or maxAngle == minAngle or anglesNb <= 0:
                print "Wrong angles definition"
                raise TypeError,"Wrong angles definition"

    def _checkProvidedMatr(self,phMatr,selfphMatr = None):
        if phMatr.dtype != np.float32 and phMatr.dtype != np.float64:
            print "Phantom matrix data not float32 or float64"
            raise TypeError,"Supported data type for phantom matrix are numpy.float32 or numpy.float64"

        if phMatr.flags.c_contiguous == False:
            print "Provided phantom matrix is not passed using a NumPy C contiguous array"
            raise TypeError,"Provided phantom matrix is not passed using a NumPy C contiguous array"

        if selfphMatr is not None:
            if selfphMatr.dtype != np.float32 and selfphMatr.dtype != np.float64:
                print "Phantom self absorption matrix data not float32 or float64"
                raise TypeError,"Supported data type for phantom self absorption matrix are numpy.float32 or numpy.float64"
            
            if selfphMatr.flags.c_contiguous == False:
                print "Provided self-absorption matrix is not passed using a NumPy C contiguous array"
                raise TypeError,"Provided self-absorption matrix is not passed using a NumPy C contiguous array"


###########################################################
#
#       FreeARTBckProjection class
#
###########################################################

cdef class FreeARTBckProjection(FreeARTBaseClass):
    """The FreeART back projection class
    """
    def __cinit__(self):
        pass

    def __dealloc__(self):
        pass

    def iterate(self, numIter):
        """
        Ask algorithm to do the required number of iteration
        This method releases the python GIL in order to let other Python thread(s) run.

        :param numIter: Iteration number
        :return: The phantom absorption matrix as a 3D numpy array

        """
        if self.FlDb == DOUBLE_DAT:
            return self.__iterateDb(numIter)
        else:
            return self.__iterateFl(numIter)

    cdef __iterateDb(self,int numIter):
        cdef BinVec3D[double] C_phDb
        cdef int xmax 
        cdef int ymax
        cdef int zmax

        if self.thisptrTxDb is not NULL:
            with nogil:
                self.thisptrTxDb.doWork(numIter)
            C_phDb = self.thisptrTxDb.getPhantom()
        elif self.thisptrFluoDb is not NULL:
            with nogil:
                self.thisptrFluoDb.doWork(numIter)
            C_phDb = self.thisptrFluoDb.getPhantom()
        else:
            raise ExceptionDiffraction("Diffraction tomography not handled yet")

        xmax = C_phDb.getLength()
        ymax = C_phDb.getWidth()
        zmax = C_phDb.getHeight()
        cdef np.ndarray[DTYPE_DB_t, ndim=3] hDb = np.zeros([xmax,ymax,zmax],dtype=DTYPE_DB)

        for x in range(xmax):
            for y in range(ymax):
                hDb[x,y] = C_phDb.get(y,x,0)

        return hDb

    cdef __iterateFl(self,int numIter):
        cdef BinVec3D[float] C_phFl
        cdef int xmax 
        cdef int ymax
        cdef int zmax

        if self.thisptrTxFl is not NULL:
            with nogil:
                self.thisptrTxFl.doWork(numIter)
            C_phFl = self.thisptrTxFl.getPhantom()
        elif self.thisptrFluoFl is not NULL:
            with nogil:
                self.thisptrFluoFl.doWork(numIter)
            C_phFl = self.thisptrFluoFl.getPhantom()
        else:
            raise ExceptionDiffraction("Diffraction tomography not handled yet")

        xmax = C_phFl.getLength()
        ymax = C_phFl.getWidth()
        zmax = C_phFl.getHeight()
        cdef np.ndarray[DTYPE_FL_t, ndim=3] hFl = np.zeros([xmax,ymax,zmax],dtype=DTYPE_FL)

        for x in range(xmax):
            for y in range(ymax):
                hFl[x,y] = C_phFl.get(y,x,0)

        return hFl


###########################################################
#
#       FreeARTFwdProjection class
#
###########################################################

cdef class FreeARTFwdProjection(FreeARTBaseClass):

    def __cinit__(self):
        pass

    def __dealloc__(self):
        pass

    def makeSinogram(self,np.ndarray mask = None):
        """
        Ask algorithm to generate a sinogram. The mask has to be a numpy 2 dimensions array (data type bool) with one
        element per phantom matrix pixel. In transmission mode, the specification of a ROI using the 
        mask parameter is not supported.

        :param mask: mask to specify a Region Of Interest (ROI) - Optional

        :return:

            * A tuple with two elements which are:
            * The sinogram data as a 3 dimensions numpy array. The dimensions are slice number,
                  rotation number and ray number. Today, slice number is always 1
            * The sinogram angles (degree) as a numpy array
        """
        if mask is not None:
            if mask.dtype != np.bool:
                print "Provided mask is not a numpy array of boolean"
                raise TypeError,"Provided mask is not a numpy array of boolean"

            if mask.ndim != 2:
                print "Provided mask does not have the correct dimension (2)"
                raise TypeError,"Provided mask does not have the correct dimension (2)"

            if mask.flags.c_contiguous == False:
                print "Provided mask is not C contiguous"
                raise TypeError,"Provided mask is not a NumPy C contiguous array"

        if self.FlDb == DOUBLE_DAT:
            return self.__makeSinogramDb(mask)
        else:
            return self.__makeSinogramFl(mask)

    cdef __makeSinogramDb(self,np.ndarray mask=None):
        cdef GenericSinogram3D[double] sino
        cdef int sliceNb 
        cdef int rotNb
        cdef int rayNb
        cdef BinVec3D[bool] C_mask

        if mask is not None:
            C_mask.reset(mask.shape[0],mask.shape[1],1)
            for x in range(mask.shape[0]):
                for y in range(mask.shape[1]):
                    if mask[x,y] == True:
                        C_mask[(x * mask.shape[0]) + y] = 1
                    else:
                        C_mask[(x * mask.shape[0]) + y] = 0

        if self.thisptrTxDb is not NULL:
            if mask is None:
                self.thisptrTxDb.makeSinogram()
            else:
                self.thisptrTxDb.makeSinogram(C_mask)
            sino = self.thisptrTxDb.getSinogram()
        elif self.thisptrFluoDb is not NULL:
            if mask is None:
                self.thisptrFluoDb.makeSinogram()
            else:
                self.thisptrFluoDb.makeSinogram(C_mask)
            sino = self.thisptrFluoDb.getSinogram()
        else:
            raise ExceptionDiffraction("Diffraction tomography not handled yet")

        sliceNb = sino.getSliceNb()
        rotNb = sino.getRotNb()
        rayNb = sino.getRayNb()

        cdef np.ndarray[DTYPE_DB_t, ndim=3] sinoDat = np.zeros([sliceNb,rotNb, rayNb],dtype=DTYPE_DB)
        cdef np.ndarray[DTYPE_DB_t, ndim=1] sinoAngles = np.zeros([rotNb],dtype=DTYPE_DB)

        for x in range(rotNb):
            for y in range(rayNb):
                sinoDat[0,x,y] = sino.getPoint(0,x,y)
            sinoAngles[x] = sino.getAngle(0,x)

        return (sinoDat, sinoAngles)

    cdef __makeSinogramFl(self,np.ndarray mask=None):
        cdef GenericSinogram3D[float] sino
        cdef int sliceNb 
        cdef int rotNb
        cdef int rayNb
        cdef BinVec3D[bool] C_mask

        if mask is not None:
            C_mask.reset(mask.shape[0],mask.shape[1],1)
            for x in range(mask.shape[0]):
                for y in range(mask.shape[1]):
                    if mask[x,y] == True:
                        C_mask[(x * mask.shape[0]) + y] = 1
                    else:
                        C_mask[(x * mask.shape[0]) + y] = 0

        if self.thisptrTxFl is not NULL:
            if mask is None:
                self.thisptrTxFl.makeSinogram()
            else:
                self.thisptrTxFl.makeSinogram(C_mask)
            sino = self.thisptrTxFl.getSinogram()
        elif self.thisptrFluoFl is not NULL:
            if mask is None:
                self.thisptrFluoFl.makeSinogram()
            else:
                self.thisptrFluoFl.makeSinogram(C_mask)
            sino = self.thisptrFluoFl.getSinogram()
        else:
            raise ExceptionDiffraction("Diffraction tomography not handled yet")

        sliceNb = sino.getSliceNb()
        rotNb = sino.getRotNb()
        rayNb = sino.getRayNb()

        cdef np.ndarray[DTYPE_FL_t, ndim=3] sinoDat = np.zeros([sliceNb, rotNb, rayNb],dtype=DTYPE_FL)
        cdef np.ndarray[DTYPE_FL_t, ndim=1] sinoAngles = np.zeros([rotNb],dtype=DTYPE_FL)

        for x in range(rotNb):
            for y in range(rayNb):
                sinoDat[0, x,y] = sino.getPoint(0,x,y)
            sinoAngles[x] = sino.getAngle(0,x)

        return (sinoDat, sinoAngles)


###########################################################
#
#       Transmission reconstruction class
#
###########################################################

cdef class TxBckProjection(FreeARTBckProjection):
    """
    Class to do a FreeART reconstruction in Transmission mode

    :param sinoDat: Sinogram data. It has to be a numpy ndarray with data type float32 or float64.
            The first array dimension is the slice number, the second array dimension is the angles 
            number and the third one is the ray number. Today, slice number has to be 1
            Sinogram data has to be -ln(I / I0) with I0 being the incoming beam intensity 
            and I the beam intensity on the detector
    :param sinoAngles: Sinogram angles (degree). It has to be a numpy ndarray. Data type has to be float32 or float64 

    """
#
#  Cython ctor
#

    def __cinit__(self,np.ndarray sinoDat not None,
                  np.ndarray sinoAngles not None):
        self._checkNumpyDat(sinoDat,sinoAngles)

        if sinoAngles.dtype == np.float32:
            sinoAngles = np.ascontiguousarray(sinoAngles,dtype=np.double)

        if sinoDat.dtype == np.float32:
            self.__sartTxFl(sinoDat,sinoAngles)
        else:
            self.__sartTxDb(sinoDat,sinoAngles)

    cdef __sartTxDb(self,np.ndarray[dtype=np.double_t,ndim=3] sinoDat,np.ndarray[dtype=np.double_t,ndim=1] sinoAngles):
        cdef AlgorithmIO algoIO
        cdef Sinograms3D[double] outSinoDataDb
        cdef SinogramsGeometry sinoGeo
       
        algoIO.buildSinogramGeometryTx[double](&sinoAngles[0],&sinoDat[0,0,0],sinoDat.shape[0],sinoDat.shape[1],sinoDat.shape[2],outSinoDataDb,sinoGeo)

        self.thisptrTxDb = new SARTAlgorithm[double,TxReconstruction](outSinoDataDb,sinoGeo)
        self.FlDb = DOUBLE_DAT

    cdef __sartTxFl(self,np.ndarray[dtype=np.float32_t,ndim=3] sinoDat,np.ndarray[dtype=np.double_t,ndim=1] sinoAngles):
        cdef AlgorithmIO algoIO
        cdef Sinograms3D[float] outSinoDataFl
        cdef SinogramsGeometry sinoGeo
        
        algoIO.buildSinogramGeometryTx[float](&sinoAngles[0],&sinoDat[0,0,0],sinoDat.shape[0],sinoDat.shape[1],sinoDat.shape[2],outSinoDataFl,sinoGeo)

        self.thisptrTxFl = new SARTAlgorithm[float,TxReconstruction](outSinoDataFl,sinoGeo)
        self.FlDb = FLOAT_DAT

#
# Cython dtor
#

    def __dealloc__(self):
        if self.thisptrTxDb is not NULL:
            del self.thisptrTxDb
        else:
            del self.thisptrTxFl


###########################################################
#
#       Fluorescence reconstruction class
#
###########################################################

cdef class FluoBckProjection(FreeARTBckProjection):
    """
    Class to do a FreeART reconstruction in Fluorescence mode

    :param sinoDat: Sinogram data. It has to be a numpy 3D ndarray with data type float32 or float64
            The first array dimension is the slice number, the second array dimension is the angles 
            number and the third one is the ray number. Today, slice number has to be 1
            Sinogram data has to be -ln(I / I0) with I0 being the incoming beam intensity 
            and I the beam intensity on the detector
    :param sinoAngles: Sinogram angles (degree). It has to be a numpy ndarray. Data type has to be float32 or float64 
    :param expSetUp:
            The experiment detector set up. This is a list with one element per detector.
            Each detector is represented by a tuple with two elements which are
                #. The detector center position for the FIRST angle defined in the sinogram. This is
                   a tuple with 3 elements which are the x, y and z coordinates. The coordinate system origin
                   is the sample center. The unit is defined by the sinogram lines.  
                   For instance, if the sinogram line is 256 points long for a sample motion of 10 mm, 
                   the unit is 10/256 mm. 

                #. The detector size. The detector is supposed to be a square. The unit is the same 
                   than previously described.
    :param absorp: The phantom absorption matrix (retrieved using a previous Tx reconstruction for instance)
    :param selfAbsorp: The phantom absorption matrix in case fluorescence self absorption is taken into account
    """
#
#  Cython ctor
#

    def __cinit__(self,np.ndarray sinoDat not None,
                  np.ndarray sinoAngles not None,
                  expSetUp not None,
                  np.ndarray absorp not None,
                  np.ndarray selfAbsorp = None):
        self._checkPyExpSetUp(expSetUp)
        self._checkNumpyDat(sinoDat,sinoAngles)

        cdef vector[DetectorSetUp] C_expSetUp
        for det in expSetUp:
            detCenter = det[0]
            C_expSetUp.push_back(DetectorSetUp(Position_FC(detCenter[0],detCenter[1],detCenter[2]),det[1],0.0,0.0))

        if sinoAngles.dtype == np.float32:
            sinoAngles = np.ascontiguousarray(sinoAngles,dtype=np.double)

        if sinoDat.dtype == np.float32:
            self.__sartFluoFl(sinoDat,sinoAngles,C_expSetUp,absorp,selfAbsorp)
        else:
            self.__sartFluoDb(sinoDat,sinoAngles,C_expSetUp,absorp,selfAbsorp)
      
    cdef __sartFluoDb(self,np.ndarray[dtype=np.double_t,ndim=3] sinoDat,
                      np.ndarray[dtype=np.double_t,ndim=1] sinoAngles,
                      vector[DetectorSetUp] C_expSetUp,
                      np.ndarray[dtype=np.double_t,ndim=3] absorp,
                      np.ndarray[dtype=np.double_t,ndim=3] selfAbsorp):
        cdef AlgorithmIO algoIO
        cdef Sinograms3D[double] outSinoDataDb
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[double] absorpMatr
        cdef BinVec3D[double] selfAbsorpMatr
        
        algoIO.buildSinogramGeometry[double](&sinoAngles[0],&sinoDat[0,0,0],sinoDat.shape[0],sinoDat.shape[1],sinoDat.shape[2],C_expSetUp,outSinoDataDb,sinoGeo)
        algoIO.createMatr[double](&absorp[0,0,0],absorp.shape[0],absorp.shape[1],absorp.shape[2],absorpMatr)

        if selfAbsorp is None:
            self.thisptrFluoDb = new SARTAlgorithm[double,FluoReconstruction](outSinoDataDb,absorpMatr,sinoGeo)
        else:
            algoIO.createMatr[double](&selfAbsorp[0,0,0],selfAbsorp.shape[0],selfAbsorp.shape[1],selfAbsorp.shape[2],selfAbsorpMatr)
            self.thisptrFluoDb = new SARTAlgorithm[double,FluoReconstruction](outSinoDataDb,absorpMatr,selfAbsorpMatr,sinoGeo)
        self.FlDb = DOUBLE_DAT

    cdef __sartFluoFl(self,np.ndarray[dtype=np.float32_t,ndim=3] sinoDat,
                      np.ndarray[dtype=np.double_t,ndim=1] sinoAngles,
                      vector[DetectorSetUp] C_expSetUp,
                      np.ndarray[dtype=np.float32_t,ndim=3] absorp,
                      np.ndarray[dtype=np.float32_t,ndim=3] selfAbsorp):
        cdef AlgorithmIO algoIO
        cdef Sinograms3D[float] outSinoDataFl
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[float] absorpMatr
        cdef BinVec3D[float] selfAbsorpMatr
          
        algoIO.buildSinogramGeometry[float](&sinoAngles[0],&sinoDat[0,0,0],sinoDat.shape[0],sinoDat.shape[1],sinoDat.shape[2],C_expSetUp,outSinoDataFl,sinoGeo)
        algoIO.createMatr[float](&absorp[0,0,0],absorp.shape[0],absorp.shape[1],absorp.shape[2],absorpMatr)

        if selfAbsorp is None:
            self.thisptrFluoFl = new SARTAlgorithm[float,FluoReconstruction](outSinoDataFl,absorpMatr,sinoGeo)
        else:
            algoIO.createMatr[float](&selfAbsorp[0,0,0],selfAbsorp.shape[0],selfAbsorp.shape[1],selfAbsorp.shape[2],selfAbsorpMatr)
            self.thisptrFluoFl = new SARTAlgorithm[float,FluoReconstruction](outSinoDataFl,absorpMatr,selfAbsorpMatr,sinoGeo)
        self.FlDb = FLOAT_DAT

#
# Cython dtor
#

    def __dealloc__(self):
        if self.thisptrFluoDb is not NULL:
            del self.thisptrFluoDb
        else:
            del self.thisptrFluoFl


###########################################################
#
#       Transmission sinogram generation class
#
###########################################################

cdef class TxFwdProjection(FreeARTFwdProjection):
    """
    Class to do a FreeART sinogram generation in transmision mode. The angles at which the sinogram 
    must be computed is defined either by the angleList parameter either by the three parameters
    minAngle, maxAngle and AnglesNb

    :param phMatr: The phantom matrix. It has to be a numpy ndarray with data type float32 or float64
    :param angleList: The angle (degree) list for which the sinogram has to be generated. It has to be a numpy ndarray. 
            Data type has to be float32 or float64 - Optional
    :param minAngle: The smallest angle (degree) - Optional
    :param maxAngle: The largest angle (degree) - Optional
    :param anglesNb: The angle number - Optional
    """
#
#  Cython ctor
#

    def __cinit__(self,np.ndarray phMatr not None,
                  np.ndarray angleList = None,minAngle = None,maxAngle = None,anglesNb = None ):
        self._checkAngles(angleList,minAngle,maxAngle,anglesNb)
        self._checkProvidedMatr(phMatr)
        if angleList is not None:
            if angleList.dtype == np.float32:
                angleList = np.ascontiguousarray(angleList,dtype=np.double)

        if phMatr.dtype == np.float32:
            self.__sartTxFl(phMatr,angleList,minAngle,maxAngle,anglesNb)
        else:
            self.__sartTxDb(phMatr,angleList,minAngle,maxAngle,anglesNb)


    cdef __sartTxDb(self,np.ndarray[dtype=np.double_t,ndim=3] phMatr,
                    np.ndarray[dtype=np.double_t,ndim=1,mode="c"] angleList,
                    minAngle,maxAngle,anglesNb):
        cdef AlgorithmIO algoIO
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[double] matr
        cdef AnglesArray aa

        algoIO.createMatr[double](&phMatr[0,0,0],phMatr.shape[0],phMatr.shape[1],phMatr.shape[2],matr)

        if angleList is None:
            algoIO.prepareSinogramGeneration(minAngle,maxAngle,anglesNb,sinoGeo)
        else:
            algoIO.createAnglesArray[double](&angleList[0],angleList.shape[0],aa)
            algoIO.prepareSinogramGeneration(aa,sinoGeo)

        self.thisptrTxDb = new SARTAlgorithm[double,TxReconstruction](matr,sinoGeo)
        self.FlDb = DOUBLE_DAT

    cdef __sartTxFl(self,np.ndarray[dtype=np.float32_t,ndim=3] phMatr,
                    np.ndarray[dtype=np.double_t,ndim=1,mode="c"] angleList,
                    minAngle,maxAngle,anglesNb):
        cdef AlgorithmIO algoIO
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[float] matr
        cdef AnglesArray aa

        algoIO.createMatr[float](&phMatr[0,0,0],phMatr.shape[0],phMatr.shape[1],phMatr.shape[2],matr)

        if angleList is None:
            algoIO.prepareSinogramGeneration(minAngle,maxAngle,anglesNb,sinoGeo)
        else:
            algoIO.createAnglesArray[double](&angleList[0],angleList.shape[0],aa)
            algoIO.prepareSinogramGeneration(aa,sinoGeo)

        self.thisptrTxFl = new SARTAlgorithm[float,TxReconstruction](matr,sinoGeo)
        self.FlDb = FLOAT_DAT

#
# Cython dtor
#

    def __dealloc__(self):
        if self.thisptrTxDb is not NULL:
            del self.thisptrTxDb
        else:
            del self.thisptrTxFl


###########################################################
#
#       Fluorescence sinogram generation class
#
###########################################################

cdef class FluoFwdProjection(FreeARTFwdProjection):
    """
    Class to do a FreeART sinogram generation in fluorescence mode. The angles at which the sinogram 
    must be computed is defined either by the angleList parameter either by the three parameters
    minAngle, maxAngle and AnglesNb

    :param phMatr: The phantom matrix. It has to be a numpy ndarray with data type float32 or float64
    :param expSetUp:
            The experiment detector set up. This is a list with one element per detector.
            Each detector is represented by a tuple with two elements which are
                #. The detector center position for the FIRST angle defined in the sinogram. This is
                   a tuple with 3 elements which are the x, y and z coordinates. The coordinate system origin
                   is the sample center. The unit is defined by the sinogram lines.  
                   For instance, if the sinogram line is 256 points long for a sample motion of 10 mm, 
                   the unit is 10/256 mm. 

                #. The detector size. The detector is supposed to be a square. The unit is the same 
                   than previously described.
    :param absorpMatrix: The absorption matrix for the incoming beam for fluorescence mode
    :param selfAbsorpMatrix: The self absorption matrix for the outgoing beam for fluorescence mode 
    :param angleList: The angle (degree) list for which the sinogram has to be generated. It has to be a numpy ndarray. 
            Data type has to be float32 or float64 - Optional
    :param minAngle: The smallest angle (degree) - Optional
    :param maxAngle: The largest angle (degree) - Optional
    :param anglesNb: The angle number - Optional
    """
#
#  Cython ctor
#

    def __cinit__(self,np.ndarray phMatr not None,
                  expSetUp not None,
                  np.ndarray absorpMatr not None,
                  np.ndarray selfAbsorpMatrix not None,
                  np.ndarray angleList = None,
                  minAngle = None,
                  maxAngle = None,
                  anglesNb = None ):
        self._checkPyExpSetUp(expSetUp)
        self._checkAngles(angleList,minAngle,maxAngle,anglesNb)
        self._checkProvidedMatr(phMatr)

        if angleList is not None:
            if angleList.dtype == np.float32:
                angleList = np.ascontiguousarray(angleList,dtype=np.double)

        cdef vector[DetectorSetUp] C_expSetUp
        for det in expSetUp:
            detCenter = det[0]
            C_expSetUp.push_back(DetectorSetUp(Position_FC(detCenter[0],detCenter[1],detCenter[2]),det[1],0.0,0.0))

        if phMatr.dtype == np.float32:
            self.__sartFluoFl(phMatr, C_expSetUp, absorpMatr, selfAbsorpMatrix, angleList, minAngle, maxAngle, anglesNb)
        else:
            self.__sartFluoDb(phMatr, C_expSetUp, absorpMatr, selfAbsorpMatrix, angleList, minAngle, maxAngle, anglesNb)


    cdef __sartFluoDb(self,np.ndarray[dtype=np.double_t,ndim=3] iPhMatr,
                    vector[DetectorSetUp] C_expSetUp,
                    np.ndarray[dtype=np.double_t,ndim=3] iAbsorpMatr,
                    np.ndarray[dtype=np.double_t,ndim=3] iSelfAbsorpMatrix,
                    np.ndarray[dtype=np.double_t,ndim=1,mode="c"] angleList,
                    minAngle,maxAngle,anglesNb):
        cdef AlgorithmIO algoIO
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[double] phMatr
        cdef BinVec3D[double] absorpMatrix
        cdef BinVec3D[double] selfAbsorpMatrix
        cdef AnglesArray aa

        algoIO.createMatr[double](&iPhMatr[0,0,0], iPhMatr.shape[0], iPhMatr.shape[1],iPhMatr.shape[2], phMatr)
        algoIO.createMatr[double](&iAbsorpMatr[0,0,0], iAbsorpMatr.shape[0], iAbsorpMatr.shape[1], iAbsorpMatr.shape[2], absorpMatrix)
        algoIO.createMatr[double](&iSelfAbsorpMatrix[0,0,0], iSelfAbsorpMatrix.shape[0], iSelfAbsorpMatrix.shape[1], iSelfAbsorpMatrix.shape[2], selfAbsorpMatrix)

        if angleList is None:
            algoIO.prepareSinogramGeneration(C_expSetUp, minAngle, maxAngle, anglesNb, sinoGeo)
        else:
            algoIO.createAnglesArray[double](&angleList[0], angleList.shape[0], aa)
            algoIO.prepareSinogramGeneration(C_expSetUp, aa, sinoGeo)

        self.thisptrFluoDb = new SARTAlgorithm[double,FluoReconstruction](phMatr, absorpMatrix, selfAbsorpMatrix, sinoGeo)
        self.FlDb = DOUBLE_DAT


    cdef __sartFluoFl(self,np.ndarray[dtype=np.float32_t,ndim=3] iPhMatr,
                    vector[DetectorSetUp] C_expSetUp,
                    np.ndarray[dtype=np.float32_t,ndim=3] iAbsorpMatrix,
                    np.ndarray[dtype=np.float32_t,ndim=3] iSelfAbsorpMatrix,
                    np.ndarray[dtype=np.double_t,ndim=1,mode="c"] angleList,
                    minAngle,maxAngle,anglesNb):
        cdef AlgorithmIO algoIO
        cdef SinogramsGeometry sinoGeo
        cdef BinVec3D[float] phMatr
        cdef BinVec3D[float] absorpMatrix
        cdef BinVec3D[float] selfAbsorpMatrix
        cdef AnglesArray aa

        algoIO.createMatr[float](&iPhMatr[0,0,0], iPhMatr.shape[0], iPhMatr.shape[1], iPhMatr.shape[2], phMatr)

        if angleList is None:
            algoIO.prepareSinogramGeneration(C_expSetUp,minAngle,maxAngle,anglesNb,sinoGeo)
        else:
            algoIO.createAnglesArray[double](&angleList[0],angleList.shape[0],aa)
            algoIO.prepareSinogramGeneration(C_expSetUp,aa,sinoGeo)

        algoIO.createMatr[float](&iAbsorpMatrix[0,0,0], iAbsorpMatrix.shape[0], iAbsorpMatrix.shape[1], iAbsorpMatrix.shape[2], absorpMatrix)
        algoIO.createMatr[float](&iSelfAbsorpMatrix[0,0,0], iSelfAbsorpMatrix.shape[0], iSelfAbsorpMatrix.shape[1], iSelfAbsorpMatrix.shape[2], selfAbsorpMatrix)
        
        self.thisptrFluoFl = new SARTAlgorithm[float,FluoReconstruction](phMatr, absorpMatrix, selfAbsorpMatrix, sinoGeo)            
        self.FlDb = FLOAT_DAT

#
# Cython dtor
#

    def __dealloc__(self):
        if self.thisptrFluoDb is not NULL:
            del self.thisptrFluoDb
        else:
            del self.thisptrFluoFl
