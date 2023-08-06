//+==================================================================================================================
//
// FreeARTAlgorithm.h
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
 * File:   FreeARTAlgorithm.h
 * Author: taurel
 *
 * Created on 18 November 2014
 */

#ifndef FREEART_ALGORITHM_H
#define	FREEART_ALGORITHM_H

#include <Projections.h>
#include <AlgoIO.h>

namespace FREEART_NAMESPACE
{

/*
 * Base class for FreeART algorithm
 */
template <typename TYPE>
class Algorithm
{
public:
    Algorithm():gt(NULL) {}
    virtual ~Algorithm() {delete gt; gt=NULL;}

    virtual void init() = 0;
    virtual void doWork(const uint32_t = MAX_ITERAZ) = 0;
    virtual void makeSinogram(const BinVec3D_B & mask = BinVec3D_B(0,0,0)) = 0;

    void setSinogram(Sinogram &_s) {sino=_s;}
    void setPhantomAbsorption(BinVec2D_FS &_pa) {phantomAbsorption=_pa;}

    BinVec3D<TYPE> &getPhantom() {return phantom;}
    const BinVec3D<TYPE> &getPhantom() const {return phantom;}

    BinVec3D<TYPE> &getPhantomAbsorption() {return phantomAbsorption;}
    const BinVec3D<TYPE> &getPhantomAbsorption() const {return phantomAbsorption;}

    BinVec3D<TYPE> &getPhantomSelfAbsorption() {return phantomSelfAbsorption;}
    const BinVec3D<TYPE> &getPhantomSelfAbsorption() const {return phantomSelfAbsorption;}

