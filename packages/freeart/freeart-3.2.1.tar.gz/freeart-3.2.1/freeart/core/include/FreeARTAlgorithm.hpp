//+==================================================================================================================
//
// FreeARTAlgorithm.tpp
//
//
// Copyright (C) :      2014,2015
//						European Synchrotron Radiation Facility
//                      BP 220, Grenoble 38043
//                      FRANCE
//
// This file is part of FreeART.
//
// FreeART is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
// License as published by the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// FreeART is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
// warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
// for more details.
//
// You should have received a copy of the GNU Lesser General Public License along with FreeART.
// If not, see <http://www.gnu.org/licenses/>.
//
//+==================================================================================================================

/*
 * File:   FreeARTAlgorithm.tpp
 * Author: taurel
 *
 * Created on 18 November 2014
 */

#ifndef FREEART_ALGORITHM_TPP
#define	FREEART_ALGORITHM_TPP

#include "macros.h"
#include "edfwriter.h"
#include <assert.h>
#include <limits>

#if defined (_MSC_VER)
    /* Microsoft Visual Studio */
    #if _MSC_VER >= 1600
        /* Visual Studio 2010 and higher */
        #define myisnan std::isnan
    #else
        #include <float.h>
        #define myisnan _isnan
    #endif
#else
    #define myisnan std::isnan
#endif


namespace FREEART_NAMESPACE
{

//-------------------------------------------------------------------------------------------------------------
//
//                      SARTAlgorithm class methods
//
//-------------------------------------------------------------------------------------------------------------

// extern static bool _print;

// new constructor for the fluorescence projector
template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(
    const BinVec3D<TYPE> &_phMatr,
    const BinVec3D<TYPE> &_absMatr,
    const BinVec3D<TYPE> &_selfAbsMatr,
    SinogramsGeometry &_sinosGeo ):
Algorithm<TYPE>(), makeSino(true), diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    setDefaultValue();
    this->phantom = _phMatr;
    this->phantomAbsorption = _absMatr;
    this->phantomSelfAbsorption = _selfAbsMatr;

    recons.setReconstructionParam(&rp);

//
// Init detector distance, length and angles
//

    detsDistanceLengthAngle(_sinosGeo);

//
// Init rotation angles
//

    size_t totRot = _sinosGeo.rotNb();
    angArray.reset(totRot);

    for (size_t loop = 0;loop < totRot;loop++)
    {
        Position_FC &pos = _sinosGeo.getbi(loop);
        positionToAngle(pos,angArray[loop]);
    }


    abs = true;
    selfAbs = true;

    init();
}


// Another sinogram generation ctor

// Reconstruction ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const Sinograms3D<TYPE> &sinosData,SinogramsGeometry &sinosGeo):
Algorithm<TYPE>(),makeSino(false),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    setDefaultValue();
    recons.setReconstructionParam(&rp);
    fromNewInterfaceToFormerWay(sinosData,sinosGeo);

    this->phantomAbsorption.reset(this->phantom.getLength(),this->phantom.getWidth(),this->phantom.getHeight());

    init();
}

// Reconstruction ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const Sinograms3D<TYPE> &sinosData,const BinVec3D<TYPE> &absorpMatr,SinogramsGeometry &sinosGeo):
Algorithm<TYPE>(),makeSino(false),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    size_t rayNb = sinosData[0].getRayNb();
    if (absorpMatr.getLength() != rayNb || absorpMatr.getWidth() != rayNb)
    {
        stringstream stream;
        stream << "Incoherent input parameters:\n";
        stream << "Provided sinograms width is " << rayNb << " while provided absorption matrix is (";
        stream << absorpMatr.getLength() << ", " << absorpMatr.getWidth() << ")";
        throw InitializationException(stream.str());
    }

    setDefaultValue();
    recons.setReconstructionParam(&rp);
    fromNewInterfaceToFormerWay(sinosData,sinosGeo);
    this->phantomAbsorption = absorpMatr;
    abs = true;

    init();
}

