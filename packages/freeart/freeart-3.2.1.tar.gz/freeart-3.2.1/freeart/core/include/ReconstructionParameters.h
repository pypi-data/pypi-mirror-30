// //+==================================================================================================================
// //
// // RayHelpers.h
// //
// //
// // Copyright (C) :      2014,2015, 2016
// //                       European Synchrotron Radiation Facility
// //                      BP 220, Grenoble 38043
// //                      FRANCE
// //
// // This file is part of FreeART.
// //
// // FreeART is free software: you can redistribute it and/or modify it under the terms of the GNU Lesser General Public
// // License as published by the Free Software Foundation, either version 3 of the License, or
// // (at your option) any later version.
// //
// // FreeART is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
// // warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
// // for more details.
// //
// // You should have received a copy of the GNU Lesser General Public License along with FreeART.
// // If not, see <http://www.gnu.org/licenses/>.
// //
// //+==================================================================================================================

/*
 * File:   ReconstructionParameters.h
 * Author: payno
 *
 * Created on March, 2016
 *
 * This class will group all information about the projection or reconstruction
 * in order to summuraize information
 * Author: payno
 */

#include "BinaryVectors.h"
#include "macros.h"
#include "units.h"
#include <bitset>

#ifndef RECONSTRUCTION_PARAMETERS
#define RECONSTRUCTION_PARAMETERS


namespace FREEART_NAMESPACE
{

using namespace UNITS;

/// Beam Calculation Method
/// It defined the way the value of sample point of the beam are calculated.
/// This is apply for the incoming ray AND the outgoing ray (this last case if you are in fluorescence of course)
enum RayPointCalculationMethod
{
    /// we will pick the value of the sample point from the voxel containig the point AND
    /// the neighbooring voxels
    withInterpolation,  
    /// we will pick the value of the sample point ONLY from the voxel containig the point
    withoutInterpolation
};

/// Outgoing beam calculation method
/// This define the way the OUTGOING ray values are computed
/// This apply only for the fluorescence mode
enum OutgoingRayAlgorithm
{
    /// in this case we are making the evaluation of the outgoing ray the faster as possible.
    /// For each rotation we are creating a matrice containing "more or less" the mean attenuation value of the sampled point inside this specific voxels.
    rawApproximation,
    /// in this version we are creating the real outgoing ray for each sample point on the incoming ray
    /// and computing the 'real' outgoing absorption of the ray by sampling voxels           
    createOneRayPerSamplePoint,
    /// This is the raw approximation case but by subdividing the voxels for the outgoing rays
    /// we are reducing the noise of the "raw" approximation.
    matriceSubdivision
};


/// This is where are stored the number of rays per rotation 
struct TotRaysPerRot
{
    uint32_t incoming;  //< the number of rays per rotation for the incoming rays
    uint32_t outgoing;  //< the number of rays per rotation for the outgoing rays

    TotRaysPerRot(uint32_t _incoming, uint32_t _outgoing){
        incoming = _incoming;
        outgoing = _outgoing;
    }
};

/// This is the structure storing the offsets of the rays
template <typename TYPE>
struct RayOffset
{
    TYPE incoming;      //< offset between incoming rays
    TYPE outgoing;      //< offset between outgoing rays

    RayOffset(TYPE _incoming, TYPE _outgoing){
        incoming = _incoming;
        outgoing = _outgoing;
    }
};

/// This is the structure storing the width of rays
/// WARNING the ray widths must always be 1 for now
/// If change then should be a template to ;atch with RayOffset and so on
struct RayWidth
{
    /// if one day you want to change that you must take it into account
    /// that the value we are integrating is not 1 in width and transmit 
    /// modification to the functions computing attenuation such as 
    /// updateIncomingLossFraction or getOutgoingLossFraction
    static const uint32_t incoming = RAY_WIDTH;
    static const uint32_t outgoing = RAY_WIDTH;
};

template <typename TYPE>
struct ReconstructionParameters
{
private:   
    TYPE voxelSizeInExpe;               //< voxel width and height (Voxels are still square) in "real" world

    bitset<MAX_TYPES> reconsType;      //< The type of reconsturction we want to do

    TYPE       phSemiX;                //< phantom x half size 
    TYPE       phSemiY;                //< phantom y half size
    
    bool       solidAngleOn;           //< do we want to activate the solid angle or set it to 1 
                                       /// It can be usefull to have it set at 1 for debugging purpose

    RayPointCalculationMethod beamCalculationMethod;                    // < the way to compute beams values
    OutgoingRayAlgorithm outgoingrayPointCalculationMethod;    //< the way to compute "outgoing beams" values

    size_t           realProjSel;            //< The projection selected
    TYPE             damping;                //< damping factor for the ART
    