    GenericSinogram3D<TYPE> &getSinogram() {return sino;}
    const GenericSinogram3D<TYPE> &getSinogram() const {return sino;}

protected:
    BinVec3D<TYPE>              phantomSelfAbsorption;
    BinVec3D<TYPE>              phantomAbsorption;
    BinVec3D<TYPE>              phantom;
    GenericSinogram3D<TYPE>     sino;
    GeometryTable<TYPE>         *gt;

private:
	Algorithm(const Algorithm<TYPE> &) {}
	Algorithm<TYPE> & operator=(const Algorithm<TYPE> &) {}
};

#ifdef USER_DOC
/**
 * FreeART class to do a SART reconstruction
 *
 * This class is the heart of the FreeART reconstruction software. It is this class which will effectively
 * do  the reconstruction using a SART (Simultaneous Algebraic Reconstruction Technique) algorithm.
 * It is a template class with two template parameters allowing the user to specify the
 * computation data type and the reconstruction type.
 * @tparam TYPE The data type used for all computations
 * @tparam RECONS The reconstruction type.
 *
 * In FreeART, there is a class specific to each reconstruction type. These classes are:
 * \li <b>TxReconstruction</b> for a transmission reconstruction
 * \li <b>FluoReconstruction</b> for a fluorescence reconstruction
 * \li <b>DiffractReconstruction</b> for a diffraction reconstruction
 * It's one of these classes which has to be specified as the RECONS template parameter.
 *
 * @headerfile FreeART.h
 * Note : In this file we have a redundancy of getter & setter function to call the functions of the reconstruction parameters class
 * This is needed because of the python binding with is targeting the SARTAlgorithm class.
 */
template <typename TYPE,template<typename> class RECONS>
class SARTAlgorithm
{
#else
template <typename TYPE,template<typename> class RECONS>
class SARTAlgorithm: public Algorithm<TYPE>
{
#endif
public:

/**
* Constructor to be used for Tx reconstruction
*
* @param [in] _sinos The sinogram data
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const Sinograms3D<TYPE> &_sinos, SinogramsGeometry &_sinosGeo);
/**
* Constructor (with absorption). To be used for Fluorescence or Diffraction reconstruction
*
* @param [in] _sinos The sinogram data
* @param [in] _matr The absorption matrix
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const Sinograms3D<TYPE> &_sinos, const BinVec3D<TYPE> &_matr, SinogramsGeometry &_sinosGeo);

/**
* Constructor (with absorption ans delf absorption). To be used for Diffraction reconstruction
*
* @param [in] _sinos The sinogram data
* @param [in] _matr The absorption matrix
* @param [in] _selfAbs The selfAbsoprtion flag
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const Sinograms3D<TYPE> &_sinos, const BinVec3D<TYPE> &_matr, const bool _selfAbs, SinogramsGeometry &_sinosGeo);

/**
* Constructor (with absorption and self absorption). To be used for Fluorescence reconstruction
*
* @param [in] _sinos The sinogram data
* @param [in] _matr The absorption matrix
* @param [in] _selfMatr The self absorption matrix
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const Sinograms3D<TYPE> &_sinos, const BinVec3D<TYPE> &_matr, const BinVec3D<TYPE> &_selfMatr, SinogramsGeometry &_sinosGeo);
/**
* Constructor to be used to generate sinogram in Tx, Fluorescence (without self-absorption) or Diffraction mode
*
* @param [in] _matr The phantom absorption matrix
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const BinVec3D<TYPE> &_matr, SinogramsGeometry &_sinosGeo);
/**
* Constructor to be used to generate sinogram in Diffraction mode with self-absorption
*
* @param [in] _matr The phantom absorption matrix
* @param [in] _selfAbs The selfAbsoprtion flag
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const BinVec3D<TYPE> &_matr, const bool _selfAbs, SinogramsGeometry& _sinosGeo);
/**
* Constructor to be used to generate sinogram in Fluorescence mode with self-absorption
*
* @param [in] _matr The phantom absorption matrix
* @param [in] _selfMatr The phantom self absorption matrix
* @param [in] _sinosGeo The experiment geometry
*/
    SARTAlgorithm(const BinVec3D<TYPE> &_matr,const BinVec3D<TYPE> &_selfMatr,SinogramsGeometry &_sinosGeo);

/**
* Constructor to be used to generate sinogram in Fluorescence mode with self-absorption
*
* @param [in] _phMatr the matrice of the phantom
* @param [in] _absMatr The phantom absorption matrix
* @param [in] _selfAbsMatr The phantom self absorption matrix
* @param [in] _sinosGeo The geometry of the experimentation
*/
    SARTAlgorithm(const BinVec3D<TYPE>& _phMatr, const BinVec3D<TYPE>& _absMatr, const BinVec3D<TYPE>& _selfAbsMatr, SinogramsGeometry& _sinosGeo);
    
/**
* Ask algorithm to do the reconstruction
*
* This method triggers the reconstruction computation with the interation number passed as argument
*
* @param [in] _iterNb The iteration number to be executed
*/
    virtual void doWork(const uint32_t _iterNb);
/**
* Ask algorithm to compute a sinogram
*
* This method triggers a sinogram computation. With the inputp parameter it is possible to
* specify only a region of interest
*
* @param [in] _mask Mask to be used in case of sinogram generation with region of interest (ROI)
*/
    virtual void makeSinogram(const BinVec3D_B & _mask = BinVec3D_B(0,0,0));

/**
* Get the voxel size. The voxels are cubes so x_size == y_size == z_size
* @param [out] the size of a voxel (x, y and z size ) in cm
* Note : this values can be normalized by using the values defined in the units.h file
*/
    const TYPE getVoxelSize() const { return rp.getVoxelSize(); }

/**
* Set the voxel size. The voxels are cubes so x_size == y_size == z_size
* @param [in]
*/
/// Warning : the setting of this value must be normalized by using the values defined in the units.h file
    void setVoxelSize(TYPE _dim) { rp.setVoxelSize(_dim);}

/**
* Set over sampling factor
*
* Set the algorithm over sampling factor. By default its value is 2.
*
* @param [in] _val The new over sampling factor value
*/
    void setOverSampling(uint32_t _val) {
        // # TODO henri : remove the cast and set setOversampling input to size_t
        rp.setOversampling((size_t)_val);
    }
/**
* Set the interpolation parameter
*
* @param [in] _val The new directive to use the interpolation or not
*/
    void setRayPointCalculationMethod(int _val){
        rp.setRayPointCalculationMethod( static_cast<RayPointCalculationMethod> (_val));
    }

/**
* Set the parameter to know if we want to create one ray per each point sample in the incoming ray (for the fluorescence mode)
*
* @param [in] _val true if we want to create the 'real' outfoing ray for each point sample in the incoming ray
*/
    void setOutgoingRayAlgorithm(int _val){
        rp.setOutgoingRayAlgorithm( static_cast<OutgoingRayAlgorithm> (_val));
    }


/**
* Set the number of which each cell of the SelfAbsMatWill be devided if we are using the matriceSubdivision option for the
* OutgoingBeamCalculationMethod. 
*
* WARNING : in fact the cell will be devide according to both axis. So the cell will be devided by _val*_val
*
* @param [in] _val 
*/
    void setSubdivisionSelfAbsMat(uint32_t _val){
        rp.setSubdivisionSelfAbsMat(_val);
    }

/**
* Set the intensity of the source. If this is not set ehn the defalt value will be 1.0
*
* @param [in] _I0 the intensity of the source
*/
    void setI0(TYPE _I0){
        rp.setI0(_I0);
    }


/**
* Set the parameters to know if we want to compute the real solid angle or not
*
* @param [in] _off true if we want to turn off the solid Angle (set always the value to 1)
*/
    void turnOffSolidAngle(bool _off){
        rp.turnOffSolidAngle(_off);
    }