// Reconstruction ctor (for Diffract reconstruction)

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const Sinograms3D<TYPE> &sinosData,const BinVec3D<TYPE> &absorpMatr,
                                          const bool _selfAbs,SinogramsGeometry &sinosGeo):
Algorithm<TYPE>(),makeSino(false),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    size_t rayNb = sinosData[0].getRayNb();
    if (absorpMatr.getLength() != rayNb || absorpMatr.getWidth() != rayNb)
    {
        stringstream stream;
        stream << "Incoherent input parameters:\n";
        stream << "Provided sinograms width is " << rayNb << " while provided absorption matrix is (";
        stream << absorpMatr.getLength() << ", " << absorpMatr.getWidth() << ")";
        throw InitializationException(stream.str());
    }

    setDefaultValue();
    recons.setReconstructionParam(&rp);
    fromNewInterfaceToFormerWay(sinosData,sinosGeo);
    this->phantomAbsorption = absorpMatr;
    abs = true;
    selfAbs = _selfAbs;

    init();
}

// Reconstruction ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const Sinograms3D<TYPE> &sinosData,const BinVec3D<TYPE> &absorpMatr,
                                          const BinVec3D<TYPE> &selfAbsorpMatr,SinogramsGeometry &sinosGeo):
Algorithm<TYPE>(),makeSino(false),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    size_t rayNb = sinosData[0].getRayNb();
    if (absorpMatr.getLength() != rayNb || absorpMatr.getWidth() != rayNb)
    {
        stringstream stream;
        stream << "Incoherent input parameters:\n";
        stream << "Provided sinograms width is " << rayNb << " while provided absorption matrix is (";
        stream << absorpMatr.getLength() << ", " << absorpMatr.getWidth() << ")";
        throw InitializationException(stream.str());
    }

    if (absorpMatr.getLength() != rayNb || absorpMatr.getWidth() != rayNb)
    {
        stringstream stream;
        stream << "Incoherent input parameters:\n";
        stream << "Provided sinograms width is " << rayNb << " while provided self absorption matrix is (";
        stream << selfAbsorpMatr.getLength() << ", " << selfAbsorpMatr.getWidth() << ")";
        throw InitializationException(stream.str());
    }

    setDefaultValue();
    recons.setReconstructionParam(&rp);
    fromNewInterfaceToFormerWay(sinosData,sinosGeo);
    this->phantomAbsorption = absorpMatr;
    this->phantomSelfAbsorption = selfAbsorpMatr;

    abs = true;
    selfAbs = true;

    init();
}

// Sinogram generation ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const BinVec3D<TYPE> &_matr,SinogramsGeometry &_sinosGeo):
Algorithm<TYPE>(),makeSino(true),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    setDefaultValue();
    this->phantom = _matr;
    this->phantomAbsorption.reset(this->phantom.getLength(),this->phantom.getWidth(),this->phantom.getHeight());
    recons.setReconstructionParam(&rp);

//
// Init detector distance, length and angles
//

    detsDistanceLengthAngle(_sinosGeo);

//
// Init rotation angles
//

    size_t totRot = _sinosGeo.rotNb();
    angArray.reset(totRot);

    for (size_t loop = 0;loop < totRot;loop++)
    {
        Position_FC &pos = _sinosGeo.getbi(loop);
        positionToAngle(pos,angArray[loop]);
    }


    abs = true;

    init();
}

// Sinogram generation ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const BinVec3D<TYPE> &_matr,const bool _selfAbs,SinogramsGeometry &_sinosGeo):
Algorithm<TYPE>(),makeSino(true),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    setDefaultValue();
    this->phantom = _matr;
    this->phantomAbsorption.reset(this->phantom.getLength(),this->phantom.getWidth(),this->phantom.getHeight());
    recons.setReconstructionParam(&rp);
    if (_selfAbs == true)
        this->phantomSelfAbsorption = _matr;

//
// Init detector distance, length and angles
//

    detsDistanceLengthAngle(_sinosGeo);