    BinVec3D<TYPE>   selfAbsBuff;            //< outgoing beam absorption
    uint32_t         overSampling;           //< The number of point to sample per mm visited for rays        

    /// The factor by which we will subdivide each cell of the selfAbsMat 
    /// Warning : this is used only in the case the outgoingrayPointCalculationMethod is set to matriceSubdivision
    /// Warning : in fact the cell will be devide according to both axis. So the cell will be devided by subdivisionSelfAbsMat*subdivisionSelfAbsMat
    uint32_t         subdivisionSelfAbsMat;  

    TotRaysPerRot totRaysPerRot;        //< The number of rays for per rotation
    RayOffset<TYPE> rayOffset;          //< The offset between rays
    RayWidth rayWidth;                  //< The width of rays. 
                                        //< WARNING : for now should always be one because this isn t take into account by the attenation calculation. 

    TYPE radiusActiveRegion;    //< The radius of the disc we will ficus the projection on
    TYPE _squareRadiusActiveRegion;     //< The square radiusof the disc we will ficus the projection on
                                        //< Note : we are registring it in cache because it is highly used

    TYPE I0;                    //< The intensity of the source

    /// Function used to update the totRaysPerRot for the outgoing rays
    /// This is used because it depends on the method used to compute the attenation of the
    /// outgoing rays
    void updateTotOutgoingRaysPerRot(){
        if(outgoingrayPointCalculationMethod == matriceSubdivision){
            totRaysPerRot.outgoing = ceil(radiusActiveRegion*2.0/rayWidth.outgoing) * subdivisionSelfAbsMat ; 
        }else{
            totRaysPerRot.outgoing = totRaysPerRot.incoming; 
        }
    }

    /// Function used to update the offset for the outgoing rays
    /// this is also needed because it depends on the outgoing rays attenuation calculation method
    void updateOutgoingRayOffset(){
        if(outgoingrayPointCalculationMethod == matriceSubdivision){
            rayOffset.outgoing = rayOffset.incoming / subdivisionSelfAbsMat ; 
        }else{
            rayOffset.outgoing = rayOffset.incoming; 
        }
    }

public:
    /// Constructor
    /// @param _reconsType : the type of reconsturction we want to apply
    /// Note : by default voxel size is set to one millimeter
    ReconstructionParameters(bitset<MAX_TYPES> _reconsType): 
        voxelSizeInExpe(1.0*mm),
        reconsType(_reconsType), phSemiX(0), phSemiY(0), solidAngleOn(true), 
        beamCalculationMethod(static_cast<RayPointCalculationMethod>(DEFAULT_BEAM_CALCULATION_METHOD)), 
        outgoingrayPointCalculationMethod(static_cast<OutgoingRayAlgorithm> (DEFAULT_OUTGOING_BEAM_CALCULATION_METHOD)), 
        realProjSel(0), damping((TYPE)DAMPING_FACT), overSampling(OVERSAMPLING), subdivisionSelfAbsMat(1.0),
        totRaysPerRot(0, 0), rayOffset((TYPE)RAY_WIDTH, (TYPE)RAY_WIDTH), 
        radiusActiveRegion(0.0), _squareRadiusActiveRegion(0.0),
        I0(1.0) { }

    /// Destructor
    ~ReconstructionParameters() {};

    /// Voxel dimension getter
    TYPE getVoxelSize() const { return voxelSizeInExpe; }
    /// Voxel dimension setter
    /// Warning : the setting of this value must be normalized by using the values defined in the units.h file
    void setVoxelSize(TYPE _dim) { voxelSizeInExpe = _dim; }

    /// Reconstruction type getter
    bitset<MAX_TYPES> getReconstructionType() const { return reconsType;}


    /// BeamCalculaltion method.
    /// This method : with or without interpolation will be used for the incoming and
    /// The outgoing Rays
    RayPointCalculationMethod getRayPointCalculationMethod() const { return beamCalculationMethod;};
    void setRayPointCalculationMethod(RayPointCalculationMethod _val) { beamCalculationMethod = _val;}
    
    // One ray per sample pt getter & setter
    OutgoingRayAlgorithm getOutgoingRayAlgorithm() const { return outgoingrayPointCalculationMethod;}
    void setOutgoingRayAlgorithm(OutgoingRayAlgorithm _val) { 
        outgoingrayPointCalculationMethod = _val;
        updateTotOutgoingRaysPerRot();
        updateOutgoingRayOffset();
    }
    
    // subdivisionSelfAbsMat setter & getter
    uint32_t getSubdivisionSelfAbsMat() const { return subdivisionSelfAbsMat;}
    void setSubdivisionSelfAbsMat(uint32_t _val) { 
        subdivisionSelfAbsMat = _val;
        updateTotOutgoingRaysPerRot();
        updateOutgoingRayOffset();
    } 

