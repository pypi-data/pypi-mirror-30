//+==================================================================================================================
//
// GeometryFactory.hpp
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
 * GeometryFactory.hpp
 *
 *  Created on: Dec 1, 2014
 *      Author: vigano
 */

#include "RayHelpers.h"
#include "ScannerPhantom2D.h"
#include "ReconstructionParameters.h"

#include <sstream>
#include <assert.h>

namespace FREEART_NAMESPACE
{

template <typename TYPE>
void GeometryFactory::addRotation( BaseGeometryTable<TYPE> & gt, const radians & angle,
                              const RayProperties<TYPE> & rayProp, const bool isIncoming)
{
#ifdef DEBUG_SAMPLING
  cout << "add rotation " << (isIncoming ? "Incoming " : "Outgoing ") << angle << endl; 
#endif

  /* Let's create a rotation object that represents a projection, and fill it
   * with the rays */
  // Rotation<TYPE> * rot = new Rotation<TYPE>(angle, (isIncoming ? gt.getTotIncomingRaysPerRot() : gt.getTotOutgoingRaysPerRot() ),
  Rotation<TYPE> * rot = new Rotation<TYPE>(angle, (isIncoming ? gt.getIncomingRays() : gt.getOutgoingRays() ) );
  for(uint32_t numRay = 0; numRay < (isIncoming ? gt.getTotIncomingRaysPerRot() : gt.getTotOutgoingRaysPerRot()); numRay++)
  {
    /* This approach can support ray Intensity modulation or fluctuations */
    // Here the ray.offset can be see as the initial offset - the offset the ray at the left possition of the set of rays.
    // offsetBetweenRays is the offset between each rays
    const TYPE offset = rayProp.offset + (TYPE)numRay*rayProp.width;

    // if this is an incoming ray then we a re taking the source intensity. Otherwise we take 1.0 
    // because for outgoing we will multiple the value with the intensity of the incoming. As we
    // are computing absorption this is correct.
    const TYPE I0 = isIncoming ? gt.getReconstructionParams()->getI0() : TYPE(1.0);
    // cout << "a " << numRay << " isincoming = " << isIncoming << " outgoing rays vect size = " << gt.getOutgoingRays().size() <<   endl; 
    // rot->getRay(numRay) = Ray<TYPE>(rayProp.width, offset, I0);
    rot->getRay(numRay).setWidth(rayProp.width);
    rot->getRay(numRay).setOffset(offset);
    rot->getRay(numRay).setI0(I0);
  }

  /* We insert now the rotation in the table */
  gt.push_back( rot );
}

template <typename TYPE>
RayProperties<TYPE>
GeometryFactory::prepareTable(BaseGeometryTable<TYPE> & gt, const bool isIncoming)
{
#ifdef DEBUG_SAMPLING
  cout << "prepareTable for " << (isIncoming ? "Incoming" : "Outgoing") << endl; 
  cout << " Should get " << gt.getReconstructionParams()->getTotRaysPerRot().incoming << " inc rays ";
  cout << gt.getReconstructionParams()->getTotRaysPerRot().outgoing << " out rays" << endl;
  cout << "with an offset of " << gt.getReconstructionParams()->getRayOffset().incoming << " inc rays";
  cout << gt.getReconstructionParams()->getRayOffset().outgoing << " out rays" << endl;
#endif


  /* Sets the parameters about the phantom that is going to be sampled */
  if (gt.getPhantomLength() == 0)
    gt.setPhantomLength(matrDims.x);
  if (gt.getPhantomWidth() == 0)
    gt.setPhantomWidth(matrDims.y);
  DebugPrintf(("Preparing table against a phantom ( %u, %u)\n",
     gt.getPhantomWidth(), gt.getPhantomHeight()));

  /* Information about the rays */
  const TYPE rayWidth = isIncoming ? gt.getReconstructionParams()->getRayWidth().incoming : gt.getReconstructionParams()->getRayWidth().outgoing;

  /* Let's compute the initial offset of the first ray */
  const TYPE radiusActiveRegion = isIncoming ? 
    gt.getReconstructionParams()->getRadiusActiveRegion():
    gt.getReconstructionParams()->getRadiusActiveRegionForOutgoing();
  const TYPE rest = (TYPE)fmod((TYPE)(radiusActiveRegion*2.0), rayWidth);
  const TYPE rayOffset = (rayWidth - (radiusActiveRegion*2.0) - rest)/2.0;

  // if this is an incoming ray then we a re taking the source intensity. Otherwise we take 1.0 
  // because for outgoing we will multiple the value with the intensity of the incoming. As we
  // are computing absorption this is correct.
  const TYPE I0 = isIncoming ? gt.getReconstructionParams()->getI0() : TYPE(1.0);

  return RayProperties<TYPE>(rayWidth, rayOffset, I0) ;
}

template <typename TYPE>
void GeometryFactory::createTable(BaseGeometryTable<TYPE> & gt, const AnglesArray & angles, const bool isIncoming)
{
#ifdef DEBUG_SAMPLING
  cout << "createTable for " << (isIncoming ? "Incoming" : "Outgoing") << endl; 
  cout << " Should get " << gt.getReconstructionParams()->getTotRaysPerRot().incoming << " inc rays ";
  cout << gt.getReconstructionParams()->getTotRaysPerRot().outgoing << " out rays" << endl;
  cout << "with an offset of " << gt.getReconstructionParams()->getRayOffset().incoming << " inc rays";
  cout << gt.getReconstructionParams()->getRayOffset().outgoing << " out rays" << endl;
#endif

  const RayProperties<TYPE> rayProp = prepareTable(gt, isIncoming);

  const size_t & anglesSize = angles.size();
  CHECK_THROW(anglesSize, InitializationException(
        "Vector of angles' size is 0, Table cannot be initialized!"));

  gt.reserve(anglesSize);

  /* Initialize rotations */
  /* For every angle, scan the sample */
  const BinVec_FC::const_iterator anglesEnd = angles.end();
  for(BinVec_FC::const_iterator it1 = angles.begin(); it1 != anglesEnd; it1++) {
    cout << "create new rays for rotation : " << *it1 << endl;
    addRotation(gt, *it1, rayProp);
  }
}

template <typename TYPE>
void GeometryFactory::createTable(BaseGeometryTable<TYPE> & gt, const radians & angle, const bool isIncoming)
{
#ifdef DEBUG_SAMPLING
  cout << "createTable for " << (isIncoming ? "Incoming" : "Outgoing") << endl; 
  cout << " Should get " << gt.getReconstructionParams()->getTotRaysPerRot().incoming << " inc rays ";
  cout << gt.getReconstructionParams()->getTotRaysPerRot().outgoing << " out rays" << endl;
  cout << "with an offset of " << gt.getReconstructionParams()->getRayOffset().incoming << " inc rays";
  cout << gt.getReconstructionParams()->getRayOffset().outgoing << " out rays" << endl;
#endif

  const RayProperties<TYPE>rayProp = prepareTable(gt, isIncoming);
  gt.reserve(1);

  /* Initialize rotation */
  addRotation(gt, angle, rayProp, isIncoming);
}

template <typename TYPE>
void GeometryFactory::createTable(BaseGeometryTable<TYPE> & gt, const Sinogram & sino, const bool isIncoming)
{
#ifdef DEBUG_SAMPLING
  cout << "createTable for " << (isIncoming ? "Incoming" : "Outgoing") << endl; 
  cout << " Should get " << gt.getReconstructionParams()->getTotRaysPerRot().incoming << " inc rays ";
  cout << gt.getReconstructionParams()->getTotRaysPerRot().outgoing << " out rays" << endl;
  cout << "with an offset of " << gt.getReconstructionParams()->getRayOffset().incoming << " inc rays";
  cout << gt.getReconstructionParams()->getRayOffset().outgoing << " out rays" << endl;
#endif  

  const size_t sinoSize = sino.size();

  CHECK_THROW(sinoSize, InitializationException(
        "Sinogram's size is 0, Table cannot be initialized!"));

  const RayProperties<TYPE> rayProp = prepareTable(gt);
  /* We need to verify that the sinogram is consistent with the number of rays
   * per rotation. This prevents building a table that has a different number
   * of rays per projection from the sinogram */
  if (sino.getWidth() != gt.getTotIncomingRaysPerRot()) {
    stringstream stream;
    stream  << "The number of rays required and the width of the sinogram are"
              << " different:" << endl
            << "Number of rays: " << gt.getTotIncomingRaysPerRot() << ", "
            << "Sinogram size: " << sino.getWidth() << endl;
    throw InitializationException(stream.str());
  }

  gt.reserve(sinoSize);

  /* Initialize rotations */
  /* For every angle, scan the sample */
  const Sinogram::const_iterator sinoEnd = sino.end();
  for(Sinogram::const_iterator it1 = sino.begin(); it1 != sinoEnd; it1++) {
    addRotation(gt, (*it1)->angle, rayProp);
  }
}

template <typename TYPE>
void GeometryFactory::sampleTable(BaseGeometryTable<TYPE> & gt, const bool isIncoming)
{
  const size_t & totRots = gt.size();
  /* Let's now evaluate the sampling points */
  ScannerPhantom2D<TYPE> scanner(gt);
  scanner.sampleVoxels(gt, isIncoming);

  /* Let's build now the offset table */
  uint32_t offset = 0;
  gt.offsetsTable.reset(totRots, gt.getTotIncomingRaysPerRot());
  for(uint32_t numRot = 0; numRot < totRots; numRot++) {
    const Rotation<TYPE> & rot = gt.getRotation(numRot);
    for(uint32_t numRay = 0; numRay < gt.getTotIncomingRaysPerRot(); numRay++) {
      // cout << "b " << numRay << endl; 
      const Ray<TYPE> & ray = rot.getRay(numRay);
      gt.offsetsTable.getRayOffset(numRot, numRay) = offset;
      offset += ray.size();
    }
  }
}

template <typename TYPE>
void GeometryFactory::updateIncomingLossFraction(GeometryTable<TYPE> & gt,
    const BinVec3D<TYPE> & absorbMatr)
{
  const size_t & totRots = gt.size();
  uint32_t numRot = 0;
#if defined(HAVE_OMP)
  #pragma omp parallel for shared(absorbMatr, gt, totRots) private(numRot)
#endif
  for(numRot = 0; numRot < totRots; numRot++) {
    updateIncomingLossFraction(gt, absorbMatr, numRot);
  }
}

template <typename TYPE>
void GeometryFactory::updateIncomingLossFraction(GeometryTable<TYPE> & gt,
                                            const BinVec3D<TYPE> & absMatr,
                                            const uint32_t & numRot)
{
  Rotation<TYPE> & rot = gt.getRotation(numRot);
  TYPE* lossFractionIncident = gt.lossFractionIncident + gt.offsetsTable.getRotOffset(numRot);

  updateIncomingLossFraction(rot, 
                             absMatr, 
                             lossFractionIncident, 
                             (TYPE)1.0/(TYPE)gt.getReconstructionParams()->getOverSampling(), 
                             gt.getReconstructionParams()->getVoxelSize() );
}

/// Simple function to print matrice to the console
template<typename T>
void printMatrice( const vector<T>& matrix ){
  unsigned int width = sqrt(matrix.size());
  std::cout.precision(3);
  for(unsigned int iVal = 0; iVal < matrix.size(); iVal++){
    if(iVal%(width) == 0){
      cout << endl;
    }else{
      cout << " , ";
    }
    cout << matrix[iVal];
  }
  cout << endl;
}

template <typename TYPE>
void GeometryFactory::updateIncomingLossFraction(Rotation<TYPE> & rot,
                                            const BinVec3D<TYPE> & absMatr,
                                            TYPE * lossFractionIncident,
                                            const TYPE stepLength,      // in voxel
                                            const TYPE physicalSize)
{
  /* -- IMPORTANT -- Numerical Stability/Convergence
   * There may be issues in the numerical stability/convergence of the method
   * in case the product interactLen*coefficient is not in the region (-2 ,0)
   * for every coefficient in the vector.
   * To cope with it we need to check every time if the product is in the region
   * of stability, otherwise solve the problem doing an artificial reduction of
   * the step considering more steps in one step, but with a shorter length. */
  const TYPE interactLength = stepLength * rot.integralNormalization * physicalSize;
  /* Let's allocate a buffer for loading the coefficients */
  size_t maxPoints = 0;
  for(typename vector<Ray<TYPE> >::iterator itRay = rot.begin(); itRay != rot.end(); ++itRay ){
    maxPoints = std::max(maxPoints, itRay->size());
  }

  /* A buffer based on a vector class is safer and better against memory leaks:
   * You can check the access, the boundaries, and it get's automatically
   * deallocated when returning from the function (even in case of exception) */
  BinVec<TYPE> coeffsBufferObj(maxPoints);
  TYPE * const coeffsBuffer = &*coeffsBufferObj.begin();
  for(typename vector<Ray<TYPE> >::iterator itRay = rot.begin(); itRay != rot.end(); ++itRay )
  {
    TYPE fract = 1.0;
    // Get the absorption coefficient for each point of the ray 
    loadMeanCoeffs(*itRay, absMatr, coeffsBuffer);

    // WARNING : 
    // Previously we where not computing from source to the detector but from the detector to the source.
    // This had an effect in the fluorescence mode because we want to get the incomingLoss ans the outgoing loss.
    // To get the "correct" effect then we add this small fix of resetting the values (2).
    // This is a bad hack in the sense that it is costly. 
    // But to make a correct fix we should sample the rau in the invert direction.
    // Might be done one day
    /// TODO Henri : iterate on the overway
    const TYPE * const endCoeff  = coeffsBuffer + itRay->size();
    const TYPE * coeff           = coeffsBuffer;
    vector<TYPE> vals;

    vals.resize(itRay->size());
    for(int i=0; coeff < endCoeff; coeff++, i++)
    {
      fract *= exp(-interactLength*(*coeff)); 
      assert(! isnan(fract) );
      vals[i] = fract;
    }
    // order do no change the global attenuation
    itRay->lossFractionOutput = TYPE(fract);

    // reset the values in the correct order (2)
    for(typename vector<TYPE>::iterator it = vals.begin(); it < vals.end(); ++it  ){
      *lossFractionIncident++ = fract / *it;
      assert(! isnan(*lossFractionIncident) );
    }

#if defined(DEBUG)
#ifndef _MSC_VER
    if (endCoeff >= &*coeffsBufferObj.end()) {
      stringstream stream;
      stream  << "ERROR in " << __PRETTY_FUNCTION__ << ": Exceeded buffer size!"
              << endl << "Wrong calculation of the buffer size (maximum number "
              << "of sampled points)";
      throw OutOfBoundException(stream.str());
    }
#endif
#endif
  }
}

template<typename TYPE>
INLINE void 
GeometryFactory::createSelfAbsorptionMatriceFromRays(
  const Rotation<TYPE>& rot,
  const BinVec3D<TYPE>& initialSelfAbsorbMatr,
  BinVec<TYPE>& OBLossFractionBuffer,
  BinVec3D<TYPE>& outgoingBeamTotalAttenuationMatrice )
{

  typename BinVec<TYPE>::iterator buff = OBLossFractionBuffer.begin();

  BinVec2D<TYPE> coeffsMatr(outgoingBeamTotalAttenuationMatrice.getLength(), outgoingBeamTotalAttenuationMatrice.getWidth());
  unsigned int iRay = 0;
  // for eqch rotation we are doing
  for(typename vector<Ray<TYPE> >::const_iterator ray = rot.begin(); ray != rot.end(); ray++, iRay++)
  {  
    typename vector<RayPoint<TYPE> >::const_iterator itPoint;
    // For each sample point of the ray
    for(itPoint = ray->samplePointsBegin(); itPoint != ray->samplePointsEnd(); ++itPoint, ++buff)
    { 
      const TYPE & lossFract = *buff;
      // we add the contribution of the point to the voxels he is sampling
      const uint32_t * const voxlist = itPoint->getIndexesList();
      const TYPE * const weights = itPoint->getWeightsList();      

      switch (itPoint->getNbVoxelsSample()) {
        case 4: {
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[0]) += lossFract * weights[0];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[1]) += lossFract * weights[1];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[2]) += lossFract * weights[2];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[3]) += lossFract * weights[3];

          coeffsMatr.get((int)voxlist[0]) += weights[0];
          coeffsMatr.get((int)voxlist[1]) += weights[1];
          coeffsMatr.get((int)voxlist[2]) += weights[2];
          coeffsMatr.get((int)voxlist[3]) += weights[3];
          break;
        }
        case 2: {
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[0]) += lossFract * weights[0];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[1]) += lossFract * weights[1];

          coeffsMatr.get((int)voxlist[0]) += weights[0];
          coeffsMatr.get((int)voxlist[1]) += weights[1];
          break;
        }
        case 3: {
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[0]) += lossFract * weights[0];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[1]) += lossFract * weights[1];
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[2]) += lossFract * weights[2];

          coeffsMatr.get((int)voxlist[0]) += weights[0];
          coeffsMatr.get((int)voxlist[1]) += weights[1];
          coeffsMatr.get((int)voxlist[2]) += weights[2];
          break;
        }              
        case 1: {
          outgoingBeamTotalAttenuationMatrice.get((int)voxlist[0]) += lossFract * weights[0];
          
          coeffsMatr.get((int)voxlist[0]) += weights[0];          
          break;
        }
        default: {
          WarningPrintf(("No Voxel sampled here!\n"));
          break;
        } 
      }
    } // end for points in ray

  } // end for rotation

  // Henri : pb : both matrice haven t the same size
  assert(std::distance(coeffsMatr.begin(), coeffsMatr.end()) == std::distance(outgoingBeamTotalAttenuationMatrice.begin(), outgoingBeamTotalAttenuationMatrice.end()));
  /* Let's normalize the values in the matrix, based on how much it was covered
   * during the sampling. If the covering is not enough we put 1 as denominator,
   * to avoid division by 0 */
  typename BinVec<TYPE>::const_iterator coeff = coeffsMatr.begin();
  for(typename BinVec3D<TYPE>::iterator fract = outgoingBeamTotalAttenuationMatrice.begin();
      fract != outgoingBeamTotalAttenuationMatrice.end(); fract++, coeff++)
  {
    if(*coeff != 0){
      *fract /= *coeff;
    }
  }
}

