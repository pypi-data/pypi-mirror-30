// //+==================================================================================================================
// //
// // RayHelpers.h
// //
// //
// // Copyright (C) :      2014,2015
// //						European Synchrotron Radiation Facility
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

// /*
//  * RayHelpers.h
//  *
//  *  Created on: Feb 2, 2011
//  *      Author: vigano
//  */

#ifndef RAYHELPERS_H_
#define RAYHELPERS_H_

#include "Ray.h"
 
#include <iostream>
#include <assert.h>

using namespace std;

namespace FREEART_NAMESPACE
{

// ///////////////////////////////////////////////////////////////////////////////
// // Ray Iterators //////////////////////////////////////////////////////////////
// ///////////////////////////////////////////////////////////////////////////////

/**
 * Base Ray iterator class
 */
template< typename lrayPtsIter, typename TYPE>
class PartialRayBaseIterator {
//protected:
public:
  /**
   * iterator pointing to the initial value of the points sampled by the ray
   */
  lrayPtsIter points;

  /**
   * End of the sample points vector
   */
  lrayPtsIter endPoints;

  /**
   * Moves to the next point all the iterators
   */
  void shiftPartialBase() throw() {
    // const uint8_t & shift = *(this->sizes)++;
    // indexes += shift, weights += shift;
    points++;
  }

public:
  PartialRayBaseIterator( lrayPtsIter _points, lrayPtsIter _end_points)
    : points(_points), endPoints(_end_points)
  { }

  /**
   * Public advancing operator that moves to next point
   */
  PartialRayBaseIterator & operator++(int) throw() {
    shiftPartialBase();
    return *this;
  }

  /**
   * It returns the addres of the index of the initial voxel in the list of the
   * sampled voxels for the pointed point
   */
  const uint32_t * getIndexesList() const throw() { return &points->indexes; }
  /**
   * It returns the addres of the weight of the initial voxel in the list of the
   * sampled voxels for the pointed point
   */
  const TYPE *  getWeightsList() const throw() { return &points->weights; }


  /**
   * Test condition that tells if the iterator reached the end of the ray
   */
  bool isEnd() const throw() { return (points == endPoints); }
 
};

/**
 * Base class for the iterators that report also the poisition of the points
 */
template< typename lrayPtsIter, typename posType, typename TYPE>
class RayBaseIterator
  : public PartialRayBaseIterator<lrayPtsIter, TYPE>
{
protected:
  /**
   * Position of the pointed point
   */
  posType position;
  /**
   * IOncrement from one position and the following
   */
  const posType increm;
public:
  RayBaseIterator(lrayPtsIter _points, lrayPtsIter _end_points, posType _pos, posType _incr)
    : PartialRayBaseIterator<lrayPtsIter, TYPE>( _points, _end_points)
    , position(_pos), increm(_incr)
  { }
  /**
   * Iterator advancing method that also increments the position
   */
  RayBaseIterator & operator++(int) throw() {
    this->shiftPartialBase(); 
    position += increm;
    return *this;
  }
  /**
   * Returns the position of the pointed point
   */
  const Position<TYPE> & getPosition() const throw() { return this->position; }
};

////////////////////////////////////////////////////////////////////////////////
// Derived Iterator classes for real usage
////////////////////////////////////////////////////////////////////////////////

template <typename TYPE>
class SubRayIterator
  : public RayBaseIterator< typename vector<RayPoint<TYPE> >::iterator, Position<TYPE>, TYPE>
{
public:
  SubRayIterator(SubRay<TYPE> & _subray, const Position<TYPE> & _increment)
    : RayBaseIterator<typename vector<RayPoint<TYPE> >::iterator,
                      Position<TYPE>, TYPE >
        ( _subray.samplePointsBegin(), _subray.samplePointsEnd(),
          _subray.initPosition, _increment )
  { }
};

template <typename TYPE>
class ConstSubRayIterator
  : public RayBaseIterator< typename vector<RayPoint<TYPE> >::const_iterator,
                            Position<TYPE>,
                            TYPE >
{
public:
  ConstSubRayIterator(const SubRay<TYPE> & _subray, const Position<TYPE> & _increment)
    : RayBaseIterator<typename vector<RayPoint<TYPE> >::const_iterator,
                      Position<TYPE>,
                      TYPE >
        ( _subray.samplePointsBegin(), _subray.samplePointsEnd(),
          _subray.initPosition, _increment )
  { }
};


} // End of FreeART namespace

#endif /* RAYHELPERS_H_ */