    // Oversampling option
    uint32_t getOverSampling() const { return overSampling;}
    void setOversampling(TYPE _val){overSampling = _val;}
    /// return the length of each steps for ray absorption computation
    TYPE getIncrementationLength() const { return 1.0/overSampling;}

    // Damping factor setter & getter
    void setDampingFactor(TYPE _damping) { damping = _damping;}
    TYPE getDampingFactor() const {return damping;}

    // phamtom dimension getter & setter
    TYPE getPhantomSemiX() const { return phSemiX;}
    void setPhantomSemiX(TYPE _val) { phSemiX = _val;}

    TYPE getSemiXOutgoing() const {
        if(outgoingrayPointCalculationMethod == matriceSubdivision){
            return GET_C_SEMI((this->getPhantomSemiX()*2+1)*this->getSubdivisionSelfAbsMat());
        }else{
            return getPhantomSemiX();
        }
    } 
    TYPE getSemiYOutgoing() const {
        if(outgoingrayPointCalculationMethod == matriceSubdivision){
            return GET_C_SEMI((this->getPhantomSemiY()*2+1)*this->getSubdivisionSelfAbsMat());
        }else{
            return getPhantomSemiY();
        }
    }

    // phamtom dimension getter & setter
    TYPE getPhantomSemiY() const { return phSemiY;}
    void setPhantomSemiY(TYPE _val) {phSemiY = _val;}

    // Projection selection getter & setter
    size_t getRealProjSel() const { return realProjSel;}
    void setRealProjSel(size_t _val) { realProjSel = _val;}

    // SelfAbsBuffer getter & setter
    const BinVec3D<TYPE>& getSelfAbsBuff() const {return selfAbsBuff;}
    BinVec3D<TYPE>& getSelfAbsBuff() {return selfAbsBuff;}
    void setSelfAbsBuff(BinVec3D<TYPE> _val) { selfAbsBuff = _val;}

    void resetSelfAbs(uint32_t maxPointNum, const uint32_t numSelfAbsRays, const size_t height) { 
        selfAbsBuff.reset(maxPointNum, numSelfAbsRays, height); 
    };

    // TotRaysPerRot getter and setter
    const TotRaysPerRot& getTotRaysPerRot() const {
        return totRaysPerRot;}

    void setTotIncomingRaysPerRot(uint32_t _val ){
        totRaysPerRot.incoming = _val;
        updateTotOutgoingRaysPerRot();
    }

    // Ray Offset getter
    const RayOffset<TYPE>& getRayOffset() const { return rayOffset;}
    
    // Ray width getter
    const RayWidth& getRayWidth() const { return rayWidth;}

    // solidAngleOn getter and setter
    void turnOffSolidAngle(bool off) { solidAngleOn = !off;}
    bool isSolidAngleOn() const { return solidAngleOn;}

    // radiusActiveRegion getter and setter
    void setRadiusActiveRegion(TYPE rad) { 
        radiusActiveRegion = rad;
        _squareRadiusActiveRegion = radiusActiveRegion*radiusActiveRegion;
        this->setTotIncomingRaysPerRot( ceil(radiusActiveRegion*2.0/rayWidth.incoming)); 
    }
    TYPE getRadiusActiveRegion() const { return radiusActiveRegion;}
    TYPE getSquareRadiusActiveRegion() const { return _squareRadiusActiveRegion;}

    TYPE getSquareRadiusActiveRegionForOutgoing() const {
        TYPE val = getRadiusActiveRegionForOutgoing();
        return val*val;
    }

    TYPE getRadiusActiveRegionForOutgoing() const {
        if(outgoingrayPointCalculationMethod == matriceSubdivision){
            return radiusActiveRegion * subdivisionSelfAbsMat;
        }else{
            return radiusActiveRegion; 
        }
    }

    // I0 getter and setter
    TYPE getI0() const { return I0;}
    void setI0(TYPE _I0) { I0 = _I0; }

    void print() const {
        cout << "phSemiX = " << phSemiX << endl;
        cout << "phSemiY = " << phSemiY << endl;
        cout << "outgoingrayPointCalculationMethod = " << outgoingrayPointCalculationMethod << endl;
        cout << "rayPointCalculationMethod = " << beamCalculationMethod << endl;
        cout << "realProjSel = " << realProjSel << endl;
        cout << "damping = " << damping << endl;
        cout << "overSampling = " << overSampling << endl;
        cout << "getSquareRadiusActiveRegionForOutgoing = " << this->getSquareRadiusActiveRegionForOutgoing() << endl;
        cout << "getPhantomSemix" << this->getPhantomSemiY() << endl;
    }
};

} // end namepsace
#endif