template <typename TYPE>
void GeometryFactory::scaleMatrice_xy(const BinVec3D<TYPE> & matrToScale, BinVec3D<TYPE>& scaledMatr, const uint32_t scaleFactor)
{
  assert(scaleFactor > 1);
  uint32_t width = matrToScale.getWidth();
  scaledMatr.reset(matrToScale.getLength()*scaleFactor, matrToScale.getWidth()*scaleFactor, matrToScale.getHeight() );

  typename BinVec3D<TYPE>::iterator itScaled = scaledMatr.begin();
  uint32_t index = 0;

  typename BinVec3D<TYPE>::const_iterator itOriginal;
  for(itOriginal = matrToScale.begin(); itOriginal != matrToScale.end(); ++itOriginal){
    uint32_t oldIndex_y = (uint32_t)floor((double)index / (double)width );
    uint32_t oldIndex_x = index - oldIndex_y*width ;

    for(unsigned int ix = 0; ix < scaleFactor; ix++){
      for(unsigned int iy = 0; iy < scaleFactor; iy++){
        uint32_t newx = oldIndex_x*scaleFactor + ix;
        uint32_t newy = oldIndex_y*scaleFactor + iy;
        scaledMatr.get(newx, newy, 0) = *itOriginal;
      }
    }
    index++;
  }
}


