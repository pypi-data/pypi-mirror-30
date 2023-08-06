//+==================================================================================================================
//
// Projections.h
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
 * File:   Projections.h
 * Author: taurel
 *
 * Created on 18 November 2014,2015
 */

#ifndef PROJECTIONS_H
#define	PROJECTIONS_H

#include "RayHelpers.h"
#include "ReconstructionParameters.h"
#include <bitset>

namespace FREEART_NAMESPACE
{

template <typename TYPE,template<typename> class RECONS>
class SARTAlgorithm;

/**
 * Base class for FreeART Forward Projection
 *
 */
template <typename TYPE>
class Reconstruction
{
protected:
    /// The reconstructionParameters contains all information needed for reconstruction
    const ReconstructionParameters<TYPE>* reconsParam;

public:
    /// constructor
    Reconstruction();
    /// destructor
    virtual ~Reconstruction() {}

    ///
    /// run the forward projection for the given ray
    /// @param vol the voxelized volume containing densities or interaction probability (for fluorescence)
    /// @param ray the ray for wich we want to compute the forward projection
    /// @param gt the geometry table. Deals with the geometry for the reconstruction (solid anges, rays offsets, incoming/outgoing attenuations...)
    /// @param selfAbs True if we want to compute selfAbsorption
    /// @param selfAbsBuff the buffer of the selfAbsorption
    /// @param the denominator used for the SART algorithm
    /// @param fp the signal sum
    virtual void fwdProjection(const BinVec3D<TYPE> & vol, const Ray<TYPE>& ray, const GeometryTable<TYPE>* gt, 
        const bool selfAbs, BinVec3D<TYPE>& selfAbsBuff, TYPE& denom, TYPE& fp) = 0;
    virtual TYPE getRotationFactor(const Rotation<TYPE> &) = 0;
    virtual uint32_t getNumSelfAbsRay() =  0;
    virtual void cleanup(GeometryTable<TYPE> *,bool) = 0;
    virtual void initRotation(GeometryTable<TYPE> &,bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &, TYPE) = 0;
    virtual void initRotationMakeSino(GeometryTable<TYPE> &,const uint32_t,const bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,const TYPE) = 0;
    virtual void raySum(BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,const BinVec3D_B &,TYPE &) = 0;

    virtual void setDetectorGeometry(double,double,double) {throw NotImplementedException("Not available for base Reconstruction class");}
    virtual uint32_t getDetectorNb() {throw NotImplementedException("Not available for base Reconstruction class");}

	virtual std::bitset<MAX_TYPES> &getReconstructionType() {return reconsType;}
    void setVoxBuffSize(const uint32_t _s) {voxIndepParamBuff.resize(_s);}

    void computeSelfAbsCorrections(const BinVec3D<TYPE> &,const SubRay<TYPE> &,TYPE *) const;
    void computeSelfAbsCorrectionsWithScale(const BinVec3D<TYPE> &,const SubRay<TYPE> &,TYPE *, const ReconstructionParameters<TYPE>&) const;

    TYPE localComputeRaySum(const BinVec3D<TYPE> &,const SubRay<TYPE> &,const bool &,const BinVec3D_B &,const TYPE *);

    /// ReconstructionParameters setter
    void setReconstructionParam(const ReconstructionParameters<TYPE>* _reconsParam){ reconsParam = _reconsParam;}
    /// ReconstructionParameters getter
    void getReconstructionParam() const { return reconsParam;}

    uint32_t getOversampling() const { return (reconsParam ? reconsParam->getOverSampling() : OVERSAMPLING );}

    RayPointCalculationMethod getRayPointCalculationMethod() const { 
        return (reconsParam ?  reconsParam->getRayPointCalculationMethod() : static_cast<RayPointCalculationMethod> (DEFAULT_BEAM_CALCULATION_METHOD));}
    OutgoingRayAlgorithm getOutgoingRayAlgorithm() const { 
        return (reconsParam ?  reconsParam->getOutgoingRayAlgorithm() : static_cast<OutgoingRayAlgorithm> (DEFAULT_OUTGOING_BEAM_CALCULATION_METHOD));}


protected:
    BinVec<TYPE>                            voxIndepParamBuff;
    Detector                                *detector;
    bitset<MAX_TYPES>                       reconsType;
};

template <typename TYPE>
class TxReconstruction: public Reconstruction<TYPE>
{
public:
    TxReconstruction():Reconstruction<TYPE>() {this->reconsType.set(TRANSMISSION_TYPE);}
    virtual ~TxReconstruction() {}

