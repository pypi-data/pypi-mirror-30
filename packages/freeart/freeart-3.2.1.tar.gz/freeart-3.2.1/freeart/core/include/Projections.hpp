//+==================================================================================================================
//
// Projections.tpp
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
 * File:   Projections.tpp
 * Author: taurel
 *
 * Created on 2 December 2014
 */

#ifndef PROJECTIONS_TPP
#define	PROJECTIONS_TPP

#include "macros.h"

namespace FREEART_NAMESPACE
{

//-------------------------------------------------------------------------------------------------------
//
//                      Reconstruction class methods
//
//-------------------------------------------------------------------------------------------------------

template<typename TYPE>
Reconstruction<TYPE>::Reconstruction():
  reconsParam(NULL), detector(NULL){

}

template<typename TYPE>
inline void
Reconstruction<TYPE>::computeSelfAbsCorrections( const BinVec3D<TYPE> & vol,
                                           const SubRay<TYPE> & subray,
                                           TYPE * buffer)
  const
{
  typename vector<RayPoint<TYPE> >::const_iterator itPoint;
  for(itPoint = subray.samplePointsBegin(); itPoint != subray.samplePointsEnd(); ++itPoint)
  {
    TYPE meanField = itPoint->getMeanField(vol);
    assert(!isnan(meanField));
    *buffer++ = meanField; 
  }
}

// this function has been created to get indices for the matriceSubdivision option
// and to compute on the fly the new indices to fit to the scaled selfAbsMat
template<typename TYPE>
inline void
Reconstruction<TYPE>::computeSelfAbsCorrectionsWithScale(const BinVec3D<TYPE> & vol,
                                                  const SubRay<TYPE> & subIncomingray,
                                                  TYPE * buffer, 
                                                  const ReconstructionParameters<TYPE>& rp) 
  const
{

  // Here we only want to affect to the incoming rays the good value of the outgoing ray attenaution.
  // But has we devided the outgoing rays attenation matrice we need to get the 
  // corresponding position of the sampling point to this matrice of a differente dimensions
  const TYPE newSemiX = rp.getSemiXOutgoing();
  const TYPE newSemiY = rp.getSemiYOutgoing();

  Position<TYPE> currentPosition = subIncomingray.initPosition;

  VoxelSelector<TYPE> voxelSelector(rp, vol.getLength(), vol.getWidth());
  voxelSelector.setIsIncomingBeam(false);

  typename vector< RayPoint<TYPE> >::const_iterator itPoint;
  for(itPoint = subIncomingray.samplePointsBegin(); itPoint !=subIncomingray.samplePointsEnd(); ++itPoint)
  {
    BinVec_UI32 indexes;
    indexes.resize(4);
    BinVec<TYPE> weights;
    weights.resize(4);

    uint8_t size = 0;

    // Avoir un manager aui s occupe de ca, serait plus simple
    Position<TYPE> convert(
      (TYPE)(currentPosition.x*( rp.getSubdivisionSelfAbsMat()) + newSemiX), 
      (TYPE)(currentPosition.y*(rp.getSubdivisionSelfAbsMat()) + newSemiY),
      currentPosition.z );

    voxelSelector.selectVoxels( convert, indexes, weights, size );
    *buffer++ = (itPoint->getMeanField(vol, indexes, weights));

    currentPosition += subIncomingray.pointIncrement;
  } 
}



template<typename TYPE>
INLINE TYPE
Reconstruction<TYPE>::localComputeRaySum(const BinVec3D<TYPE> & vol, const SubRay<TYPE> & ray,
    const bool & completeSinogram, const BinVec3D_B & mask,
    const TYPE * voxIndepParams)
{
  TYPE signal = 0;

  typename BinVec< RayPoint<TYPE> >::const_iterator itPoint;
  for(itPoint = ray.samplePointsBegin(); itPoint != ray.samplePointsEnd(); ++itPoint, voxIndepParams++)
  {
    /* If it is complete we don't mind to consider voxel by voxel through the
     * mask */
    if (completeSinogram)
    {
      signal += itPoint->getMeanField(vol) *(*voxIndepParams);
    }
    else
    {
      /* Otherwise let's check voxel by voxel */
      TYPE signalSmplPoint = 0;
      const uint32_t * voxIndexes = itPoint->getIndexesList();
      const TYPE *voxWeights = itPoint->getWeightsList();
      const uint32_t numTotVox = itPoint->getNbVoxelsSample();
      for(uint32_t numVox = 0; numVox < numTotVox;
          numVox++, voxIndexes++, voxWeights++)
      {
        /* if this voxel is allowed by the mask, let's sum it up */
        if ( mask.get( *voxIndexes ) )
        {
          signalSmplPoint +=  *voxWeights *
                              /* Weight of the voxel */
                              vol.get(*voxIndexes);
                              /* Emission probab of the voxel */
        }
      }
      signal += signalSmplPoint * (*voxIndepParams);
    }
  }
  return signal;
}

//-------------------------------------------------------------------------------------------------------
//
//                      TxReconstruction class methods
//
//-------------------------------------------------------------------------------------------------------

template <typename TYPE>
void TxReconstruction<TYPE>::fwdProjection(const BinVec3D<TYPE> &vol,const Ray<TYPE> &ray,
                                           const GeometryTable<TYPE> *gt,bool selfAbs,
                                           BinVec3D<TYPE> &selfAbsBuff,TYPE &denom,TYPE &fp )
{
    (void)gt;
    (void)selfAbs;
    (void)selfAbsBuff;
    typename vector<RayPoint<TYPE> >::const_iterator itPoint;
    for(itPoint = ray.samplePointsBegin(); itPoint != ray.samplePointsEnd(); ++itPoint)
    {
        fp += itPoint->getMeanField(vol);
        denom += itPoint->getSquareWeightSum();
    }
}

template <typename TYPE>
void TxReconstruction<TYPE>::initRotation(GeometryTable<TYPE> &gt,bool selfAbs,
                                          const BinVec3D<TYPE> &phAbsorption,
                                          const BinVec3D<TYPE> &phSelfAbsorption,
                                          TYPE detAngle )
{
    // to shut down warning
    (void)gt;
    (void)selfAbs;
    (void)phAbsorption;
    (void)phSelfAbsorption;
    (void)detAngle;
}

template <typename TYPE>
void TxReconstruction<TYPE>::initRotationMakeSino(GeometryTable<TYPE> &gt,const uint32_t  numRot,const bool selfAbs,
                                                  const BinVec3D<TYPE> &phAbsorp,const BinVec3D<TYPE> &phSelfAbsorp,
                                                  const TYPE detAngle )
{
    (void)selfAbs;
    (void)phAbsorp;
    (void)phSelfAbsorp;
    (void)detAngle;

    AnglesArray rotAnglesArray = gt.getRotAnglesArray();

    const size_t numSlice = 0;
    gt.computeGeometryForSliceRotation(numSlice,rotAnglesArray[numRot], Reconstruction<TYPE>::getRayPointCalculationMethod());
}

template <typename TYPE>
void TxReconstruction<TYPE>::raySum(BinVec3D<TYPE> &vol,const Ray<TYPE> &ray,const GeometryTable<TYPE> *gt,const bool selfAbs,
                                    BinVec3D<TYPE> &selfAbsBuff,const BinVec3D_B &mask,TYPE &signal)
{
    (void)gt;
    (void)selfAbs;
    (void)selfAbsBuff;
    (void)mask;

    typename vector<RayPoint<TYPE> >::const_iterator it;
    for(it = ray.samplePointsBegin(); it != ray.samplePointsEnd(); ++it)
    {
        signal += it->getMeanField(vol);
    }
}

//-------------------------------------------------------------------------------------------------------
//
//                      FluoReconstruction class methods
//
//-------------------------------------------------------------------------------------------------------

template<typename TYPE>
INLINE
void FluoReconstruction<TYPE>::tuplewise_2vectors_product(const TYPE *vec01, const TYPE *vec02,const uint32_t & totPoints)
throw()
{
  /* I'm using iterators instead of pointers, but they work exactly the same */
  const typename BinVec<TYPE>::iterator endOfPoints = this->voxIndepParamBuff.begin() + totPoints;
  for(typename BinVec<TYPE>::iterator vecBuffer = this->voxIndepParamBuff.begin();
      vecBuffer != endOfPoints; vecBuffer++, vec01++, vec02++)
  {
    *vecBuffer = *vec01 * *vec02;
    assert(!isnan(*vecBuffer));
  }
}

template<typename TYPE>
INLINE
void FluoReconstruction<TYPE>::tuplewise_3vectors_product(const TYPE *vec01, const TYPE *vec02,
                                               const TYPE *vec03,const uint32_t & totPoints)
throw()
{
  /* I'm using iterators instead of pointers, but they work exactly the same */
  const typename BinVec<TYPE>::iterator endOfPoints = this->voxIndepParamBuff.begin() + totPoints;
  for(typename BinVec<TYPE>::iterator vecBuffer = this->voxIndepParamBuff.begin();
      vecBuffer != endOfPoints; vecBuffer++, vec01++, vec02++, vec03++)
  {
    *vecBuffer = *vec01 * *vec02 * *vec03;
    assert(!isnan(*vecBuffer));
  }
}

template <typename TYPE>
void FluoReconstruction<TYPE>::initRotation(GeometryTable<TYPE> &gt,bool selfAbs,const BinVec3D<TYPE> &phAbsorption,
                                            const BinVec3D<TYPE> &phSelfAbs, TYPE _detAngle )
{
    DebugPrintf(("Entering initRotation()"));
    numRay = 0;
    
/* Compute incident loss fraction and solid angles for this rotation */

    gt.createInitLossFractionIncident();
    GeometryFactory geomFactory;
    geomFactory.updateIncomingLossFraction(gt,phAbsorption);

    detector = new FluoDetector(detLength[0],detDistance[0], _detAngle);
    geomFactory.assignSolidAngles(gt,*detector);

/* If required, compute geometry for fluorescence detector and update self absorption matrix */

    if (selfAbs == true)
    {
        gt.computeGeometryForFluoDetector(_detAngle, Reconstruction<TYPE>::getRayPointCalculationMethod());
        geomFactory.updateSelfAbsorptionMatrices(gt, phSelfAbs, _detAngle);
    }
}

template <typename TYPE>
void FluoReconstruction<TYPE>::initRotationMakeSino(GeometryTable<TYPE> &gt,
                                                    const uint32_t numRot,
                                                    const bool selfAbs,
                                                    const BinVec3D<TYPE> &phAbsorp,
                                                    const BinVec3D<TYPE> &phSelfAbsorp,
                                                    const TYPE _detAngle )
{
    DebugPrintf(("Entering initRotationMakeSino() for rot %d\n",numRot));
    AnglesArray rotAnglesArray = gt.getRotAnglesArray();
    const size_t numSlice = 0;
    gt.computeGeometryForSliceRotation(numSlice, rotAnglesArray[numRot], Reconstruction<TYPE>::getRayPointCalculationMethod());

    numRay = 0;
    GeometryFactory geomFactory;
    gt.createInitLossFractionIncident();
    geomFactory.updateIncomingLossFraction(gt,phAbsorp);

    detector = new FluoDetector(detLength[0],detDistance[0], _detAngle);
    geomFactory.assignSolidAngles(gt,*detector);

    if (selfAbs == true)
    {
        gt.computeGeometryForFluoDetector(detector->getAngle(), Reconstruction<TYPE>::getRayPointCalculationMethod());
        geomFactory.updateSelfAbsorptionMatrices(gt, phSelfAbsorp, _detAngle);
    }

}

template <typename TYPE>
void FluoReconstruction<TYPE>::fwdProjection(const BinVec3D<TYPE> &matr,const Ray<TYPE> &incomingRay,
                                             const GeometryTable<TYPE> *gt,bool selfAbs,
                                             BinVec3D<TYPE> &selfAbsBuff,TYPE &denom,TYPE &fp )
{
    const uint32_t & raySize = incomingRay.size();
    uint32_t deltaPoint = gt->getOffsets().getRayOffset(0,numRay);
    const TYPE *solidAngle = gt->getSolidAngles() + deltaPoint;
    const TYPE *inLossFract = gt->getIncidentLossFractions() + deltaPoint;
    numRay++;

    if (selfAbs && (this->getOutgoingRayAlgorithm() != createOneRayPerSamplePoint ) )
    {
        const BinVec3D<TYPE> & selfMatr  = gt->getSelfAbsorpAttenuation(0, 0);

        if(this->getOutgoingRayAlgorithm() == matriceSubdivision){
           // Let's load interpolated self-absorption coefficients for the points in the ray 
          this->computeSelfAbsCorrectionsWithScale(selfMatr, incomingRay, &*selfAbsBuff.begin(), *gt->getReconstructionParams() );          
        }else{
          this->computeSelfAbsCorrections(selfMatr, incomingRay, &*selfAbsBuff.begin() );          
        }

        /* Let's do the product between corrections for Solid Angle, Incoming Beam Attenuation and Self-Absorption for every
        point of the ray */
        this->tuplewise_3vectors_product(solidAngle,inLossFract,&*selfAbsBuff.begin(),raySize);
    }else
    {
        /// Note : for fluorescence, effect of the outgoing ray has already been computed and integrated
        /// in the sample point value
        /* Let's do the product between corrections for Solid Angle and Incoming Beam Attenuation for every point of the ray */
        this->tuplewise_2vectors_product(solidAngle,inLossFract,raySize);
    }

    TYPE *params = &*this->voxIndepParamBuff.begin();

    typename vector<RayPoint<TYPE> >::const_iterator itPoint;
    for(itPoint = incomingRay.samplePointsBegin(); itPoint != incomingRay.samplePointsEnd(); ++itPoint, params++)
    {
        fp += *params * itPoint->getMeanField(matr);
        denom += *params * itPoint->getSquareWeightSum();
    }
}

template <typename TYPE>
void FluoReconstruction<TYPE>::raySum(
  BinVec3D<TYPE> &vol,
  const Ray<TYPE> &ray,
  const GeometryTable<TYPE> *gt,
  const bool selfAbs,
  BinVec3D<TYPE> &selfAbsBuff,
  const BinVec3D_B &mask,
  TYPE &signal )
{
    const uint32_t & raySize = ray.size();
    uint32_t deltaPoint = gt->getOffsets().getRayOffset(0,numRay);
    const TYPE *solidAngle = gt->getSolidAngles() + deltaPoint;
    const TYPE *inLossFract = gt->getIncidentLossFractions() + deltaPoint;
    numRay++;

    if (selfAbs && (this->getOutgoingRayAlgorithm() != createOneRayPerSamplePoint ) )
    {
        const BinVec3D<TYPE> & selfMatr  = gt->getSelfAbsorpAttenuation(0, 0);

        if(this->getOutgoingRayAlgorithm() == matriceSubdivision){
           // Let's load interpolated self-absorption coefficients for the points in the ray 
          this->computeSelfAbsCorrectionsWithScale(selfMatr, ray, &*selfAbsBuff.begin(), *gt->getReconstructionParams() );          
        }else{
          this->computeSelfAbsCorrections(selfMatr, ray, &*selfAbsBuff.begin() );          
        }

        /* Let's do the product between corrections for Solid Angle, Incoming Beam Attenuation and Self-Absorption for every
        point of the ray */
        this->tuplewise_3vectors_product(solidAngle,inLossFract,&*selfAbsBuff.begin(),raySize);
    }else
    {
        /// Note : for fluorescence, effect of the outgoing ray has already been computed and integrated
        /// in the sample point value
        /* Let's do the product between corrections for Solid Angle and Incoming Beam Attenuation for every point of the ray */
        this->tuplewise_2vectors_product(solidAngle,inLossFract,raySize);
    }

    const bool completeSinogram = !mask.size();
    signal = ray.I0*this->localComputeRaySum(vol,ray,completeSinogram,mask,&*this->voxIndepParamBuff.begin());
}

template <typename TYPE>
void FluoReconstruction<TYPE>::cleanup(GeometryTable<TYPE> *gt,bool selfAbs)
{
    if (selfAbs == true)
    {
        BinVec<BaseGeometryTable<TYPE> > & detGeometry = gt->getSelfAbsGeometries();
        delete detGeometry[0][0];
        detGeometry[0].clear();

        PointedBinVec2D<BinVec3D<TYPE> >  &emAtts = gt->getSelfAbsAttenuations();
        for(uint32_t det = 0; det < emAtts.getWidth(); det++)
        {
            for(uint32_t numMatr = 0; numMatr < emAtts.getLength(); numMatr++)
            {
                BinVec3D<TYPE> & vol = emAtts.get(det, numMatr);
                size_t length = vol.getLength();
                size_t width = vol.getWidth();
                size_t height = vol.getHeight();
                vol.reset(length,width,height);
            }
        }
    }

    delete (*gt)[0];
    gt->clear();

    delete detector;
    detector = NULL;
}


//-------------------------------------------------------------------------------------------------------
//
//                      DiffractReconstruction class methods
//
//-------------------------------------------------------------------------------------------------------

template<typename TYPE>
INLINE void
DiffractReconstruction<TYPE>::compute_InAndOut_LossFract_product(
    const TYPE * inLossFract, const TYPE * outLeftLossFract,
    const TYPE * outRightLossFract, const uint32_t & totPoints)
  throw()
{
    const typename BinVec<TYPE>::iterator endOfPoints = this->voxIndepParamBuff.begin() + totPoints;
    for(typename BinVec<TYPE>::iterator vecBuffer = this->voxIndepParamBuff.begin();
      vecBuffer != endOfPoints;
      vecBuffer++, outLeftLossFract++, outRightLossFract++, inLossFract++)
    {
        *vecBuffer = (*outLeftLossFract + *outRightLossFract) * (*inLossFract) / 2;
    }
}

template <typename TYPE>
INLINE void
DiffractReconstruction<TYPE>::computeDiffrSelfAbsCorrectionParams(
    const GeometryTable<TYPE> & gt, const SubRay<TYPE> & ray,
    const TYPE * inLossFract, BinVec3D<TYPE> & selfAbsBuff)
{
    TYPE * const leftOutLossFract  = &*selfAbsBuff.begin();
    TYPE * const rightOutLossFract = &selfAbsBuff.get(0,1,0);

    const BinVec3D<TYPE> & leftMatr  = gt.getSelfAbsorpAttenuation(0, 0);
    this->computeSelfAbsCorrections(leftMatr, ray, leftOutLossFract);

    const BinVec3D<TYPE> & rightMatr = gt.getSelfAbsorpAttenuation(1, 0);
    this->computeSelfAbsCorrections(rightMatr, ray, rightOutLossFract);

    compute_InAndOut_LossFract_product(inLossFract,leftOutLossFract,rightOutLossFract,ray.size());
}

template <typename TYPE>
void DiffractReconstruction<TYPE>::initRotation(GeometryTable<TYPE> &gt,bool selfAbs,
                                                const BinVec3D<TYPE> &phAbsorption,
                                                const BinVec3D<TYPE> &phSelfAbsorption,
                                                TYPE _detAngle)
{
    (void)_detAngle;

    numRay = 0;

/* Compute incident loss fraction and solid angles for this rotation */

    gt.createInitLossFractionIncident();
    GeometryFactory geomFactory;
    geomFactory.updateIncomingLossFraction(gt,phAbsorption);


/* If required, compute geometry for fluorescence detector and update self absorption matrix */

    if (selfAbs == true)
    {
        gt.computeGeometryForDiffractDetector(detAngle, Reconstruction<TYPE>::getRayPointCalculationMethod());
        geomFactory.updateSelfAbsorptionMatrices(gt, phSelfAbsorption, _detAngle);
    }
}


template <typename TYPE>
void DiffractReconstruction<TYPE>::initRotationMakeSino(GeometryTable<TYPE> &gt,
                                                        const uint32_t numRot,
                                                        const bool selfAbs,
                                                        const BinVec3D<TYPE> &phAbsorp,
                                                        const BinVec3D<TYPE> &phSelfAbsorp,
                                                        const TYPE _detAngle )
{
    (void)_detAngle;
    AnglesArray rotAnglesArray = gt.getRotAnglesArray();

    const size_t numSlice = 0;
    gt.computeGeometryForSliceRotation(numSlice, rotAnglesArray[numRot], Reconstruction<TYPE>::getRayPointCalculationMethod());

    numRay = 0;
    gt.createInitLossFractionIncident();
    GeometryFactory geomFactory;
    geomFactory.updateIncomingLossFraction(gt,phAbsorp);

    if (selfAbs == true)
    {
        gt.computeGeometryForDiffractDetector(detAngle, Reconstruction<TYPE>::getRayPointCalculationMethod()  );
        geomFactory.updateSelfAbsorptionMatrices(gt, phSelfAbsorp, _detAngle);
    }

}


template <typename TYPE>
void DiffractReconstruction<TYPE>::fwdProjection(const BinVec3D<TYPE> &matr,const Ray<TYPE> &incomingRay,
                                                 const GeometryTable<TYPE> *gt,
                                                 const bool selfAbs,BinVec3D<TYPE> &selfAbsBuff,TYPE &denom,TYPE &fp)
{
    uint32_t deltaPoint = gt->getOffsets().getRayOffset(0,numRay);
    const TYPE *inLossFract = gt->getIncidentLossFractions() + deltaPoint;
    numRay++;

    const TYPE *params;

    if (selfAbs)
    {
        this->computeDiffrSelfAbsCorrectionParams(*gt,incomingRay,inLossFract,selfAbsBuff);
        params = &*this->voxIndepParamBuff.begin();
    }
    else
    {
        params = gt->getIncidentLossFractions();
    }

    typename vector<RayPoint<TYPE> >::const_iterator itPoint;
    for(itPoint = incomingRay.samplePointsBegin(); itPoint != incomingRay.samplePointsEnd(); ++itPoint, params++)
    {
        fp += *params * itPoint->getMeanField(matr);
        denom += *params * itPoint->getSquareWeightSum();
    }
}


template <typename TYPE>
void DiffractReconstruction<TYPE>::raySum(BinVec3D<TYPE> &vol,const Ray<TYPE> &ray,const GeometryTable<TYPE> *gt,
                                    const bool selfAbs,BinVec3D<TYPE> &selfAbsBuff,const BinVec3D_B &mask,TYPE &signal)
{
    uint32_t deltaPoint = gt->getOffsets().getRayOffset(0,numRay);
    const TYPE *inLossFract = gt->getIncidentLossFractions() + deltaPoint;
    numRay++;

    const TYPE *params;

    if (selfAbs)
    {
        this->computeDiffrSelfAbsCorrectionParams(*gt,ray,inLossFract,selfAbsBuff);
        params = &*this->voxIndepParamBuff.begin();
    }
    else
    {
        params = inLossFract;
    }

    const bool completeSinogram = !mask.size();
    signal = this->localComputeRaySum(vol,ray,completeSinogram,mask,params);
}

template <typename TYPE>
void DiffractReconstruction<TYPE>::cleanup(GeometryTable<TYPE> *gt,bool selfAbs)
{
    if (selfAbs == true)
    {
        BinVec<BaseGeometryTable<TYPE> > & detGeometry = gt->getSelfAbsGeometries();
        delete detGeometry[0][0];
        detGeometry[0].clear();
        delete detGeometry[1][0];
        detGeometry[1].clear();

        PointedBinVec2D<BinVec3D<TYPE> >  &emAtts = gt->getSelfAbsAttenuations();
        for(uint32_t det = 0; det < emAtts.getWidth(); det++)
        {
            for(uint32_t numVol = 0; numVol < emAtts.getLength(); numVol++)
            {
                BinVec3D<TYPE> &vol = emAtts.get(det, numVol);
                size_t length = vol.getLength();
                size_t width = vol.getWidth();
                size_t height = vol.getHeight();
                vol.reset(length,width,height);
            }
        }
    }

    delete (*gt)[0];
    gt->clear();
}

//-------------------------------------------------------------------------------------------------------
//
//                      BckProjection class methods
//
//-------------------------------------------------------------------------------------------------------

template <typename TYPE>
void BckProjection::execute(BinVec3D<TYPE> &vol,const SubRay<TYPE> &subray,const TYPE &correction)
{
    typename vector<RayPoint<TYPE> >::const_iterator itPoint;
    for(itPoint = subray.samplePointsBegin(); itPoint != subray.samplePointsEnd(); ++itPoint)
    {
        const uint32_t * const voxlist = itPoint->getIndexesList();
        const TYPE * const weights = itPoint->getWeightsList();

/* Simple loop unrolling on the voxels sampled by the point */

        switch (itPoint->getNbVoxelsSample())
        {
            case 4:
            {
                vol.get(voxlist[0]) += correction * weights[0],
                vol.get(voxlist[1]) += correction * weights[1],
                vol.get(voxlist[2]) += correction * weights[2],
                vol.get(voxlist[3]) += correction * weights[3];
                break;
            }

            case 2:
            {
                vol.get(voxlist[0]) += correction * weights[0],
                vol.get(voxlist[1]) += correction * weights[1];
                break;
            }

            case 3:
            {
                vol.get(voxlist[0]) += correction * weights[0],
                vol.get(voxlist[1]) += correction * weights[1],
                vol.get(voxlist[2]) += correction * weights[2];
                break;
            }

            case 1:
            {
                vol.get(voxlist[0]) += correction * weights[0];
                break;
            }

            default:
            {
                WarningPrintf(("No Voxel sampled here!\n"));
                break;
            }
        }
    }
}


} // End of FreeART namespace

#endif	/* PROJECTIONS_TPP */