template <typename TYPE>
void GeometryFactory::updateSelfAbsorptionMatrices(Rotation<TYPE> & rot,
    const BinVec3D<TYPE> & absorbMatr, BinVec3D<TYPE> & selfAbsorbMatr,
    const ReconstructionParameters<TYPE>& rp)
{

  /* Reset absorption matrix to zero */
  selfAbsorbMatr.clean(); // Not to zero but to one from previously setted values !!!

  /* let's compute the regular loss fraction if the ray was coming from the
   * detector. In the next section we will transform this to the real outgoing
   * loss fraction: here we just reuse a routine for doing part of the job */
  if( (rp.getOutgoingRayAlgorithm() == matriceSubdivision)  && (rp.getSubdivisionSelfAbsMat() > 1) ){
    /* Local buffer */
    uint32_t scaleFactor = rp.getSubdivisionSelfAbsMat();
    BinVec<TYPE> lossFractBuffer(rot.totSampledPoints*scaleFactor*scaleFactor);

    BinVec3D<TYPE> scaledAbsorbMatr;
    // scale the matrice. This is simply the matrice subdivision
    scaleMatrice_xy(absorbMatr, scaledAbsorbMatr, scaleFactor );

    // Then compute the attenuation along each rays
    updateIncomingLossFraction(rot, scaledAbsorbMatr, &*lossFractBuffer.begin(), 
      (TYPE) 1.0/ (scaleFactor*rp.getOverSampling()), rp.getVoxelSize());

    selfAbsorbMatr.reset( (uint32_t)(absorbMatr.getLength()*scaleFactor), 
                          (uint32_t)(absorbMatr.getWidth()*scaleFactor), 
                          (uint32_t)(absorbMatr.getHeight()) );

    /* initialSelfAbsorbMatr contains the 'local' attenuation of the outgoing beam.
     * What we want it is for eqch voxel the attenuation from this voxel to the detector
     * That i what we will compute now. */
    createSelfAbsorptionMatriceFromRays(rot, scaledAbsorbMatr, lossFractBuffer, selfAbsorbMatr);

  }else{
    /* Local buffer */
    BinVec<TYPE> lossFractBuffer(rot.totSampledPoints);

    updateIncomingLossFraction(rot, absorbMatr, &*lossFractBuffer.begin(), 
      (TYPE) 1.0/(TYPE)rp.getOverSampling(), rp.getVoxelSize());

    /* initialSelfAbsorbMatr contains the 'local' attenuation of the outgoing beam.
     * What we want it is for eqch voxel the attenuation from this voxel to the detector
     * That i what we will compute now. */
    createSelfAbsorptionMatriceFromRays(rot, absorbMatr, lossFractBuffer, selfAbsorbMatr);    
  }
}