    virtual void fwdProjection(const BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,TYPE &,TYPE & );
    virtual TYPE getRotationFactor(const Rotation<TYPE> &_r) {return _r.integralNormalization;}
    virtual uint32_t getNumSelfAbsRay() {return 0;}
    virtual void initRotation(GeometryTable<TYPE> &,bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,TYPE);

    virtual void initRotationMakeSino(GeometryTable<TYPE> &,const uint32_t,const bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,const TYPE);
    virtual void raySum(BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,const BinVec3D_B &,TYPE &);

    virtual uint32_t getDetectorNb() {return 1;}

    virtual void cleanup(GeometryTable<TYPE> *gt,bool selfAbs)
    {
        (void)selfAbs;
        delete (*gt)[0];
        gt->clear();
    }

private:
};

template <typename TYPE>
class FluoReconstruction: public Reconstruction<TYPE>
{
public:
    FluoReconstruction():Reconstruction<TYPE>()
    {
        detector=NULL;
        this->reconsType.set(FLUORESCENCE_TYPE);
        numRay = 0;
    }
    virtual ~FluoReconstruction() {delete detector;}

    virtual void fwdProjection(const BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,TYPE &,TYPE & );
    virtual TYPE getRotationFactor(const Rotation<TYPE> &_r) {return _r.integralNormalization;}
    virtual uint32_t getNumSelfAbsRay() {return detLength.size();}
    virtual void cleanup(GeometryTable<TYPE> *gt,bool selfAbs);
    virtual void initRotation(GeometryTable<TYPE> &,bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,TYPE);

    virtual void initRotationMakeSino(GeometryTable<TYPE> &,const uint32_t,const bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,const TYPE);
    virtual void raySum(BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,const BinVec3D_B &,TYPE &);

    virtual void setDetectorGeometry(double _l,double _d,double _a)
    {
        detLength.push_back(_l);
        detDistance.push_back(_d);
        detAngle.push_back(_a);
    }

    virtual uint32_t getDetectorNb() {return (uint32_t)detLength.size();}

private:
    void tuplewise_2vectors_product(const TYPE *,const TYPE *, const uint32_t &) throw();
    void tuplewise_3vectors_product(const TYPE *,const TYPE *, const TYPE *,const uint32_t &) throw();

    vector<double>  detLength;
    vector<double>  detDistance;
    vector<double>  detAngle;          // Angle between the incoming beam and the detector center (Supposed to be cst)

    FluoDetector    *detector;
    uint32_t        numRay;
};

template <typename TYPE>
class DiffractReconstruction: public Reconstruction<TYPE>
{
public:
    DiffractReconstruction():Reconstruction<TYPE>() {this->reconsType.set(DIFFRACTION_TYPE);}
    virtual ~DiffractReconstruction() {}

    virtual void fwdProjection(const BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,TYPE &,TYPE & );
    virtual TYPE getRotationFactor(const Rotation<TYPE> &_r) {return _r.integralNormalization;}
    virtual uint32_t getNumSelfAbsRay() {return detAngle.size();}
    virtual void cleanup(GeometryTable<TYPE> *gt, bool selfAbs);
    virtual void initRotation(GeometryTable<TYPE> &,bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,TYPE);

    virtual void initRotationMakeSino(GeometryTable<TYPE> &,const uint32_t,const bool,const BinVec3D<TYPE> &,const BinVec3D<TYPE> &,const TYPE);
    virtual void raySum(BinVec3D<TYPE> &,const Ray<TYPE> &,const GeometryTable<TYPE> *,const bool,BinVec3D<TYPE> &,const BinVec3D_B &,TYPE &);

    virtual void setDetectorGeometry(double _l,double _d,double _a)
    {
        (void)_l;
        (void)_d;
        detAngle.push_back(_a);
    }

    virtual uint32_t getDetectorNb() {return detAngle.size();}

private:
    void computeDiffrSelfAbsCorrectionParams(const GeometryTable<TYPE> &, const SubRay<TYPE> &,const TYPE *, BinVec3D<TYPE> &);
    void compute_InAndOut_LossFract_product(const TYPE *, const TYPE *,const TYPE *, const uint32_t &) throw();

    vector<double>  detAngle;
    uint32_t        numRay;
};


/**
 * Base class for FreeART Back Projection
 */

class BckProjection
{
public:
    BckProjection() {}
    ~BckProjection() {}

    template <typename TYPE>
    void execute(BinVec3D<TYPE> &,const SubRay<TYPE> &,const TYPE &);
private:
};


} // End of FreeART namespace

#endif	/* PROJECTIONS_H */