    void setRandSeedToZero(bool _off){
        rndmAccessor.setSeedToZero(_off);
    }

/**
* Get over sampling factor
*
* Get the algorithm over sampling factor. By default its value is 2.
*
* @return The over sampling factor value
*/
    uint32_t getOverSampling() const {return rp.getOverSampling();}
/**
* Set the upper limit threshold
*
* When one algorithm iteration result is applied to the already computed value, it is possible to filter out
* values which are outside a user defined window. This upper limit defined the upper threshold for this window.
* All values greater (stricly) than this threshold will be replaced by the threshold. By the default, this value is
* infinity
*
* @param [in] _val The new threshold
*/
    void setUpperLimit(TYPE _val);
/**
* Get the upper limit threshold
*
* Get the algorithm upper limit. See method \see setUpperLimit to know more about this upper limit
*
* @return The upper limit
*/
    TYPE getUpperLimit() const {return upperLimit;}
/**
* Set the lower limit threshold
*
* When one algorithm iteration result is applied to the already computed value, it is possible to filter out
* values which are outside a user defined window. This lower limit defined the lower threshold for this window.
* All values lower (stricly) than this threshold will be replaced by the threshold. By default, this value
* is set to 0 (meaning rejecting all negative values)
*
* @param [in] _val The new threshold
*/
    void setLowerLimit(TYPE _val);
/**
* Get the lower limit threshold
*
* Get the algorithm lower limit. See method \see setLowerLimit to know more about this upper limit
*
* @return The upper limit
*/
    TYPE getLowerLimit() const {return lowerLimit;}

///@privatesection

    virtual ~SARTAlgorithm();

    virtual void init();
    virtual void initRotation(uint32_t);

    void setSelfAbsorption(bool _val) {selfAbs=_val;}
    bool getSelfAbsorption() {return selfAbs;}

    void setDampingFactor(TYPE _val) {
        rp.setDampingFactor(_val);
    }

    void printReconsParam() {
        rp.print();
    }

    TYPE getDampingFactor() const {return rp.getDampingFactor();}

    RECONS<TYPE> &getReconstruction() {return recons;}
    BckProjection &getBckProjection() {return bckProj;}

    void printInfo() const;

private:
    SARTAlgorithm(const SARTAlgorithm<TYPE,RECONS> &) {}
    SARTAlgorithm<TYPE,RECONS> & operator=(const SARTAlgorithm<TYPE,RECONS> &) {}

    void setDefaultValue();
    void fromNewInterfaceToFormerWay(const Sinograms3D<TYPE> &,SinogramsGeometry &);
    void checkAndPrepareIteration(ReconstructionParameters<TYPE> &,const GenericSinogram3D<TYPE> &,const uint32_t &);
    uint32_t computeMaxRayLength(uint32_t,uint32_t) const;
    void checkMask(const BinVec3D_B &,const BinVec3D<TYPE> &) const;
    void initMakeSino();
    void initReconstr();
    void detsDistanceLengthAngle(SinogramsGeometry &);
    void positionToAngle(const Position_FC &,double &);

    bool                            makeSino;   //< do we want to rpoduce a sinogram
    bool                            abs;        //< True if the phantom absorption volume is provided (aka phantom for incoming rays)
    bool                            selfAbs;    //< True if the phantom self absorption volume is provided (aka phantom for outgoing rays)
    TYPE                            upperLimit; //< higher value limitation
    TYPE                            lowerLimit; //< lower value limitation

    uint32_t                        maxPointNum;//< maximal number of point sample per ray

    RECONS<TYPE>                    recons;     //< the type of reconstruction/ projection we want to made : transmission, fluorescence...
    BckProjection                   bckProj;    //< the algorithm for the back projection

    BinVec3D<TYPE>                  diffMatr;   //< diffMatr for diffraction reconsturction
    RandomAccessMng                 rndmAccessor;//< The random accessor to pick pseudo randomly the rotation to use for reconstruction
    ReconstructionParameters<TYPE>  rp;         //< The parameters of the reconstruction/projection

    AnglesArray                     angArray;       // Used when generating sinogram

    BinVec<double>                  detsLength;     // lengths of detectors
    BinVec<double>                  detsDistance;   // distances from matrice phantom center to detectors
    BinVec<double>                  detsAngle;      // Angle between incoming beam and detector center (OC vector in doc)
};

} // End of FreeART namespace

#endif	/* FREEART_ALGORITHM_H */