template <typename TYPE>
INLINE TYPE
GeometryFactory::getOutgoingLossFraction( const Rotation<TYPE>& rot, const Position<TYPE>& initPos, 
  Ray<TYPE>& ray, const BinVec3D<TYPE>& selfAbsMatrix, RotationData<TYPE> rotData, TYPE lineDenom, 
  TYPE angularCoeff, ScannerPhantom2D<TYPE>& scanner, const radians& outgoingAngle,
  const ReconstructionParameters<TYPE>& rp )
{
  const TYPE incr = (TYPE) 1.0/(TYPE)rp.getOverSampling();

  /* The physical size of the voxel is important for quantitative results */
  const TYPE & physicalSize = rp.getVoxelSize();
  // cout << "physicalSize " << physicalSize << endl;

  /* -- IMPORTANT -- Numerical Stability/Convergence
   * There may be issues in the numerical stability/convergence of the method
   * in case the product interactSurface*coefficient is not in the region (-2 ,0)
   * for every coefficient in the vector.
   * To cope with it we need to check every time if the product is in the region
   * of stability, otherwise solve the problem doing an artificial reduction of
   * the step considering more steps in one step, but with a shorter length. */
  const TYPE interactLength = incr*physicalSize;

  // deal with the sampling
  IterationData<TYPE> data( rotData, incr );

  /* Let's define the line followed by the given ray */
  data.line = StraightLine(angularCoeff, (ray.offset)/lineDenom);

  /* get the final point of the ray (intersection circle/ray) amd update data informations (limits, begin/end points ... ) */
  scanner.fixRayExit( data, outgoingAngle, initPos);

  /* Samples the given ray */
  scanner.sampleLineFromOriginAndDirection(ray, data );  

  TYPE fract = 0;
  typename vector<RayPoint<TYPE> >::const_iterator itPoint;
  for( itPoint = ray.samplePointsBegin(); itPoint != ray.samplePointsEnd(); ++itPoint)
  {
    fract += itPoint->getMeanField(selfAbsMatrix)*interactLength;
    assert(! isnan(fract) );
  }
  ray.lossFractionOutput = TYPE(exp(-fract));
  return ray.lossFractionOutput;
}

