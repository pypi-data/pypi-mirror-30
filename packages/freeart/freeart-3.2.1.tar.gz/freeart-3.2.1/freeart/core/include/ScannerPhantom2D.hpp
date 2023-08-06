//+==================================================================================================================
//
// ScannerPhantom2D.tpp
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
 * ScannerPhantom2D.tpp
 *
 *  Created on: Dec 7, 2010
 *      Author: vigano
 */

#include <ReferencedObject.h>
#include <cmath>
#include <iostream>

#ifdef HAVE_OMP
# include <omp.h>
#endif

namespace FREEART_NAMESPACE
{

#ifndef M_SQRT1_2
# define M_SQRT1_2 7.0710678118654752440E-1
#endif


///////////////////////////////////////////////////////////////////////////////
// Public Method

template <typename TYPE>
void
ScannerPhantom2D<TYPE>::sampleVoxels(BaseGeometryTable<TYPE>& lgt, const bool isIncoming)
{
  /* Sampling is based on the idea of a circle centered in the center of the
   * Phantom matrix. So for every ray of every projection we are going to
   * sample every fixed distance to get an almost uniform coverage of the matrix
   */
  VoxelSelector<TYPE>::setIsIncomingBeam(isIncoming);

  const TYPE  voxelLength  = VOXEL_LENGTH;
  const TYPE  voxelWidth = VOXEL_WIDTH;

  const uint32_t phantomLength = gt.getPhantomLength();
  const uint32_t phantomWidth = gt.getPhantomWidth();

  // Note : we don t need this, phantom is already of the good size !!!

  const TYPE radius =  TYPE(min((TYPE)(phantomLength)*voxelLength,
                             (TYPE)(phantomWidth)*voxelWidth) /2.0);

  TYPE radiusActiveRegion = VoxelSelector<TYPE>::rp.getRadiusActiveRegion();

  if (fabs(radiusActiveRegion - radius) > TOLL_COMP) {
    DebugPrintf(("Radius Changed! from %f to %f\n", radiusActiveRegion, radius));
    radiusActiveRegion = radius;
  }

  const float_C incr = 1/_FT_C(VoxelSelector<TYPE>::rp.getOverSampling());
  const uint32_t & totRots = (uint32_t)gt.size();

  uint32_t numRot = 0;
  uint64_t totPoints = 0;
#if defined(HAVE_OMP)
  #pragma omp parallel shared(lgt) private(numRot)
#endif
  {
#if defined(HAVE_OMP)
  #pragma omp for private(numRot)
#endif
  for(numRot = 0; numRot < totRots; numRot++)
  {
    Rotation<TYPE> & rot = lgt.getRotation(numRot);

    RotationData<TYPE> rotData(voxelLength, voxelWidth);

    rotData.refSys.setRotAngleRadians(rot.angle);

    /* Sets the angle of the rotation so the rays are now parallel to the
     * vertical axis, and they can be seen _externally_ like coming down
     * from the top to the bottom */
    TYPE angularCoeff = 0.0;
    TYPE lineDenom = 0.0;

#ifdef DEBUG_SAMPLING          
      cout << endl << endl << "_______ New rot _______" << endl;
#endif
 
    setRotData(rotData, rot, angularCoeff, lineDenom, VoxelSelector<TYPE>::rp.getOverSampling());
#ifdef DEBUG_SAMPLING          
    cout << "rot data after setting" << endl;
    rotData.printInfo();
#endif

    /* Now that the rotation is fixed, let's sample the single rays */
    const uint32_t totRaysPerRot = isIncoming ? lgt.getTotIncomingRaysPerRot() : lgt.getTotOutgoingRaysPerRot();
    for(uint32_t numRay = 0; numRay < totRaysPerRot; numRay++)
    {
      // cout << "c " << numRay << endl; 
      Ray<TYPE> & ray = rot.getRay(numRay);

      /* The iteration data holds the temporary information for the current scan
       */
      IterationData<TYPE> data( rotData, incr );
#ifdef DEBUG_SAMPLING          
      ray.printInfo();
      cout << endl << endl << " +++++ New Ray +++++" << endl;
      cout << " angularCoeff = " << angularCoeff << ", lineDemon = " << lineDenom << endl;    
      cout << " cosAngle = " << rotData.refSys.getCosAngle() << endl;
      cout << " sinAngle = " << rotData.refSys.getSinAngle() << endl;          
      cout << "after construction with incr = " << incr << endl;
      cout << " data.pos = " << data.getPosition().x << ", " << data.getPosition().y << endl;
#endif
      /* Let's define the line followed by the given ray */
      data.line = StraightLine(angularCoeff, (ray.offset)/lineDenom);

      /* Adjusts the initial point of the scan to be aligned */
      fixRayEntrance( data, ray.offset );
      /* Samples the given ray */
      sampleLine(ray, data );
      rot.totSampledPoints += (unsigned int) ray.size();
    }
  }

  /* Let's now sum the number of all the points sampled in the scan */
#if defined(HAVE_OMP)
  #pragma omp for private(numRot) reduction(+:totPoints)
#endif
  for(numRot = 0; numRot < totRots; numRot++) {
    const Rotation<TYPE> & rot = lgt.getRotation(numRot);
    totPoints += rot.totSampledPoints;
  }
  }
  gt.totSampledPoints = totPoints;
  DebugPrintf(("Sampled phantom with %20lu points\n", lgt.totSampledPoints));
}


template<typename TYPE>
INLINE void 
ScannerPhantom2D<TYPE>::fixRayExit(IterationData<TYPE>& data, const radians& angle, const Position<TYPE>& beginPoint)
{
  // get the final point of the ray (which is the intersection between the line and the circle of acquisition)
  Position_2D<TYPE> inter;
  vector<Position_2D<TYPE> > intersections = Circle_2D<TYPE>(Position_2D<TYPE>::getOrigin() , 
    VoxelSelector<TYPE>::rp.getRadiusActiveRegion()).getIntersections(
      Line_2D<TYPE>( Position_2D<TYPE>(beginPoint.x, beginPoint.y), Vector_2D<TYPE>((TYPE)sin(angle), (TYPE)cos(angle))) );

  switch(intersections.size()){
    case 2 :
    {
      // the solution will always be the first point
      inter = intersections[0];
      break;
    }
    case 1 :
    {
      inter = intersections[0];
      break;
    }
    default :
    {
      stringstream stream;
      stream << "FixRayExit : Can't find any intersection between the Line with origin (" << beginPoint.x << ", " << beginPoint.x << " )";
      stream << " and the circle of acquisition centered to the phantom center and with a radius of " << VoxelSelector<TYPE>::rp.getRadiusActiveRegion();
      stream << "This mean that FreeART try to sample on a ray outside the area of interest.";
      throw BasicException(stream.str());
    }
  } 
  const Position_2D<TYPE> endPoint = inter;
  // Let's fix the limits for the iteration: these limits will give a test for
  // * stopping the iterations over the ray points. 
  data.limits.x = (beginPoint.x < endPoint.x)
      ? Range_D(beginPoint.x, endPoint.x) : Range_D(endPoint.x, beginPoint.x);
  data.limits.y = (beginPoint.y < endPoint.y)
      ? Range_D(beginPoint.y, endPoint.y) : Range_D(endPoint.y, beginPoint.y);

  // To operate easily over the points, without caring about conditions on the
  // * main axis, we define a reference to the independent and the dependent
  // * coordinates 
  TYPE & indepCoord = data.rot.alongX ? data.getPosition().x : data.getPosition().y;
  TYPE & depCoord   = data.rot.alongX ? data.getPosition().y : data.getPosition().x;

  {
    // let's now decide the initial point to the independent coordinate 
    Range_D & limitsIndep = (data.rot.alongX ? data.limits.x : data.limits.y);
    indepCoord = data.rot.forward ? limitsIndep.min : limitsIndep.max;
  }

  //fix the sampling direction
  Vector_2D<TYPE> dir(endPoint.x - beginPoint.x, endPoint.y - beginPoint.y);
  dir.normalize();
  // update them from the increment level
  dir.x *=(TYPE)data.increment;
  dir.y *=(TYPE)data.increment;

  data.rot.pointIncrement.x = dir.x;
  data.rot.pointIncrement.y = dir.y;

  const TYPE direction = (data.rot.forward ? 1 : -1);
  indepCoord += direction * fmod((TYPE)fabs(indepCoord), (TYPE)data.increment);
  depCoord = data.line(indepCoord);

  data.setPosition(beginPoint);
}

template<typename TYPE>
INLINE void
ScannerPhantom2D<TYPE>::setRotData( RotationData<TYPE>& rotData, 
                                    TYPE& angularCoeff, 
                                    TYPE& lineDenom,
                                    const uint32_t overSamp )
{
  const TYPE incr = (TYPE)1.0/(TYPE)overSamp;

  // /* First of all it is important to define the most parallel axis to the
  //  * direction of the scan.
  //  * - From the Joseph's algorithm it will be the reference axis.
  //  * - Moreover we need to know if we will go from higher numbers to lower
  //  *   numbers or vice versa.
  //  * - Finally is important to know the slope and offset of the direction of
  //  *   scan. This is important for the increment in the scan process */
  const TYPE & cosAngle = (TYPE)rotData.refSys.getCosAngle();
  const TYPE & sinAngle = (TYPE)rotData.refSys.getSinAngle();
  const TYPE & absCosAngle = (TYPE)rotData.refSys.getAbsCosAngle();

  /* Normalization needed for the Joseph's algorithm, since the sampling is
   * going to be aligned to the internal matrix rows and columns */
  if (absCosAngle > M_SQRT1_2) {

    rotData.alongX = false;
    rotData.forward = (cosAngle > 0);

    angularCoeff = -sinAngle/cosAngle;
    lineDenom = cosAngle;
  } else {

    rotData.alongX = true;
    rotData.forward = !(sinAngle > 0);

    angularCoeff = -cosAngle/sinAngle;
    lineDenom = sinAngle;
  }

  const TYPE sign = (TYPE) (rotData.forward ? 1.0 : -1.0);
  if (rotData.alongX) {
    rotData.pointIncrement.x = sign*incr;
    rotData.pointIncrement.y = sign*incr*angularCoeff;
  } else {
    rotData.pointIncrement.x = sign*incr*angularCoeff;
    rotData.pointIncrement.y = sign*incr;
  }

}

template<typename TYPE>
INLINE void
ScannerPhantom2D<TYPE>::setRotData( RotationData<TYPE>& rotData, 
                                    Rotation<TYPE>& rot, 
                                    TYPE& angularCoeff, 
                                    TYPE& lineDenom,
                                    const uint32_t overSamp )
{
  const TYPE incr = (TYPE)1.0/(TYPE)overSamp;

  // /* First of all it is important to define the most parallel axis to the
  //  * direction of the scan.
  //  * - From the Joseph's algorithm it will be the reference axis.
  //  * - Moreover we need to know if we will go from higher numbers to lower
  //  *   numbers or vice versa.
  //  * - Finally is important to know the slope and offset of the direction of
  //  *   scan. This is important for the increment in the scan process */
  const TYPE & cosAngle = (TYPE)rotData.refSys.getCosAngle();
  const TYPE & sinAngle = (TYPE)rotData.refSys.getSinAngle();
  const TYPE & absCosAngle = (TYPE)rotData.refSys.getAbsCosAngle();
  const TYPE & absSinAngle = (TYPE)rotData.refSys.getAbsSinAngle();

  /* Normalization needed for the Joseph's algorithm, since the sampling is
   * going to be aligned to the internal matrix rows and columns */
  if (absCosAngle > M_SQRT1_2) {
    /* Iterate on the internal Y (vertical axis) */
    rot.integralNormalization = TYPE(1.0/absCosAngle);

    rotData.alongX = false;
    rotData.forward = (cosAngle > 0);

    angularCoeff = -sinAngle/cosAngle;
    lineDenom = cosAngle;
  } else {
    /* Iterate on the internal X (horizontal axis) */
    rot.integralNormalization = TYPE(1.0/absSinAngle);

    rotData.alongX = true;
    rotData.forward = !(sinAngle > 0);

    angularCoeff = -cosAngle/sinAngle;
    lineDenom = sinAngle;
  }

  const float_C sign = rotData.forward ? 1.0 : -1.0;
  if (rotData.alongX) {
    rotData.pointIncrement.x = sign*incr;
    rotData.pointIncrement.y = sign*incr*angularCoeff;
  } else {
    rotData.pointIncrement.x = sign*incr*angularCoeff;
    rotData.pointIncrement.y = sign*incr;
  }
  rot.increment = rotData.pointIncrement;

}

///////////////////////////////////////////////////////////////////////////////
// Private Methods

template <typename TYPE>
INLINE void
ScannerPhantom2D<TYPE>::fixRayEntrance(IterationData<TYPE>& data, const float_C& rayOffset)
{
  /* We want now to find the initial and final values of this ray on the circle
   * IMPORTANT: Coordinates in the ray's system of reference */
  const TYPE radiusActiveRegion = VoxelSelector<TYPE>::isIncoming ? VoxelSelector<TYPE>::rp.getRadiusActiveRegion() :
    VoxelSelector<TYPE>::rp.getRadiusActiveRegionForOutgoing();

  const float_C highExtY = CATHETUS(radiusActiveRegion, rayOffset);
  const float_C lowExtY  = -highExtY;

  /* Let's transform them to the matrix system of reference (Centered)*/
  ReferencedObject ro = data.rot.refSys;
  const Position_FC beginPoint =
      ro.toInternalCentered<float_C, float_C>(lowExtY, rayOffset);
  const Position_FC endPoint   =
      ro.toInternalCentered<float_C, float_C>(highExtY, rayOffset);

#ifdef DEBUG_SAMPLING
  cout << " rayOffset = " << rayOffset << endl; 
  cout << " begin Point = " << beginPoint.x << ", " << beginPoint.y << endl;
  cout << " end Point = " << endPoint.x << ", " << endPoint.y << endl;
  cout << " radiusActiveRegion = " << radiusActiveRegion << endl;
  cout << " lowExtY : " << lowExtY << endl;
#endif
  
  /* Let's fix the limits for the iteration: these limits will give a test for
   * stopping the iterations over the ray points. */
  data.limits.x = (beginPoint.x < endPoint.x)
      ? Range_D(beginPoint.x, endPoint.x) : Range_D(endPoint.x, beginPoint.x);
  data.limits.y = (beginPoint.y < endPoint.y)
      ? Range_D(beginPoint.y, endPoint.y) : Range_D(endPoint.y, beginPoint.y);

  /* To operate easily over the points, without caring about conditions on the
   * main axis, we define a reference to the independent and the dependent
   * coordinates */
  TYPE & indepCoord = data.rot.alongX ? data.getPosition().x : data.getPosition().y;
  TYPE & depCoord   = data.rot.alongX ? data.getPosition().y : data.getPosition().x;

  {
    /* let's now decide the initial point to the independent coordinate */
    Range_D & limitsIndep = (data.rot.alongX ? data.limits.x : data.limits.y);
    indepCoord = data.rot.forward ? limitsIndep.min : limitsIndep.max;
  }

  /* Fix the initial point to be aligned to the oversampling:
   * without oversampling it would be aligned to integral parts of the voxels'
   * positions. The oversampling just makes it possible to align to subintegral
   * parts, but to the incementr given by 1/oversampling */
  const float_C direction = (data.rot.forward ? 1 : -1);
  indepCoord += direction * fmod((TYPE)fabs(indepCoord), (TYPE)data.increment);
  depCoord = data.line(indepCoord);
}

template <typename TYPE>
INLINE void
ScannerPhantom2D<TYPE>::sampleLine( SubRay<TYPE> & subRay, IterationData<TYPE>& data)
{
  /// Note : for now (June 2016) this function is called only for the incoming ray.
  /// The outgoing ray will call sampleLineFromOriginAndDirection
# ifdef DEBUG_SAMPLING  
    cout << endl << "data = " << endl;
    data.printInfo(); 
#endif
  /* This method is the one that finally samples a ray on the circle
   * For every point it will sample the 4 nearest voxels, giving linear weights
   * based on the distance on the X and Y axes */
  const Range_D & limitsIndep = data.rot.alongX ? data.limits.x : data.limits.y;

  /* A shift in the system of reference to bring it to the C matrix system of
   * reference: [ -a, +a ] => [ 0, +2a ] to use rounded numbers as indexes */
  data.limits.x += VoxelSelector<TYPE>::semiX;
  data.limits.y += VoxelSelector<TYPE>::semiY;
  data.setPosition(Position_FC(data.getPosition().x+VoxelSelector<TYPE>::semiX, data.getPosition().y+VoxelSelector<TYPE>::semiY));

  /* Initialization of the initial position in the ray: it's needed to generate
   * all the others */
  subRay.initPosition = data.getPosition();

  const uint32_t numPoints =
      _FT_UI32(floor(limitsIndep.getLength()/data.increment));

  /* Buffer of positions: it's used to save positions in order to not
   * re-compute them in the following block */
  BinVec<Position<TYPE> > posVec;
  posVec.reserve(numPoints);

  /* Counting the points that can be sampled */
  for(; data.limits.contains(data.getPosition());)
  {
    /* Push this new position */
    posVec.push_back(data.getPosition());

    /* Next sample point */
    data.setPosition(data.getPosition() + data.rot.pointIncrement);
  }

# ifdef DEBUG_SAMPLING  
    cout << "data limits x = " << data.limits.x.min << ", " << data.limits.x.max << endl;
    cout << "data limits y = " << data.limits.y.min << ", " << data.limits.y.max << endl;
    cout << "should sample : " << posVec.size() << " point qt most " << endl;
    cout << "datapos : " << data.getPosition().x << ", " << data.getPosition().y << endl;
    cout << "increment : " << data.rot.pointIncrement.x << ", " << data.rot.pointIncrement.y << endl;
    cout << "semiX : " << VoxelSelector<TYPE>::semiX << ", semiY = " << VoxelSelector<TYPE>::semiY << endl;
#endif    

  /* Let's allocate enough place for sampling the voxels */
  subRay.reset((uint32_t)posVec.size());
  /* Sampling */
  typename BinVec<Position<TYPE> >::const_iterator posIt = posVec.begin();
  typename vector<RayPoint<TYPE> >::iterator itPoint = subRay.samplePointsBegin();
  while(posIt != posVec.end())
  {
    /* Get the next position from the buffer */
    const Position<TYPE> & pos = *posIt;
    /* Sample it! */
    if (VoxelSelector<TYPE>::selectVoxels(pos, itPoint->indexes, itPoint->weights, itPoint->getNbVoxelsSample() ) == 0){
      // remove one leement to the set of sample points
      subRay.setCurrentSize((uint32_t)subRay.size()-1);
    }else{
      ++itPoint;
      
    }
    // anyway go to the next position
    ++posIt;
  }

  /* Let's get them back to the real reference system
   * (we used the matrix reference system till now) */
  subRay.initPosition.x -= (TYPE)(VoxelSelector<TYPE>::semiX), subRay.initPosition.y -= (TYPE)(VoxelSelector<TYPE>::semiY);
  subRay.pointIncrement = data.rot.pointIncrement;
}


template<typename TYPE>
INLINE void
ScannerPhantom2D<TYPE>::sampleLineFromOriginAndDirection(SubRay<TYPE> &subRay, IterationData<TYPE> &data )
{
  /// Note : for now (June 2016) this function is called only for the outgoing ray.
  /// The incoming ray will call sampleLine

  /* This method is the one that finally samples a ray on the circle
   * For every point it will sample the 4 nearest voxels, giving linear weights
   * based on the distance on the X and Y axes */
  const Range_D & limitsIndep = data.rot.alongX ? data.limits.x : data.limits.y;

  /* A shift in the system of reference to bring it to the C matrix system of
   * reference: [ -a, +a ] => [ 0, +2a ] to use rounded numbers as indexes */
  data.limits.x += VoxelSelector<TYPE>::semiX;
  data.limits.y += VoxelSelector<TYPE>::semiY;
  data.setPosition(Position_FC(data.getPosition().x+VoxelSelector<TYPE>::semiX, data.getPosition().y+VoxelSelector<TYPE>::semiY));

  /* Initialization of the initial position in the ray: it's needed to generate
   * all the others */
  subRay.initPosition = data.getPosition();
  data.rot.forward = 1;

  const uint32_t numPoints =
      _FT_UI32(floor(limitsIndep.getLength()/data.increment));

  /* Buffer of positions: it's used to save positions in order to not
   * re-compute them in the following block */
  BinVec<Position<TYPE> > posVec;
  posVec.reserve(numPoints);

  /* Counting the points that can be sampled */
  for(; data.limits.contains(data.getPosition());)
  {
    /* Push this new position */
    posVec.push_back(data.getPosition());
    data.setPosition(data.getPosition() + data.rot.pointIncrement);
  }

  subRay.reset((uint32_t)posVec.size());

  /* Sampling */
  typename BinVec<Position<TYPE> >::iterator posIt = posVec.begin();
  typename BinVec<RayPoint<TYPE> >::iterator itPoint = subRay.samplePointsBegin();
  while(posIt != posVec.end())
  {
    /* Get the next position from the buffer */
    const Position<TYPE> & pos = *posIt;
    VoxelSelector<TYPE>::selectVoxels(pos, itPoint->indexes, itPoint->weights, itPoint->getNbVoxelsSample() );
    ++posIt;  
    ++itPoint;
    /* Sanity check test! (I should throw an exception) */
    if ( itPoint->getNbVoxelsSample() == 0 )  {
      const Position<TYPE> internal(pos - Position<TYPE>(-VoxelSelector<TYPE>::semiX, -VoxelSelector<TYPE>::semiY));
      ReferencedObject ro = data.rot.refSys;
      const Position<TYPE> external(
                ro.toExternalCentered<float_S,float_S>(internal));
      WarningPrintf(("Wrong Sampling Point: int( %3f, %3f ) ext( %3f, %3f )\n",
                      internal.x, internal.y, external.x, external.y));
    }

  }
  /* Let's get them back to the real reference system
   * (we used the matrix reference system till now) */
  subRay.initPosition.x -= TYPE(VoxelSelector<TYPE>::semiX), subRay.initPosition.y -= TYPE(VoxelSelector<TYPE>::semiY);
  subRay.pointIncrement = data.rot.pointIncrement;
}


//////////////// VoxelSelector implementation ////////////////////////

template <typename TYPE>
inline bool
VoxelSelector<TYPE>::saveVoxel(const float_C& iy, const float_C& ix, const TYPE& weight, 
  vector<uint32_t>& indexes, vector<TYPE>& weights, uint8_t& size  )
{
  const TYPE sqrRadAR = VoxelSelector<TYPE>::isIncoming ? 
    VoxelSelector<TYPE>::rp.getSquareRadiusActiveRegion() :
    VoxelSelector<TYPE>::rp.getSquareRadiusActiveRegionForOutgoing();

  /* If the point is within the circle area, let's push it */
  const TYPE delta_x = ix - VoxelSelector<TYPE>::semiX;
  const TYPE delta_y = iy - VoxelSelector<TYPE>::semiY;
  // TODO Henri : should be two points and them compute the distance between the two points
  if ( (SQUARE(delta_x) + SQUARE(delta_y) ) <= sqrRadAR) {

    uint32_t index = _FT_UI32(iy)*phantomWidth + _FT_UI32(ix);

#   ifdef DEBUG_SAMPLING    
      cout << "storing i = " << index << endl;
      cout << "storing w = " << weight << endl;
#   endif    

    indexes[size] = index;
    weights[size] = weight;
    size++;

    return true;
  }else{
    return false;
  }
}


template <typename TYPE>
INLINE uint8_t
VoxelSelector<TYPE>::selectVoxels( 
  const Position<TYPE> & pos, vector<uint32_t>& indexes, vector<TYPE>& weights, uint8_t& sizes )
{
#ifdef DEBUG_SAMPLING
  cout << "\n computeIndexesAndWeights" << endl;
  cout << " pos " << pos.x << ", " << pos.y << endl;
  cout << "phantomWidth" << phantomWidth << endl;
  cout << "phantomLength" << phantomLength << endl;
#endif
  const float_C voxelWidth = VOXEL_WIDTH;
  const float_C voxelLength = VOXEL_LENGTH;

  /* Sample the point:
   * first of all it finds the integral parts of the nearest points */
  float_C lowerX; 
  float_C lowerY; 

  const float_C pos_x_InVoxelWorld = pos.x * voxelWidth; 
  const float_C pos_y_InVoxelWorld = pos.y * voxelLength; 

  if(rp.getRayPointCalculationMethod() == withInterpolation){
    lowerX = std::floor(pos_x_InVoxelWorld);
    lowerY = std::floor(pos_y_InVoxelWorld);   
  }else{
    // in the case of interpolation we will take only one voxel to sample per point. So we need to round the value
    // to avoid bad mismatches
    lowerX = std::floor(pos_x_InVoxelWorld + 0.5);
    lowerY = std::floor(pos_y_InVoxelWorld + 0.5);
  }

  /* In principle I should use ceil(pos.x) and ceil(pos.y) but this should be
   * faster and safe since if the high weights are too low we are not going to
   * consider high points. The only case in which these two cannot be true is
   * when the high weights are exactly zero. */
  const float_C higherX = lowerX + voxelWidth;
  const float_C higherY = lowerY + voxelLength;

  if(rp.getRayPointCalculationMethod() == withoutInterpolation){
    if((lowerX>=0.0) && (lowerY>=0.0))
    {
      const float_C weight = WEIGHT(1.0, 1.0);
      return (unsigned int) saveVoxel(lowerY, lowerX, weight, indexes, weights, sizes );
    }else{
      return 0;
    }
  }else{
    uint8_t iSampleVoxel = 0;
    /* Then finds the weights of both the axes */
    const float_C hiXWeight = pos_x_InVoxelWorld - lowerX;
    const float_C hiYWeight = pos_y_InVoxelWorld - lowerY;
    const float_C loXWeight = voxelWidth - hiXWeight;
    const float_C loYWeight = voxelLength - hiYWeight;

    /* Simple idea: is to consider the 4 points separately */
    /* Changed the considered order to make it fit better in cache */
    /* Precompute, to skip some conditional jumps */
    const bool doHiX = hiXWeight > TOLL_COMP && higherX < phantomLength && higherX >= 0;
    const bool doHiY = hiYWeight > TOLL_COMP && higherY < phantomWidth && higherY >= 0;
    if (lowerY >= 0) {
      if (lowerX >= 0) {
        const float_C weight = WEIGHT(loXWeight, loYWeight);
        iSampleVoxel += (uint8_t)saveVoxel(lowerY, lowerX, weight, indexes, weights, sizes );
      }
      if (doHiX) {
        const float_C weight = WEIGHT(loYWeight, hiXWeight);
        iSampleVoxel += (uint8_t)saveVoxel(lowerY, higherX, weight, indexes, weights, sizes );
      }
    }
    if (doHiY) {
      if (lowerX >= 0) {
        const float_C weight = WEIGHT(hiYWeight, loXWeight);
        iSampleVoxel += (uint8_t)saveVoxel(higherY, lowerX, weight, indexes, weights, sizes );
      }
      if (doHiX) {
        const float_C weight = WEIGHT(hiYWeight, hiXWeight);
        iSampleVoxel += (uint8_t)saveVoxel(higherY, higherX, weight, indexes, weights, sizes );
      }
    }
    return iSampleVoxel;
  }
}


} // End of FreeART namespace
