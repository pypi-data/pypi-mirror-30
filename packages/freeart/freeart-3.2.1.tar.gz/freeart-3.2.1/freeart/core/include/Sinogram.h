//+==================================================================================================================
//
// Sinogram.h
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
 * Sinogram.h
 *
 *  Created on: Nov 29, 2010
 *      Author: vigano
 */

#ifndef SINOGRAM_H_
#define SINOGRAM_H_

#include "BinaryVectors.h"

#include <iostream>

namespace FREEART_NAMESPACE
{

//////////////////////////////////////////
// Sinogram Classes
//////////////////////////////////////////

template<typename Type>
class GenericSinogramProj : public BinVec<Type> {
#ifdef DEBUG
  void checkBoundaries(const size_t & numRay) const
  {
    if (numRay >= this->size()) {
      stringstream stream;
      stream  << "Out of boundaries for point: " << numRay
              << ", slice size: " << this->size()
              << ", slice angle: " << this->angle
              << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
public:
  void print() const {
    cout << endl;
    for(typename BinVec<Type>::const_iterator it = this->begin(); it != this->end(); ++it){
      Type v = (*it);
      cout << v;
    }
    cout << endl;
  }  
  GenericSinogramProj(const size_t & width = 0, const Type & init = Type())
    : BinVec<Type>(width, init)
  { }

  radians angle;

  const Type & getPoint(const size_t & numRay) const
  {
    DEBUG_CHECK( checkBoundaries(numRay) );
    return (*this)[numRay];
  }
  Type & getPoint(const size_t & numRay)
  {
    DEBUG_CHECK( checkBoundaries(numRay) );
    return (*this)[numRay];
  }
};

template<typename Precision>
class GenericSinogram : public PointedBinVec2D<Precision, GenericSinogramProj> {
#ifdef DEBUG
  void checkBoundaries(const size_t & numRotation) const
  {
    if (numRotation >= this->size()) {
      stringstream stream;
      stream  << "Out of boundaries for rotation: " << numRotation
              << ", sinogram size: " << this->size() << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
public:
  void print() const{
    for(typename PointedBinVec2D<Precision, GenericSinogramProj>::const_iterator it = this->begin(); it != this->end(); ++it ){
      (*it)->print();
    }
  }
  void setFixedSpaceAngles(const radians & minAngle, const radians & maxAngle)
  {
    const size_t & sinoSize = this->size();
    AnglesArray array;
    array.setFixedSpaceAngles(sinoSize, minAngle, maxAngle);
    for(size_t angle = 0; angle < sinoSize; angle++) {
      getRotation(angle).angle = array[angle];
    }
  }

  const GenericSinogramProj<Precision> & getRotation(const size_t &rotationNum) const
  {
    DEBUG_CHECK( this->checkBoundaries(rotationNum) );
    return *(*this)[rotationNum];
  }

  GenericSinogramProj<Precision> & getRotation(const size_t &rotationNum)
  {
    DEBUG_CHECK( this->checkBoundaries(rotationNum) );
    return *(*this)[rotationNum];
  }

  const Precision & getPoint(const size_t &rotationNum, const size_t &pointNum) const
  {
    return getRotation(rotationNum).getPoint(pointNum);
  }

  Precision & getPoint(const size_t &rotationNum, const size_t &pointNum)
  {
    return getRotation(rotationNum).getPoint(pointNum);
  }
};

typedef GenericSinogramProj<float_S>  SinogramProj;
typedef GenericSinogram<float_S>      Sinogram;

/* We do not use inheritance for this class. Using inheritance, we should inherit from class PointedBinvec3D
   class which is a class with a template template template parameter!
   This makes the stuff quite complicated.
   In order to keep things understandable even the morning just after one evening spent downtown in pubs, we
   simply use a data member of class vector<GenericSinogram<T> > */

template<typename Precision>
class GenericSinogram3D {
#ifdef DEBUG
  void checkBoundaries(const size_t & numSlice,const size_t numRotation) const
  {
    if (numSlice >= theSlices.size() || numRotation >= theSlices[0]->size()) {
      stringstream stream;
      stream  << "Out of boundaries for slice: " << numSlice << ", rotation: " << numRotation
              << ", sinogram size: slices " << theSlices.size() << ", rotation " << theSlices[0]->size() << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif

    vector<GenericSinogram<Precision> *> theSlices;

public:

    void print() const {
      cout << "nbSlices = " << theSlices.size() << endl;
      typename vector<GenericSinogram<Precision> *>::const_iterator itSlice;
      for(itSlice = theSlices.begin(); itSlice != theSlices.end(); ++itSlice){
        (*itSlice)->print();
      }
    }
  void reset(const size_t numSlice, const size_t & numRotation = 0, const size_t & numPoint = 0)
  {
    if (theSlices.empty() == false)
    {
        for(size_t i = 0; i < theSlices.size(); i++)
        {
          delete theSlices[i];
        }
        theSlices.clear();
    }

    for (size_t i=0;i < numSlice;i++)
    {
        theSlices.push_back(new GenericSinogram<Precision>());
        theSlices.back()->reset(numRotation,numPoint);
    }
  }

  size_t size() const {return theSlices.size();}
  size_t getSliceNb() const {return size();}
  size_t getRotNb() const {return theSlices[0]->size();}
  size_t getLength() const { return theSlices[0]->getLength(); }
  size_t getRayNb() const {return getLength();}

  const GenericSinogramProj<Precision> & getRotation(const size_t &sliceNum, const size_t &rotationNum) const
  {
    DEBUG_CHECK( this->checkBoundaries(sliceNum,rotationNum) );
    return *(*theSlices[sliceNum])[rotationNum];
  }

  GenericSinogramProj<Precision> & getRotation(const size_t & sliceNum,const size_t &rotationNum)
  {
    DEBUG_CHECK( this->checkBoundaries(sliceNum,rotationNum) );
    GenericSinogram<Precision>  &gs = *(theSlices[sliceNum]);
    GenericSinogramProj<Precision> &gsp = *(gs[rotationNum]);
    return gsp;
  }

  const Precision & getPoint(const size_t sliceNum,const size_t &rotationNum, const size_t &pointNum) const
  {
    return theSlices[sliceNum]->getRotation(rotationNum).getPoint(pointNum);
  }

  Precision & getPoint(const size_t &sliceNum, const size_t &rotationNum, const size_t &pointNum)
  {
    return theSlices[sliceNum]->getRotation(rotationNum).getPoint(pointNum);
  }

  double getAngle(const size_t sliceNum,const size_t rotationNum)
  {
    return theSlices[sliceNum]->getRotation(rotationNum).angle;
  }
};

#ifdef USER_DOC
/**
 * Class representing a sinogram
 *
 * This class is used to store a sinogram in memory
 *
 * @headerfile FreeART.h
 */

class Sinogram
{
public:
  /**
   * Default Sinogram class constructor
   */
    Sinogram();
};
#endif

} // End of FreeART namespace

#endif /* SINOGRAM_H_ */