template <typename TYPE>
INLINE void 
GeometryFactory::updateIncomingLossFractionWithOutgoingLossFraction(
  Rotation<TYPE>& incomingRot,
  const BinVec3D<TYPE> & selfAbsMatrice,
  TYPE* incomingLossFraction,
  GeometryTable<TYPE>& gt,
  ScannerPhantom2D<TYPE>& scanner,
  radians detAngle )
{
  const radians outgoingRayAngle = incomingRot.angle+detAngle;

  // create the nor;alization for the Joseph sampling
  TYPE angularCoeff = 0.0;
  TYPE lineDenom = 0.0;
  RotationData<TYPE> rotData(VOXEL_WIDTH, VOXEL_LENGTH);

  rotData.refSys.setRotAngleRadians( outgoingRayAngle );

  scanner.setRotData(rotData, angularCoeff, lineDenom, gt.getReconstructionParams()->getOverSampling());
  
  // TODO henri : shouldn t probably not use the rays from gt...
  typename vector<Ray<TYPE> >::iterator itRayOutgoing = gt.getOutgoingRays().begin();
  for(typename vector<Ray<TYPE> >::iterator itRay = incomingRot.begin(); itRay != incomingRot.end(); ++itRay, ++itRayOutgoing)
  {

    SubRayIterator<TYPE> point(*itRay, itRay->pointIncrement);
    for(; !point.isEnd(); point++, incomingLossFraction++)
    {     
      // The angle of the outgoing ray is the angle of the incoming ray + the angle that the detector is
      // making with the outgoing ray (cd : here the sample is fixed, this the couple detector/incomingbeam which is 
      // turning around the sample.)
      assert(gt.getReconstructionParams() != NULL);
      TYPE outgoingLossFraction = getOutgoingLossFraction(incomingRot, point.getPosition(), *itRayOutgoing, selfAbsMatrice, 
        rotData, lineDenom, angularCoeff, scanner, outgoingRayAngle, *gt.getReconstructionParams());
      *incomingLossFraction *= outgoingLossFraction; 
    }    
  }
}

