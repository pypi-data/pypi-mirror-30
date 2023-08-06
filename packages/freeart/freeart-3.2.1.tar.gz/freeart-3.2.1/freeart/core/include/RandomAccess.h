//+==================================================================================================================
//
// RandomAccess.h
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
 * File:   RandomAccess.h
 * Author: vigano
 *
 * Created on October 18, 2010, 10:16 AM
 */

#ifndef RANDOMACCESS_H
#define	RANDOMACCESS_H

#include "GeometryTable.h"
#include <algorithm>

namespace FREEART_NAMESPACE
{

/**
 * Class for accessing pseudo-randomly to a vector
 */
class RandomAccessMng : public vector<size_t> {

private:
  /// seedToZero : True if we want to reshuffle at each reset. Can be turn off to make sure unit test
  /// or some experimentation are repeatable
  bool seedToZero;

public:
  /**
   * Constructor
   *
   * @param length Number of pseudo random elements
   */
  RandomAccessMng(const size_t & length):
   seedToZero(true) 
  {
    reset(length);
  }
  /**
   * Re initializes the vector to a new length and re shuffling it.
   *
   * @param length Number of pseudo random elements
   */
  void reset(const size_t & length) {
    this->resize(length);
    this->reShuffle();
  }
  /**
   * Re shuffles the vector
   */
  void reShuffle() {
    const size_t & length = size();
    for(size_t i1 = 0; i1 < length; i1++) {
      (*this)[i1] = i1;
    }
    if(seedToZero){
      srand(0);
    }
    random_shuffle(this->begin(), this->end());
  }

  /**
   * Do we want to turn off the shuffle to make sure no random elent wil be taken into account.
   * @param b
   */
  void setSeedToZero(bool b){ seedToZero = b;}
};

} // End of FreeART namespace

#endif	/* RANDOMACCESS_H */