//
// Init rotation angles
//



    size_t totRot = _sinosGeo.rotNb();
    angArray.reset(totRot);

    for (size_t loop = 0;loop < totRot;loop++)
    {
        Position_FC &pos = _sinosGeo.getbi(loop);
        positionToAngle(pos, angArray[loop]);
    }



    abs = true;
    selfAbs = _selfAbs;

    init();
}

// Another sinogram generation ctor

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::SARTAlgorithm(const BinVec3D<TYPE> &_matr,const BinVec3D<TYPE> &_selfMatr,SinogramsGeometry &_sinosGeo):
Algorithm<TYPE>(),makeSino(true),diffMatr(0,0,0), rndmAccessor(0), rp(ReconstructionParameters<TYPE>(recons.getReconstructionType()))
{
    setDefaultValue();
    this->phantom = _matr;
    this->phantomAbsorption.reset(this->phantom.getLength(),this->phantom.getWidth(),this->phantom.getHeight());
    this->phantomSelfAbsorption = _selfMatr;
    recons.setReconstructionParam(&rp);

//
// Init detector distance, length and angles
//

    detsDistanceLengthAngle(_sinosGeo);

//
// Init rotation angles
//


    size_t totRot = _sinosGeo.rotNb();
    angArray.reset(totRot);

    for (size_t loop = 0;loop < totRot;loop++)
    {
        Position_FC &pos = _sinosGeo.getbi(loop);
        positionToAngle(pos,angArray[loop]);
    }


    abs = true;
    selfAbs = true;

    init();
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::fromNewInterfaceToFormerWay(const Sinograms3D<TYPE> &sinosData,SinogramsGeometry &sinosGeo)
{
//
// Copy first sinogram
//

    this->sino = sinosData[0];

//
// Init rotation angle in the sinogram object.
//

    size_t totRot = sinosGeo.rotNb();
    for (size_t loop = 0;loop < totRot;loop++)
    {
        Position_FC &pos = sinosGeo.getbi(loop);
        positionToAngle(pos,this->sino.getRotation(0,loop).angle);
    }

//
// Init detector distance, length and angles
//

    detsDistanceLengthAngle(sinosGeo);
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::positionToAngle(const Position_FC &pos,double &ang)
{
    // we want the angle between the vector y_up and the vector (origin, position)
    ang = fmod(atan2(1.0, 0.0) - atan2(pos.y, pos.x), (2.0*M_PI) );
    return;
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::detsDistanceLengthAngle(SinogramsGeometry &sinosGeo)
{

//
// Give some place for the detectors distance, radius and angle (used in Fluo mode)
//

    size_t detNb = sinosGeo.detNb();
    DebugPrintf(("detNb = %zu\n",detNb));

    detsDistance.reset(detNb);
    detsLength.reset(detNb);
    detsAngle.reset(detNb);

//
// Compute detectors distance, angle and radius
//

    for (size_t loop = 0;loop < detNb;loop++)
    {
        DetectorGeometry &detGeo = sinosGeo.getDetectorsGeometry()[loop];

        Position_FC &detPos = detGeo.getCi(0);
        detsDistance[loop] = detPos.norm();
        DebugPrintf(("Detector distance = %f\n",detsDistance[loop]));

        Position_FC &detUBegin = detGeo.getDi(0);
        Position_FC &detUEnd = detGeo.getUi(0);
        Position_FC UVector(detUEnd.x - detUBegin.x,detUEnd.y - detUBegin.y,detUEnd.z - detUBegin.z);
        detsLength[loop] = UVector.norm();
        DebugPrintf(("Detector length = %f\n",detsLength[loop]));

        detsAngle[loop] = fmod((TYPE)(atan2(1.0, 0.0) - atan2(detPos.y, detPos.x)), (TYPE)(2.0*M_PI) );
        if (detPos.y < 0){
            detsAngle[loop] = -detsAngle[loop];
        }
        DebugPrintf(("Detector angle = %f\n",detsAngle[loop]));
    }

}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::setDefaultValue()
{
    abs = false;
    selfAbs = false;
    upperLimit = std::numeric_limits<TYPE>::infinity();
    lowerLimit = 0.0;

    maxPointNum = 0;
}

template <typename TYPE,template <typename> class RECONS>
SARTAlgorithm<TYPE,RECONS>::~SARTAlgorithm()
{

}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::setUpperLimit(TYPE _val)
{
    if (_val <= lowerLimit)
    {
        stringstream stream;
        stream << "Incoherent upper limit: It is lower than the already defined lower limit (" << lowerLimit << ")";
        throw InitializationException(stream.str());
    }
    upperLimit = _val;
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::setLowerLimit(TYPE _val)
{
    if (_val >= upperLimit)
    {
        stringstream stream;
        stream << "Incoherent lower limit: It is greater than the already defined upper limit (" << upperLimit << ")";
        throw InitializationException(stream.str());
    }
    lowerLimit = _val;
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::printInfo() const
{
    InfoPrintf(("Phantom created: width length %3u, width %3u, height %3u\n",
                _FT_UI32(this->phantom.getLength()), _FT_UI32(this->phantom.getWidth()), _FT_UI32(this->phantom.getHeight())));
    InfoPrintf(("               : voxLength %f, voxWidth %f \n",
                VOXEL_LENGTH, VOXEL_WIDTH ));
    InfoPrintf(("               : Physical Length %f, Physical Width %f\n",
                VOXEL_LENGTH*this->phantom.getLength(), VOXEL_WIDTH*this->phantom.getWidth()));
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::checkAndPrepareIteration(ReconstructionParameters<TYPE>& rp,
    const GenericSinogram3D<TYPE> & sino, const uint32_t &numSelfAbsRays)
{
    if (!this->phantom.haveEqualDimensions(diffMatr))
    {
        diffMatr.reset(this->phantom.getLength(), this->phantom.getWidth(),this->phantom.getHeight());
    }

    if (rndmAccessor.size() != sino.getRotNb())
    {
        rndmAccessor.reset(sino.getRotNb());
    }

/* In case of self-absorption we need a buffer more to hold the interpolated coefficients */

    if (numSelfAbsRays && (selfAbs || abs))
    {
        rp.resetSelfAbs(maxPointNum, numSelfAbsRays,this->phantom.getHeight());
    }
}

template <typename TYPE,template <typename> class RECONS>
uint32_t SARTAlgorithm<TYPE,RECONS>::computeMaxRayLength(uint32_t length,uint32_t width) const
{
/* One extra point for the borders */
    return rp.getOverSampling() * (1 + _FT_UI32( max(length, width) ) );
}

template<typename TYPE,template <typename> class RECONS>
INLINE void
SARTAlgorithm<TYPE,RECONS>::checkMask(const BinVec3D_B &mask, const BinVec3D<TYPE> &ph) const
{
  if ( mask.getLength() != ph.getLength() || mask.getWidth() != ph.getWidth() || mask.getHeight() != ph.getHeight())
  {
    stringstream stream;
    stream << "Got wrong mask size:\n  "
           << "Mask: (" << mask.getLength()
             << ", " << mask.getWidth() << ", " << mask.getHeight() << "), "
           << "Phantom dimensions: (" << ph.getLength()
             << ", " << ph.getWidth() << ", " << ph.getHeight() << ")\n";
    throw InitializationException(stream.str());
  }
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::init()
{
    //
    // create the data storing the reconstruction and construction parameters
    //
    rp.setPhantomSemiX( GET_C_SEMI(Algorithm<TYPE>::phantom.getLength()) );
    rp.setPhantomSemiY( GET_C_SEMI(Algorithm<TYPE>::phantom.getWidth()) );

    DebugPrintf(("abs = %d, selfAbs = %d\n",abs,selfAbs));
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::initReconstr()
{
    DebugPrintf(("Entering SARTAlgorithm::initReconstr() method\n"));

    if (makeSino == true)
    {
        stringstream stream;
        stream << "Wrong init() method. It is not coherent with the SARTAlgorithm contructor used.\n";
        stream << "Use init(minAmgle,maxAngle,angleNb) or init(AnglesArray)";
        throw InitializationException(stream.str());
    }


//
// Some checks
//

    if (this->sino.size() == 0)
    {
        string str("Sinogram size is 0! Do you specify one?");
        throw NotInitializedObjException(str);
    }

//
// For fluo and diffract reconstructiom, we need the phantom absorption matrix (from a previous Tx reconstruction)
//

    bitset<MAX_TYPES> reconsType = recons.getReconstructionType();
    if (reconsType.test(FLUORESCENCE_TYPE) == true ||
        reconsType.test(DIFFRACTION_TYPE) == true)
    {
        if (abs == false)
        {
            stringstream stream;
            stream << "You required a Fluorescence/Diffraction reconstruction but the phantom absorption volume is not provided\n";
            stream << "In a first step, use a Tx reconstruction to generate it";
            throw InitializationException(stream.str());
        }
    }

//
// For diffraction reconstruction, we need at least 2 detectors
//

    if (reconsType.test(DIFFRACTION_TYPE) == true)
    {
        if (detsLength.size() < 2)
        {
            stringstream stream;
            stream << "You required a Diffraction reconstruction but only one detector is defined.\n";
            stream << "For FreeART reconstruction, two virtual detectors are required even if physically you have only one";
            throw InitializationException(stream.str());
        }

        if (selfAbs == true)
        {
            this->phantomSelfAbsorption = this->phantomAbsorption;
        }
    }

//
// Set detector geometry (in case of Fluo or Diffract reconstruction)
//

    if (reconsType.test(FLUORESCENCE_TYPE) == true ||
        reconsType.test(DIFFRACTION_TYPE))
    {
        for (size_t loop = 0;loop < detsLength.size();loop++)
        {
            recons.setDetectorGeometry(detsLength[0],detsDistance[0],detsAngle[0]);
        }
    }

//
// Retrieve number of self abs ray
//

    uint32_t numSelfAbsRay = recons.getNumSelfAbsRay();

//
// Create the geometry table object
//

    GeometryFactory geomFactory;
    if (this->gt != NULL)
        delete this->gt;

    this->gt = geomFactory.getGeometryFromSinogram(this->sino,reconsType,rp,selfAbs);


//
// Set reconstruction object buffer size
//

    const Dimensions_UI32 &matrDims = geomFactory.getMatrDims();
    if (reconsType.test(TRANSMISSION_TYPE) == false)
    {
        maxPointNum = this->computeMaxRayLength(matrDims.x,matrDims.y);
        recons.setVoxBuffSize(maxPointNum);
    }

///
/// Set the radius of the active region (region of acquisition)
///

    rp.setRadiusActiveRegion( min(TYPE(matrDims.x * VOXEL_LENGTH),
                                  TYPE(matrDims.y * VOXEL_WIDTH)/2) );


//
// Init the phantom, phantom absorption and self phantom absorption matrices
//
    // if need to reset the phantom (size changed ). Otherwise continue iteration with this phantom
    if( this->phantom.getLength() != matrDims.x || 
        this->phantom.getWidth() != matrDims.y ||
        this->phantom.getHeight() != matrDims.z )
    {
        this->phantom.reset(matrDims.x,matrDims.y,matrDims.z);
    }

    rp.setPhantomSemiX( GET_C_SEMI(Algorithm<TYPE>::phantom.getLength()) );
    rp.setPhantomSemiY( GET_C_SEMI(Algorithm<TYPE>::phantom.getWidth()) );


//
// If user gives absorption volume (self or not), check its sizes
//

    if (selfAbs == true)
    {
        if (this->phantomSelfAbsorption.getHeight() != this->phantom.getHeight() ||
            this->phantomSelfAbsorption.getWidth() != this->phantom.getWidth() ||
            this->phantomSelfAbsorption.getLength() != this->phantom.getLength())
        {
            stringstream ss;
            ss << "Provided self absorption volume does not have the correct dimension\n";
            ss << "Phantom dims: Length = " << this->phantom.getLength() << ", Width = " << this->phantom.getWidth() << ", Height = " << this->phantom.getHeight() << "\n";
            ss << "Absorption volume; Length = " << this->phantomSelfAbsorption.getLength() << ", Width = " << this->phantomSelfAbsorption.getWidth() << ", Height = " << this->phantomSelfAbsorption.getHeight() << "\n";
            throw InitializationException(ss.str());
        }
    }

    if (abs == true)
    {
        if (this->phantomAbsorption.getHeight() != this->phantom.getHeight() ||
            this->phantomAbsorption.getWidth() != this->phantom.getWidth() ||
            this->phantomAbsorption.getLength() != this->phantom.getLength())
        {
            stringstream ss;
            ss << "Provided absorption volume does not have the correct dimension\n";
            ss << "Phantom dims: Length = " << this->phantom.getLength() << ", Width = " << this->phantom.getWidth() << ", Height = " << this->phantom.getHeight() << "\n";
            ss << "Absorption volume; Length = " << this->phantomAbsorption.getLength() << ", Width = " << this->phantomAbsorption.getWidth() << ", Height = " << this->phantomAbsorption.getHeight() << "\n";
            throw InitializationException(ss.str());
        }
    }

//
// Allocate memory for the rays
//
    this->gt->initRaysAllocation(matrDims);

//
// Check parameters and fix them if needed
//

    checkAndPrepareIteration(rp, this->sino, numSelfAbsRay);

//
// Some print for debug purpose
//

    printInfo();
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::initMakeSino()
{
    DebugPrintf(("Entering SARTAlgorithm::initMakeSino() method\n"));

    if (makeSino == false)
    {
        stringstream stream;
        stream << "This init method is for Sinogram creation purpose.\n";
        stream << "Please use SARTAlgorithm::init() method";
        throw InitializationException(stream.str());
    }

    rp.setRadiusActiveRegion( min(TYPE(this->phantom.getLength() * VOXEL_LENGTH),
                                   TYPE(this->phantom.getWidth() * VOXEL_WIDTH)/2) );
    bitset<MAX_TYPES> reconsType = recons.getReconstructionType();

    if (reconsType.test(DIFFRACTION_TYPE) == true &&
        selfAbs == true &&
        detsLength.size() < 2)
    {
        stringstream stream;
        stream << "You required a Diffraction sinogram but only one detector is defined.\n";
        stream << "For FreeART sinogram generation, two virtual detectors are required even if physically you have only one";
        throw InitializationException(stream.str());
    }

//
// Get geometry from the provided phantom
//
    GeometryFactory gf;
    this->gt = gf.getGeometryFromPhantom(this->phantom, rp.getRadiusActiveRegion(), reconsType, rp, selfAbs, angArray);

//
// Set detector geometry (in case of Fluo or Diffract reconstruction)
//

    if (reconsType.test(FLUORESCENCE_TYPE) == true ||
        reconsType.test(DIFFRACTION_TYPE))
    {
        for (size_t loop = 0;loop < detsLength.size();loop++)
            recons.setDetectorGeometry(detsLength[0],detsDistance[0],detsAngle[0]);
    }

//
// Set reconstruction object buffer size
//

    const Dimensions_UI32 &phDims = this->gt->getPhantomDims();

    if (reconsType.test(TRANSMISSION_TYPE) == false)
    {
        maxPointNum = this->computeMaxRayLength(phDims.x,phDims.y);
        recons.setVoxBuffSize(maxPointNum);
    }

//
// Allocating the object that holds the support data for the iterations
//

    uint32_t numSelfAbsRays = recons.getNumSelfAbsRay();
    if (numSelfAbsRays && selfAbs)
    {
        const uint32_t maxPointNum = this->computeMaxRayLength(phDims.x,phDims.y);
        rp.resetSelfAbs(maxPointNum, numSelfAbsRays,this->phantom.getHeight());
    }

//
// Set detector geometry (in case of Fluo or diffract reconstruction)
//

    if (reconsType.test(FLUORESCENCE_TYPE) == true)
    {
        for (size_t loop = 0;loop < detsLength.size();loop++)
            recons.setDetectorGeometry(detsLength[0],detsDistance[0],detsAngle[0]);
    }

//
// Allocate the rays for the sinogram generation
//
    this->gt->initRaysAllocation(this->phantom.getMatrDims());

//
// Some print for debug purpose
//

    printInfo();
}


template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::initRotation(uint32_t _n)
{
    rp.setRealProjSel( rndmAccessor[_n]);

    const size_t numSlice = 0;
    this->gt->computeGeometryForSliceRotation(numSlice, rp.getRealProjSel(), this->sino, rp.getRayPointCalculationMethod());

    TYPE angle = this->sino.getRotation(numSlice,rp.getRealProjSel()).angle;

    TYPE detAngle = angle;
    bitset<MAX_TYPES> reconsType = recons.getReconstructionType();
    if (reconsType.test(FLUORESCENCE_TYPE) == true || reconsType.test(COMPTON_TYPE) == true){
        detAngle += detsAngle[0];
    }    
    recons.initRotation(*this->gt, selfAbs, this->phantomAbsorption, this->phantomSelfAbsorption, detAngle);
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::doWork(const uint32_t iterationNb)
{
    initReconstr();
    DebugPrintf(("Entering SARTAlgorithm::doWork() method\n"));
    
    for (uint32_t iter = 0;iter < iterationNb;iter++)
    {
        InfoPrintf(("One more iteration\n"));

        for (size_t numRot = 0;numRot < this->sino.getRotNb();numRot++)
        {
            diffMatr.clean();
            this->initRotation(numRot);

            InfoPrintf(("Point number for geometry [%zu] = %zu\n",rp.getRealProjSel(),this->gt->getTotSampledPoints()));

            const size_t numSlice = 0;
            const Rotation<TYPE> & rotation = this->gt->getRotation(0);
            const TYPE rotationFactor = recons.getRotationFactor(rotation);

            for (uint32_t numRay = 0;numRay < this->gt->getTotIncomingRaysPerRot();numRay++)
            {
                const Ray<TYPE> & ray = rotation.getRay(numRay);

                TYPE denom = 0.0;
                TYPE fp = 0.0;
                recons.fwdProjection(this->phantom, ray, this->gt, selfAbs, rp.getSelfAbsBuff(), denom, fp);

                denom /= rp.getOverSampling();
                fp /= rp.getOverSampling();

                denom *= rotationFactor;
                fp *= rotationFactor;

                // we also have to handle the dimensions
                // absorption in the voxel is :
                // - the absorption recored for the voxel (in g per cm2 )
                // - multiply by the voxel surface
                const TYPE voxelLength = rp.getVoxelSize();
                
                TYPE absorptionInVoxel;
                if(recons.getReconstructionType().test(TRANSMISSION_TYPE) == true){
                    absorptionInVoxel = TYPE(this->sino.getPoint(numSlice, rp.getRealProjSel(), numRay))/voxelLength;
                }else{
                    absorptionInVoxel = TYPE(this->sino.getPoint(numSlice, rp.getRealProjSel(), numRay))/(ray.I0*voxelLength);
                }

                const TYPE correctionFactor = rp.getDampingFactor() *((absorptionInVoxel - fp)/ denom);

                if (correctionFactor == numeric_limits<TYPE>::infinity() || myisnan((double)correctionFactor) ) {
                    // In case we have an infinit voxel (bad acquisition)
                    // continue (would be probably to violent to raise an error ? )
                    continue;
                }else{
                    bckProj.execute(diffMatr, ray, correctionFactor);
                }
            }

//
// Warning: In FreeART V1, for Tx, the non negativity (second parameter) is forced to true !!!!!
//  
            bitset<MAX_TYPES> reconsType = recons.getReconstructionType();
            if (reconsType.test(TRANSMISSION_TYPE) == true)
                this->phantom.setCorrections(diffMatr,upperLimit,(TYPE)0.0);
            else
                this->phantom.setCorrections(diffMatr,upperLimit,lowerLimit);
            recons.cleanup(this->gt,selfAbs);

#ifdef EXPORT_DIFF_MATR
            stringstream ssDiffr;
            string outputDir = "/tmp/";
            ssDiffr << outputDir << "diffMatr_it_" << iter << "_rot_" << rp.getRealProjSel() << endl;
            exportMatrix( diffMatr, ssDiffr.str());
            stringstream ssPhantom;
            ssPhantom <<  outputDir << "phantom_it_" << iter << "_rot_" << rp.getRealProjSel() << endl;
            exportMatrix( diffMatr, ssPhantom.str());
#endif
        }
    }
}

template <typename TYPE,template <typename> class RECONS>
void SARTAlgorithm<TYPE,RECONS>::makeSinogram(const BinVec3D_B &mask)
{
    
    initMakeSino();

    bool sinoReset = false;
    const bool completeSinogram = !mask.size();

    bitset<MAX_TYPES> reconsType = recons.getReconstructionType();
    if (reconsType.test(TRANSMISSION_TYPE) == false)
    {
        if (!completeSinogram)
            checkMask(mask, this->phantom);
    }
    else
        CHECK_THROW(completeSinogram,
            WrongArgException("The sinogram of just a portion is not "
                                "available for the transmission setup"));

    const size_t sliceNum = 0;
    AnglesArray rotAnglesArray = this->gt->getRotAnglesArray();
    // this->gt->changeToDegree();
    const size_t & totProj = rotAnglesArray.size();

    for(size_t numRot = 0; numRot < totProj; numRot++)
    {
        double detAngle = 0.0;
        if (reconsType.test(FLUORESCENCE_TYPE) == true || reconsType.test(COMPTON_TYPE) == true){
            detAngle = rotAnglesArray[numRot] + detsAngle[0];
            this->gt->setSelfAbsMatriceForFluo(this->phantomSelfAbsorption);
        }

        recons.initRotationMakeSino(*this->gt,numRot,selfAbs, this->phantomAbsorption, this->phantomSelfAbsorption, detAngle);

        if (sinoReset == false)
        {

/* Initialize the new sinogram with the right dimensions */

            this->sino.reset(sliceNum+1,totProj,this->gt->getTotIncomingRaysPerRot());
            sinoReset = true;
        }

        const Rotation<TYPE> & rotation = this->gt->getRotation(0);
        GenericSinogramProj<TYPE> & sinoRotation = this->sino.getRotation(sliceNum,numRot);
        sinoRotation.angle = rotation.angle;
        const TYPE rotationFactor = recons.getRotationFactor(rotation);

        for(uint32_t numRay = 0; numRay < this->gt->getTotIncomingRaysPerRot(); numRay++)
        {
            TYPE signal = 0;
            const Ray<TYPE> & ray = rotation.getRay(numRay);

            recons.raySum(this->phantom,ray,this->gt, selfAbs, rp.getSelfAbsBuff(), mask,signal);
            // This is needed here because we couldn t set it before. 
            const TYPE voxelLength = rp.getVoxelSize();
            signal *= voxelLength; 

/* Apply user limit */

#ifdef _MSC_VER
            int _i_lowerInf = _finite(lowerLimit);
            int _i_upperInf = _finite(upperLimit);

            bool lowerInf = false;
            bool upperInf = false;

            if (_i_lowerInf == 0)
                lowerInf = true;

            if (_i_upperInf == 0)
                upperInf = true;
#else
            bool lowerInf = std::isinf(lowerLimit);
            bool upperInf = std::isinf(upperLimit);
#endif

            if (upperInf == false)
            {
                if (signal > upperLimit)
                signal = upperLimit;
            }
            if (lowerInf == false)
            {
                if (signal < lowerLimit)
                    signal = lowerLimit;
            }
            if(reconsType.test(TRANSMISSION_TYPE) == true){
                signal = signal * rotationFactor / rp.getOverSampling();
                signal = exp(-signal)* rp.getI0();  
                sinoRotation.getPoint(numRay) = signal;
            }else{
                sinoRotation.getPoint(numRay) = signal * rotationFactor / rp.getOverSampling();
            }
        }
        recons.cleanup(this->gt,selfAbs);
    }
}

} // End of FreeART namespace

#endif	/* FREEART_ALGORITHM_TPP */