template <typename TYPE>
void GeometryFactory::updateSelfAbsorptionMatrices(GeometryTable<TYPE> & gt,
                                              const BinVec3D<TYPE> & absMatr,
                                              const radians detAngle)
{
  const size_t & totRots = gt.size();

  if(gt.getReconstructionParams()->getOutgoingRayAlgorithm() == createOneRayPerSamplePoint ){
    // make sure we have the correct number of geometry (== number of detector)
    assert(gt.selfAbsGeometries.size() == 1);
    ScannerPhantom2D<TYPE> scanner(gt);
    for(uint32_t rot = 0; rot < totRots; rot++) {
      TYPE* lossFractionIncident =
        gt.lossFractionIncident + gt.offsetsTable.getRotOffset(rot);
      
      updateIncomingLossFractionWithOutgoingLossFraction( gt.getRotation(rot), absMatr, lossFractionIncident, gt, scanner, detAngle);
    }
  }else{
    const size_t & numOfDetectors = gt.selfAbsGeometries.size();
    for(uint32_t det = 0; det < numOfDetectors; det++) {
      BaseGeometryTable<TYPE> & detGeometry = gt.selfAbsGeometries[det];
      DebugPrintf(("Updating self-absorption matrices (%03u) for detector: %u\n",
                    _FT_UI32(totRots), _FT_UI32(det+1)));
      for(uint32_t rot = 0; rot < totRots; rot++) {
        BinVec3D<TYPE> & matr = gt.selfAbsAttenuations.get(det, rot);
        updateSelfAbsorptionMatrices(detGeometry.getRotation(rot), absMatr, matr, *gt.getReconstructionParams());
      }
    }
  }
}


