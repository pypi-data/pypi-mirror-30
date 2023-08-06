//+==================================================================================================================
//
// LookupTable.h
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
 * LookupTable.h
 *
 *  Created on: Jan 20, 2011
 *      Author: vigano
 */

#ifndef LOOKUPTABLE_H_
#define LOOKUPTABLE_H_

#include "macros.h"
#include "Exceptions.h"
# include <sstream>
# include <iterator>
# include <iostream>
 
namespace FREEART_NAMESPACE
{


/**
 * Class that manages the offsets (for indices) of the given rays and rotation 
 * initial points in the storage C vectors of the incoming loss fraction
 */
 //TODO  Henri : remove the template here
template <typename TYPE>
class LookupTable {
  uint32_t totRots;
  uint32_t totRays_perRot;
  uint32_t * ray_offsets;

#ifdef DEBUG
  void checkBoundaries(const uint32_t & numRot, const uint32_t & numRay) const;
#endif
public:
  LookupTable() throw()
    : totRots(0), totRays_perRot(0), ray_offsets(NULL)
  { }
  LookupTable( const uint32_t & _rots, const uint32_t & _rays) throw()
    : totRots(_rots), totRays_perRot(_rays), ray_offsets(NULL)
  {
    const uint32_t tot_offsets = totRays_perRot * _rots + _rays;
    ray_offsets = new uint32_t[tot_offsets];
  }
  ~LookupTable() {
    DESTROY_C_ARRAY(ray_offsets);
  }
  void reset(const uint32_t & _rots, const uint32_t & _rays) throw()
  {
    DESTROY_C_ARRAY(ray_offsets);
    totRots = _rots;
    totRays_perRot = _rays;
    const uint32_t tot_offsets = totRays_perRot * _rots + _rays;
    ray_offsets = new uint32_t[tot_offsets];
  }

  uint32_t & getRayOffset( const uint32_t & numRot,
                              const uint32_t & numRay)
  {
    DEBUG_CHECK( checkBoundaries(numRot, numRay) );
    return ray_offsets[ totRays_perRot*numRot + numRay];
  }

  const uint32_t & getRayOffset(const uint32_t & numRot,
                                const uint32_t & numRay)
    const
  {
    DEBUG_CHECK( checkBoundaries(numRot, numRay) );
    return ray_offsets[ totRays_perRot*numRot + numRay];
  }
  const uint32_t getRotOffset( const uint32_t & numRot) const
  {
    DEBUG_CHECK( checkBoundaries(numRot, 0) );
    return ray_offsets[totRays_perRot*numRot];
  }

#ifdef DEBUG
  void printTable() const;
#endif
};

//////////////////// TEMPLATe FUNCTION IMPLEMENTATION ///////////////////////////

#ifdef DEBUG

template <typename TYPE>
void
LookupTable<TYPE>::checkBoundaries( const uint32_t & numRot,
                              const uint32_t & numRay)
  const
{
  CHECK_THROW(ray_offsets,
              NotInitializedObjException("Not initialized ray offsets vector"));
  CHECK_THROW(totRots,
              NotInitializedObjException("Not initialized TotRotations"));
  CHECK_THROW(totRays_perRot,
              NotInitializedObjException("Not initialized TotRays_perRot"));

  if (numRot >= totRots) {
    stringstream stream;
    stream  << "Out of boundaries for rotation: " << numRot+1 << ", max rot: "
            << totRots;
    throw OutOfBoundException(stream.str());
  }
  if (numRay >= totRays_perRot) {
    stringstream stream;
    stream  << "Out of boundaries for ray: " << numRay+1
              << ", max ray: " << totRays_perRot << "\n"
            << "in rotation: " << numRot+1 << ", max rot: " << totRots;
    throw OutOfBoundException(stream.str());
  }
}

template <typename TYPE>
void
LookupTable<TYPE>::printTable() const
{
  ostream_iterator< uint32_t > output( cout, " " );
  cout << "Lookup Table:\n";
  for (uint32_t numRot = 0; numRot < totRots; numRot++) {
    cout << " Rot: " << numRot+1 << "\n";
    uint32_t * begin = ray_offsets+(numRot*totRays_perRot);
    copy(begin, begin+totRays_perRot, output);
    cout << "\n";
  }
}

#endif


} // End of FreeART namepsace

#endif /* LOOKUPTABLE_H_ */