template <typename TYPE>
void GeometryFactory::buildIncomingLossFraction(GeometryTable<TYPE> & gt,
    const BinVec3D<TYPE> & absorbMatr)
{
  ASSIGN_NEW_C_ARRAY(gt.lossFractionIncident, new TYPE[gt.totSampledPoints]);
  updateIncomingLossFraction(gt, absorbMatr);
}

template <typename TYPE>
void GeometryFactory::loadMeanCoeffs(const SubRay<TYPE> & subray,
    const BinVec3D<TYPE> & matr, TYPE * coeff)
{
  typename vector<RayPoint<TYPE> >::const_iterator itPoint;
  for(itPoint = subray.samplePointsBegin(); itPoint != subray.samplePointsEnd(); ++itPoint)
  {
    *coeff++ = itPoint->getMeanField(matr);
  }
}

template <typename TYPE>
GeometryTable<TYPE> *GeometryFactory::getGeometryFromSinogram(const GenericSinogram3D<TYPE> & sino,
                                                              const bitset<MAX_TYPES> reconsType,
                                                              const ReconstructionParameters<TYPE>& rp,
                                                              const bool selfAbs)
{
  const size_t & totRot = sino.size();
  CHECK_THROW(totRot, InitializationException(
      "Cannot make geometry: number of total rotation is 0"));

  /* Let's now guess some quantities like: phantom's dimensions and radius of
   * it's active region */
  const double  voxelLength  = VOXEL_LENGTH;
  const double  voxelWidth = VOXEL_WIDTH;

  matrDims = guessPhantomDims(sino.getRayNb(), voxelLength, voxelWidth);

  DebugPrintf(("Starting to create the headers and then fill\n"));
  GeometryTable<TYPE> *gt = new GeometryTable<TYPE>(rp);
  gt->setMatrDims(matrDims);

  try {
    if (selfAbs == true)
    {
        buildSelfAbsorptionGeometry(*gt,1,reconsType);
    }
  } catch (const BasicException & ex) {
    delete gt;
    throw ex;
  }
  return gt;
}

template <typename TYPE>
GeometryTable<TYPE> *
GeometryFactory::getGeometryFromPhantom(const BinVec3D<TYPE> &phantom,
                                        const TYPE radius,
                                        const bitset<MAX_TYPES> reconsType,
                                        const ReconstructionParameters<TYPE>& rp,
                                        const bool selfAbs,
                                        const AnglesArray & angles )
{
  DebugPrintf(("Starting to create the headers and then fill\n"));
  GeometryTable<TYPE> * gt = NULL;
  try {
    gt = new GeometryTable<TYPE>(rp);
    AnglesArray &geoAngles = gt->getRotAnglesArray();
    geoAngles = angles;

    Dimensions_UI32 phDims(phantom.getLength(),phantom.getWidth(),phantom.getHeight());
    gt->setPhantomDims(phDims);

    matrDims.x = phantom.getLength();
    matrDims.y = phantom.getWidth();

    if (selfAbs == true)
    {
        buildSelfAbsorptionGeometry(*gt, 1, reconsType);
    }
    return gt;

  } catch (const BasicException & ex) {
    delete gt;
    throw ex;
  }
}


template <typename TYPE>
void GeometryFactory::buildSelfAbsorptionGeometry(GeometryTable<TYPE> & gt,
                                                  size_t numRots,const bitset<MAX_TYPES> reconsType)
{
  size_t totNumRots = numRots;

  /* Structure with the geometries of self-absorption for every detector */
  BinVec<BaseGeometryTable<TYPE> > & emGTs = gt.selfAbsGeometries;

  /* Structure with the matrices of self-absorption for every detector */
  PointedBinVec2D<BinVec3D<TYPE> > & emAtts = gt.selfAbsAttenuations;

  /* This creates an empty structure, but when allocating a new row, we will get
   * exactly 'totNumRots' matrices: all the matrices for the self-absorption for
   * every rotation of the phantom */
  emAtts.reset(0, totNumRots);

  if (reconsType.test(FLUORESCENCE_TYPE) == true ||
      reconsType.test(COMPTON_TYPE) == true) {

    emGTs.reset(1);
    Dimensions_UI32 phDims(gt.getPhantomLength(),gt.getPhantomWidth(),gt.getPhantomHeight());
    if(gt.getOutgoingRayAlgorithm() == matriceSubdivision){
      phDims.x *= gt.getReconstructionParams()->getSubdivisionSelfAbsMat();
      phDims.y *= gt.getReconstructionParams()->getSubdivisionSelfAbsMat();
    }

    emGTs[0].setPhantomDims(phDims);
    emAtts.allocateNewRows(1);

  } else if (reconsType.test(DIFFRACTION_TYPE) == true) {
    emGTs.reset(2);
    Dimensions_UI32 phDims(gt.getPhantomLength(),gt.getPhantomWidth(),gt.getPhantomHeight());
    emGTs[0].setPhantomDims(phDims);
    emGTs[1].setPhantomDims(phDims);
    emAtts.allocateNewRows(2);
  }

  /* Now we allocate the points in the matrices, initialized to 0.0, that
   * corresponds to no self-absorption at all */
  uint32_t vol_length = matrDims.x;
  uint32_t vol_width = matrDims.y;
  uint32_t vol_height = 1;

  DebugPrintf(("Initializing self-absorption matrices\n"));
  for(uint32_t det = 0; det < emAtts.getWidth(); det++) {
    for(uint32_t numVol = 0; numVol < emAtts.getLength(); numVol++) {
      BinVec3D<TYPE> & vol = emAtts.get(det, numVol);
        vol.reset(vol_length, vol_width, vol_height);
    }
  }
}


template <typename TYPE>
void GeometryFactory::assignSolidAngles(GeometryTable<TYPE> & gt, const FluoDetector & det)
{
  ASSIGN_NEW_C_ARRAY(gt.solidAngles, new TYPE[(unsigned int)gt.totSampledPoints]);
  TYPE *solidAngle = gt.solidAngles;

  ReferencedObject ref(0.0, VOXEL_LENGTH, VOXEL_WIDTH);
  /* Buffers for the positions of the points in the rays and other temporary
   * quantities in the computation of the solid angles */
  BinVec<Position<TYPE> > posBuff, inPosBuff;

  // True if we want to set all solid angles to 1
  bool turnOffSolidAngle = !gt.getReconstructionParams()->isSolidAngleOn();
  
#if defined(HAVE_SSE)
  BinVec<float_S> quadNormBuff, normBuff;
#endif

  const size_t & totRots = gt.size();
  for(uint32_t numRot = 0; numRot < totRots; numRot++)
  {
    const Rotation<TYPE> & rot = gt.getRotation(numRot);
    /* Needed to change back to external system of reference in order to be
     * able to setup solid angles with the right dimensions */
    // ref.setRotAngleRadians(rot.angle);

    for(uint32_t numRay = 0; numRay < gt.getTotIncomingRaysPerRot(); numRay++)
    {
      const Ray<TYPE> & ray = rot.getRay(numRay);
      DEBUG_DECL(const TYPE * tempSolidAngle = solidAngle);

      /* Let's resize the buffers to the actual size of the ray */
      const size_t & raySize = ray.size();
      posBuff.resize(raySize);
      inPosBuff.resize(raySize);
#if defined(HAVE_SSE)
      quadNormBuff.resize(raySize), normBuff.resize(raySize);
#endif

      /* First of all let's fetch all the positions of the points in the ray */
      typename BinVec<Position<TYPE> >::iterator pos = posBuff.begin();
      for(ConstSubRayIterator<TYPE> point(ray, rot.increment); !point.isEnd();
          point++, pos++)
      {
        *pos = point.getPosition();
      }
      /* Move all the points to the external system of reference */
      ref.toExternalCentered<TYPE, TYPE>(posBuff, inPosBuff);

#if defined(HAVE_SSE)
      /* Compute the solid angles for all those points */
      det.solidAngles(inPosBuff, posBuff, quadNormBuff, normBuff, solidAngle);

      /* Let's now update the position in the vector of the solid angles */
      solidAngle += raySize;
#else
      /* Compute the solid angles for all those points */
      for(typename BinVec<Position<TYPE> >::const_iterator inPos = inPosBuff.begin();
          inPos != inPosBuff.end(); inPos++, solidAngle++)
      {
        if(turnOffSolidAngle){
          *solidAngle = 1.0;
        }else{
          *solidAngle = TYPE(det.getSolidAngle(*inPos));
        }
      }
#endif

#if defined(DEBUG)
     for(typename BinVec<Position<TYPE> >::const_iterator inPos = inPosBuff.begin();
         inPos != inPosBuff.end(); inPos++, tempSolidAngle++)


      {
        if (*tempSolidAngle < 0) {
          stringstream stream;
          stream << "Got negative solid angle in iteration with:\n  "
                 << "Rotational Angle: " << rot.angle << "(rad), "
                 << "Ray Offset: " << ray.offset << "(), "
                 << "Voxel Internal Position: (" << inPos->x
                    << ", " << inPos->y << ")\n";
          throw BadSolidAngleException(stream.str());
        }
      }
#endif
    } /* End of the For over the records */
  }
}


} // End of FreeART namespace
