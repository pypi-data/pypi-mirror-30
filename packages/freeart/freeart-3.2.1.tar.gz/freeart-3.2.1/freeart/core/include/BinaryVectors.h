//+==================================================================================================================
//
// BinaryVectors.h
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
 * BinaryVectors.h
 *
 *  Created on: Nov 30, 2010
 *      Author: vigano
 */

#ifndef BINARYVECTORS_H_
#define BINARYVECTORS_H_

#include <vector>
#include "GeometricTypes.h"
#include <iostream>
#include <cmath>

using namespace std;

namespace FREEART_NAMESPACE
{


//////////////////////////////////////////
// Bloat Classes
//////////////////////////////////////////

/**
 * Base class for the binary vectors. They are general purpose extensions of
 * the STL vector class. They can in principle be useful in replacing C vectors
 * The overhead is negligible if used just like C vectors (accessing through
 * iterators or directly to the data with pointers: data is supposed to be
 * stored contiguously in memory)
 */
template<typename Type>
class BinVec : public vector<Type> {
protected:
  /**
   * Default value for the elements in the array
   */
  Type defaultValue;

#if defined(DEBUG)
  /**
   * Boundary checking function
   *
   * @param index the index to check
   */
  void checkBoundaries(const size_t &index) const
  {
    // cout << " checking " << index << endl;
    // cout << " size of struct : " << this->size() << endl;
    if ( (index >= this->size()) ) {
      stringstream stream;
      stream  << "Out of boundaries for cardinal point: " << index+1 << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
public:
  /* Don't be afraid of typenames: they just make it again visible the nested
   * typedef in the inherited template */
  typedef typename std::vector<Type>::const_reference const_reference;
  typedef typename std::vector<Type>::reference       reference;
  typedef typename std::vector<Type>::const_iterator  const_iterator;
  typedef typename std::vector<Type>::iterator        iterator;

  /**
   * Constructor
   *
   * @param length (Optional) specifies the initial size of the vector
   * @param init (Optional) specifies the default value for the elements
   */
  BinVec(const size_t & length = 0, const Type & init = Type())
    : vector<Type>(length, init), defaultValue(init)
  {

  }
  /**
   * Resets the elements of the vector to the default value
   */
  void clean() throw() {
    for(iterator i1 = this->begin(); i1 != this->end(); i1++) {
      *i1 = defaultValue;
    }
  }
  /**
   * Sets a new default value for the array
   *
   * @param init The new default value
   */
  void setDefaultValue(const Type & init) { defaultValue = init; }

  ///////////////////////////////////////////////////////////////////////////
  // Wrapper methods to make the interface similar to the one of the BinVec2D
  ///////////////////////////////////////////////////////////////////////////

  /**
   * Resets the vector to a new size and initializes it to the default value
   *
   * @param _length The new length of the vector
   */
  void reset(const size_t & _length)
  {
    this->resize(_length, defaultValue);
    // Depend de l ordre d operation. Le reset n est jamais utilise pour le moment
    // car a chaque fois on cree un nouveau rayon.
    // On pourrait en avoir besoin si on ne creai pas de nouveaux rayons a chaue fois.
    // Serai une tres bonne optimization a mon avis. Avoir un RayPool que l on reinitialize
    // et que l on garde pour chaque rotation
    this->clean();
  }

  /**
   * Const getter method (with boundary checks when compiled in debug mode)
   *
   * @param index the index of the element to get
   */
  const_reference get(const size_t &index) const
  {
    DEBUG_CHECK( checkBoundaries(index) );
    return (*this)[index];
  }
  /**
   * Getter method (with boundary checks when compiled in debug mode)
   *
   * @param index the index of the element to get
   */
  reference get(const size_t &index)
  {
    DEBUG_CHECK( checkBoundaries(index) );
    return (*this)[index];
  }
};
typedef BinVec<float_C>  BinVec_FC;
typedef BinVec<float_S>  BinVec_FS;
typedef BinVec<uint32_t> BinVec_UI32;
typedef BinVec<size_t>   BinVec_Size_t;
typedef BinVec<uint8_t>  BinVec_UI8;

/**
 * Very complex data structure that is a 2D binary vector where the rows are
 * different binary vectors allocated when requested. You can specify a
 * different class for the rows' container class but in principle it needs to
 * expose at least the same interface of a BinVec.
 *
 * A nice example is the Sinogram (2D) class that uses as Slice class (row container)
 * SinogramProj that is a derived template class of the base BinVec.
 *
 * Without specifying the container for the slices BinVec is chosen by default
 */
template<typename Type, template<typename Type2> class SliceType = BinVec >
class PointedBinVec2D : public vector< SliceType<Type> *> {
  /**
   * Length of the rows (slices)
   */
  size_t length;
  /**
   * Default value for the elements in the slices
   */
  Type defaultValue;
#ifdef DEBUG
  /**
   * Boundary checking function
   *
   * @param ix the index of the row (slice)
   * @param iy the index of the element to select in the row
   */
  void checkBoundaries(const size_t & ix, const size_t & iy) const
  {
    if ( (ix >= this->size()) || (iy >= length) ) {
      stringstream stream;
      stream  << "Out of boundaries for point: ( " << ix+1 << ", " << iy+1 << ")"
              << ", vector size: (" << length << ", " << this->size() << ")"
              << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
  /**
   * Inherited resizing method, hidden to enforce the use of the reset method
   */
  using std::vector< SliceType<Type>* >::resize;
public:
  void print() const{
    for(unsigned int iX = 0; iX < this->size(); iX++){
      for(unsigned int iY = 0; iY < (*this)[iX].size(); iY ++ ){
        cout << (*(*this)[iX])[iY] << endl;
      }
    }
  }
  /* Don't be afraid of typenames: they just make it again visible the nested
   * typedef in the inherited template */
  typedef typename std::vector<Type>::const_reference const_reference;
  typedef typename std::vector<Type>::reference       reference;

  /**
   * Constructor
   *
   * @param _l length of the rows (slices)
   * @param init default value for the elements in the slices
   */
  PointedBinVec2D(const size_t & _l = 0, const Type & init = Type())
    : length(_l), defaultValue(init) { }
  /**
   * Destructor: it removes all the rows
   */
  ~PointedBinVec2D() {
    this->reset(0);
  }
  /**
   * Allocates new rows (slices) pushing them in the bottom
   *
   * @param totNum Number of the new rows (slices) to allocate
   */
  void allocateNewRows(const size_t & totNum)
  {
    CHECK_THROW(length, NotInitializedObjException(
        "Tried to allocate a new row before giving a valid length"));
    this->reserve(this->size() + totNum);
    for(size_t num = 0; num < totNum; num++) {
      this->push_back( new SliceType<Type>(length, defaultValue) );
    }
  }
  /**
   * Resetting method. Cleans and changes the number of rows (slices). It may also
   * change the length of the rows
   *
   * @param numOfRows The number of the rows (slices) after resetting
   * @param _length (Optional) the new length for the rows
   */
  void reset(const size_t numOfRows, const size_t & _length = 0) {
    for(size_t i = 0; i < this->size(); i++) {
      delete (*this)[i];
    }
    this->clear();

    if (_length) {
      length = _length;
    }
    if (numOfRows) {
      this->allocateNewRows(numOfRows);
    }
  }
  /**
   * Sets a new default value for the array
   *
   * @param init The new default value
   */
  void setDefaultValue(const Type & init) { defaultValue = init; }

  /**
   * Returns the length of the rows
   */
  const uint32_t getLength() const throw() { return (uint32_t) length; }
  /**
   * Returns the number of rows (slices)
   */
  uint32_t getWidth() const throw() { return (uint32_t) this->size(); }

  /**
   * Const getter method (with boundary checks when compiled in debug mode)
   *
   * @param ix the row (slice) to select
   * @param iy the index of the element in the row
   */
  const_reference get(const size_t &ix, const size_t &iy) const
  {
    DEBUG_CHECK( checkBoundaries(ix, iy) );
    return (*(*this)[ix])[iy];
  }
  /**
   * Getter method (with boundary checks when compiled in debug mode)
   *
   * @param ix the row (slice) to select
   * @param iy the index of the element in the row
   */
  reference get(const size_t &ix, const size_t &iy)
  {
    DEBUG_CHECK( checkBoundaries(ix, iy) );
    return (*(*this)[ix])[iy];
  }

  void set(const size_t &ix, const size_t &iy, reference newVal)
  {
    (*(*this)[ix])[iy] = newVal;
  }
};
typedef PointedBinVec2D<float_C > PointedBinVec2D_D;
typedef PointedBinVec2D<float_S > PointedBinVec2D_FS;


/**
 * The main bidimensional array type. It usually contains matrices around in the code.
 */
template<typename Type>
class BinVec2D : public BinVec<Type> {
  /**
   * Slice length (X axis)
   */
  size_t length;
  /**
   * Slice width (Y axis)
   */
  size_t width;

#if defined(DEBUG)
  /**
   * Boundary checking function
   *
   * @param ix the inedx of element in the row
   * @param iy the row to select
   */
  void checkBoundaries(const size_t &ix, const size_t &iy) const
  {
    if ( (iy >= width) || (ix >= length) ) {
      stringstream stream;
      stream  << "Out of boundaries for point: ( " << ix+1 << ", "
                << iy+1 << ")\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
public:
  /* Don't be afraid of typenames: they just make it again visible the nested
   * typedef in the inherited template */
  typedef typename BinVec<Type>::const_reference const_reference;
  typedef typename BinVec<Type>::reference       reference;
  typedef typename BinVec<Type>::const_iterator  const_iterator;
  typedef typename BinVec<Type>::iterator        iterator;

  /**
   * Constructor
   *
   * @param _length (Optional) length of the rows
   * @param _width (Optional) width of the slice
   * @param init (Optional) default value for the elements in the slices
   */
  BinVec2D( const size_t & _length = 0, const size_t & _width = 0,
            const Type & init = Type())
    : BinVec<Type>(_length*_width, init), length(_length),width(_width)
  {
    this->clean();
  }
  /**
   * Constructor
   *
   * @param dims Is a struct containing both slice width and length
   * @param init (Optional) default value for the elements in the slices
   */
  template<typename Type2>
  BinVec2D(const Position<Type2> & dims, const Type & init = Type())
    : BinVec<Type>(_FT_UI32(dims.x)*_FT_UI32(dims.y), init)
    , length(_FT_UI32(dims.x)), width(_FT_UI32(dims.y))
  {
    this->clean();
  }
  /**
   * Resetting method: it changes the shape of the vector and cleans the values
   *
   * @param _length new slice length
   * @param _width new slice width
   */
  void reset(const size_t & _length, const size_t & _width)
  {
    length = _length;
    width = _width;
    this->resize(length*width);
    this->clean();
  }
  /**
   * Copies the values from the given matrix eventually checking for constrains
   * on the negativity.
   *
   * @param matr The matrix with the new values
   * @param nonNegativity A boolean telling whether checking for it or not
   */
  template<typename Type2>
  void setValues( const BinVec2D<Type2> & matr,
                  const bool & nonNegativity = false)
  {
    /* Don't be afraid of typenames: they just make it again visible the nested
     * typedef in the inherited template */
    typedef typename std::vector<Type2>::const_iterator  type2_const_iterator;

    CHECK_THROW(length == matr.getLength(),
        WrongArgException("Slice has not the same length"));
    CHECK_THROW(width == matr.getWidth(),
        WrongArgException("Slice has not the same width"));

    type2_const_iterator itNewVals = matr.begin();
    const iterator & endMatrix = this->end();
    for(iterator itMatrix = this->begin(); itMatrix != endMatrix;
        itMatrix++, itNewVals++)
    {
      *itMatrix = (Type) *itNewVals;
    }
    if (nonNegativity) {
      for(iterator itMatrix = this->begin(); itMatrix != endMatrix; itMatrix++)
      {
        if (*itMatrix < 0) { *itMatrix = 0; }
      }
    }
  }
  /**
   * Sums the values from the given matrix to the corresponding ones in this
   * matris, eventually checking for constrains on the negativity.
   *
   * @param matr The matrix with the new values
   * @param nonNegativity A boolean telling whether checking for it or not
   */
  template<typename Type2>
  void setCorrections(const BinVec2D<Type2> & matr,
                      const bool & nonNegativity = false)
  {
    /* Don't be afraid of typenames: they just make it again visible the nested
     * typedef in the inherited template */
    typedef typename std::vector<Type2>::const_iterator  type2_const_iterator;

    CHECK_THROW(length == matr.getLength(),
        WrongArgException("Slice has not the same length"));
    CHECK_THROW(width == matr.getWidth(),
        WrongArgException("Slice has not the same width"));

    /* We use iterators in order to be faster: there are no order needs */
    type2_const_iterator itNewVals = matr.begin();
    const iterator & endMatrix = this->end();
    for(iterator itMatrix = this->begin(); itMatrix < endMatrix;
        itMatrix++, itNewVals++)
    {
      *itMatrix += (Type) *itNewVals;
    }
    if (nonNegativity) {
      for(iterator itMatrix = this->begin(); itMatrix < endMatrix; itMatrix++)
      {
        if (*itMatrix < 0) { *itMatrix = 0; }
      }
    }
  }

  const size_t &getLength() const throw() { return length; }
  const size_t &getWidth() const throw() { return width; }

  /**
   * Makes it again visible the getter method from the inherited class, since
   * we are then going to overload the same functions, and the compiler thinks
   * we are overriding them!
   */
  using BinVec<Type>::get;

  /**
   * Const double indexed getter
   * (with boundary checks when compiled in debug mode)
   *
   * @param ix the index of the element in the row (length)
   * @param iy the row to select (width)
   */
  const_reference get(const size_t &ix, const size_t &iy) const
  {
    DEBUG_CHECK( checkBoundaries(ix, iy) );
    return (*this)[iy*length + ix];
  }
  /**
   * Double indexed getter (with boundary checks when compiled in debug mode)
   *
   * @param ix the index of the element in the row (length)
   * @param ix the row to select (width)
   */
  reference get(const size_t &ix, const size_t &iy)
  {
    DEBUG_CHECK( checkBoundaries(ix, iy) );
    return (*this)[iy*length + ix];
  }

  /**
   * Const double indexed getter
   * (with boundary checks when compiled in debug mode)
   *
   * @param pos A structure containing the components of the needed point
   */
  const_reference get(const Position_UI32 &pos) const
  {
    return get(pos.x, pos.y);
  }
  /**
   * Double indexed getter (with boundary checks when compiled in debug mode)
   *
   * @param pos A structure containing the components of the needed point
   */
  reference get(const Position_UI32 &pos)
  {
    return get(pos.x, pos.y);
  }

  /**
   * Returns the maximum element of the matrix, using the comparator of the
   * objects in the array.
   */
  const Type max() const {
    CHECK_THROW( (length*width),
        NotInitializedObjException("The object has 0 dimension"));

    const Type * maximum = &(*this)[0];
    for(const_iterator value = this->begin(); value != this->end(); value++) {
      if (*value > *maximum) {
        maximum = &(*value);
      }
    }
    return *maximum;
  }

  /**
   * Returns the maximum element of the matrix, in respect the given member of
   * the underlying structure in the array.
   *
   * @param memb The pointer to the member in the structure
   */
  template<typename Member>
  const Type max(Member memb) const {
    CHECK_THROW( (length*width),
        NotInitializedObjException("The object has 0 dimension"));

    const Type * maximum = &(*this)[0];
    for(const_iterator value = this->begin(); value != this->end(); value++) {
      if ( (*value).*memb > (*maximum).*memb ) {
        maximum = &(*value);
      }
    }
    return *maximum;
  }

  /**
   * Divides all the elements of the matrix by the given value
   *
   * @param value The value that will divide all the elements
   */
  template<typename Type2>
  void divideBy(const Type2 & value) {
    CHECK_THROW((length*width),
        NotInitializedObjException("The object has 0 dimension"));
    for(iterator item = this->begin(); item != this->end(); item++) {
      (*item) /= value;
    }
  }
  /**
   * Divides a given member of all the elements of the matrix by the given value
   *
   * @param value The value that will divide all the elements
   * @param memb The pointer to the member in the structure
   */
  template<typename TypeMemb, typename Member>
  void divideBy(const TypeMemb & value, Member memb) {
    CHECK_THROW((length*width),
        NotInitializedObjException("The object has 0 dimension"));
    for(iterator item = this->begin(); item != this->end(); item++) {
      (*item).*memb /= value;
    }
  }

  /**
   * Comparison method that tells whether two matrices have the same shape
   *
   * @param other the other matrix
   */
  template<typename Type2>
  bool haveEqualDimensions(const BinVec2D<Type2> & other) const {
    return ((this->getLength() == other.getLength())
              && (this->getWidth() == other.getWidth()));
  }
};
typedef BinVec2D<float_C>  BinVec2D_D;
typedef BinVec2D<float_S>  BinVec2D_FS;
typedef BinVec2D<bool>     BinVec2D_B;
typedef BinVec2D<uint32_t> BinVec2D_UI32;


/**
 * The main tridimensional array type. It usually contains volumes around in the code.
 */
template<typename Type>
class BinVec3D : public BinVec<Type> {
  /**
   * Length of the volume (on X axis)
   */
  size_t length;
  /**
   * Width of the volume (on Y axis)
   */
  size_t width;
  /**
   * Height of the volume (on Z axis)
   */
  size_t height;

#if defined(DEBUG)
  /**
   * Boundary checking function
   *
   * @param ix the index of the element in the length
   * @param iy the index of the element in the width
   * @param iz the index of the element in the height
   */
  void checkBoundaries(const size_t &ix, const size_t &iy,const size_t &iz) const
  {
    if ( (iy >= width) || (ix >= length) || (iz >= height)) {
      stringstream stream;
      stream  << "Out of boundaries for point: ( " << ix+1 << ", " << iy+1 << ", " << iz+1 << ")\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
public:
 /* Don't be afraid of typenames: they just make it again visible the nested
   * typedef in the inherited template */
  typedef typename BinVec<Type>::const_reference const_reference;
  typedef typename BinVec<Type>::reference       reference;
  typedef typename BinVec<Type>::const_iterator  const_iterator;
  typedef typename BinVec<Type>::iterator        iterator;

  /**
   * Constructor
   *
   * @param _length (Optional) length of the volume (X axis)
   * @param _width (Optional) width of the volume (Y axis)
   * @param _height (Optional) height of the volume (Z axis)
   * @param init (Optional) default value for the elements in the slices
   */
  BinVec3D( const size_t & _length = 0, const size_t & _width = 0, const size_t &_height = 0,
            const Type & init = Type())
    : BinVec<Type>(_length*_width*_height,init), length(_length), width(_width),height(_height)
  {
    this->clean();
  }
  /**
   * Constructor
   *
   * @param dims Is a struct containing both length, width and height
   * @param init (Optional) default value for the elements in the volume
   */
  template<typename Type2>
  BinVec3D(const Position<Type2> & dims, const Type & init = Type())
    : BinVec<Type>(_FT_UI32(dims.x)*_FT_UI32(dims.y)*_FT_UI32(dims.z), init)
    , length(_FT_UI32(dims.x)), width(_FT_UI32(dims.y)), height(_FT_UI32(dims.z))
  {
    this->clean();
  }
  /**
   * Resetting method: it changes the shape of the vector and cleans the values
   *
   * @param _length new volume length
   * @param _width new volume width
   * @param _height new volume height
   */
  void reset(const size_t & _length, const size_t & _width,const size_t &_height)
  {
    length = _length;
    width = _width;
    height = _height;
    this->resize(length*width*height);
    this->clean();
  }
  /**
   * Copies the values from the given volume eventually checking for constrains
   * on the negativity.
   *
   * @param vol The volume with the new values
   * @param nonNegativity A boolean telling whether checking for it or not
   */
  template<typename Type2>
  void setValues( const BinVec3D<Type2> & vol,
                  const bool & nonNegativity = false)
  {
    /* Don't be afraid of typenames: they just make it again visible the nested
     * typedef in the inherited template */
    typedef typename std::vector<Type2>::const_iterator  type2_const_iterator;

    CHECK_THROW(length == vol.getLenth(),
        WrongArgException("Volume does not have the same length"));
    CHECK_THROW(width == vol.getWidth(),
        WrongArgException("Volume does not have the same width"));
    CHECK_THROW(height == vol.getHeight(),
        WrongArgException("Volume does not have the same height"));

    type2_const_iterator itNewVals = vol.begin();
    const iterator & endVol = this->end();
    for(iterator itVol = this->begin(); itVol != endVol;
        itVol++, itNewVals++)
    {
      *itVol = (Type) *itNewVals;
    }
    if (nonNegativity) {
      for(iterator itVol = this->begin(); itVol != endVol; itVol++)
      {
        if (*itVol < 0) { *itVol = 0; }
      }
    }
  }
  /**
   * Sums the values from the given volume to the corresponding ones in this
   * volume, eventually checking for constrains on the negativity.
   *
   * @param vol The matrix with the new values
   * @param upperLimit If different than infinity, all values greater than upperLimit will be set to upperLimit
   * @param lowerLimit If different than -infinity, all values lower than lowerLimit will be set to lowerLimit
   */
  template<typename Type2>
  void setCorrections(const BinVec3D<Type2> & vol,
                      Type2 upperLimit,
                      Type2 lowerLimit)
  {
    /* Don't be afraid of typenames: they just make it again visible the nested
     * typedef in the inherited template */
    typedef typename std::vector<Type2>::const_iterator  type2_const_iterator;

    CHECK_THROW(length == vol.getLength(),
        WrongArgException("Volume does not have the same length"));
    CHECK_THROW(width == vol.getWidth(),
        WrongArgException("Volume does not have the same width"));
    CHECK_THROW(height == vol.getHeight(),
        WrongArgException("Volume does not have the same height"));

    /* We use iterators in order to be faster: there are no order needs */
    type2_const_iterator itNewVals = vol.begin();
    const iterator & endVol = this->end();
    for(iterator itVol = this->begin(); itVol < endVol;
        itVol++, itNewVals++)
    {
      *itVol += (Type) *itNewVals;
    }
#ifdef _MSC_VER
    int _i_lowerInf = _finite(lowerLimit);
    int _i_upperInf = _finite(upperLimit);

    bool lowerInf = false;
    bool upperInf = false;

    if (_i_lowerInf == 0)
        lowerInf = true;

    if (_i_upperInf == 0)
        upperInf = true;
#else
    bool lowerInf = std::isinf(lowerLimit);
    bool upperInf = std::isinf(upperLimit);
#endif
    if (upperInf == false || lowerInf == false) {
      for(iterator itVol = this->begin(); itVol < endVol; itVol++)
      {
         if (upperInf == false) {
            if (*itVol > upperLimit) {*itVol = upperLimit;}
         }
         if (lowerInf == false) {
            if (*itVol < lowerLimit) {*itVol = lowerLimit;}
         }
      }
    }
  }


  uint32_t getLength() const throw() { return (uint32_t)length; }
  uint32_t getWidth() const throw() { return (uint32_t)width; }
  uint32_t getHeight() const throw() { return (uint32_t)height; }

  Dimensions_UI32 getMatrDims() const {return Dimensions_UI32(this->getLength(), this->getWidth(), this->getHeight());} 
  /**
   * Makes it again visible the getter method from the inherited class, since
   * we are then going to overload the same functions, and the compiler thinks
   * we are overriding them!
   */
  using BinVec<Type>::get;

  /**
   * Const double indexed getter
   * (with boundary checks when compiled in debug mode)
   *
   * @param ix the index of the element in the length (X axis)
   * @param iy the index of the element in the width (Y axis)
   * @param iz the index of the element in the height (Z axis)
   */
  const_reference get(const size_t &ix, const size_t &iy,const size_t &iz) const
  {
    DEBUG_CHECK( checkBoundaries(ix, iy, iz) );
    return (*this)[iz*length*width + iy*length + ix];
  }
  /**
   * Double indexed getter (with boundary checks when compiled in debug mode)
   *
   * @param ix the index of the element in the length (X axis)
   * @param iy the index of the element in the width (Y axis)
   * @param iz the index of the element in the height (Z axis)
   */
  reference get(const size_t &ix, const size_t &iy, const size_t &iz)
  {
    DEBUG_CHECK( checkBoundaries(ix, iy, iz) );
    return (*this)[iz*length*width + iy*length + ix];
  }

  /**
   * Const double indexed getter
   * (with boundary checks when compiled in debug mode)
   *
   * @param pos A structure containing the components of the needed point
   */
  const_reference get(const Position_UI32 &pos) const
  {
    return get(pos.x, pos.y, pos.z);
  }
  /**
   * Double indexed getter (with boundary checks when compiled in debug mode)
   *
   * @param pos A structure containing the components of the needed point
   */
  reference get(const Position_UI32 &pos)
  {
    return get(pos.x, pos.y, pos.z);
  }

  /**
   * Returns the maximum element of the volume, using the comparator of the
   * objects in the array.
   */
  const Type max() const {
    CHECK_THROW( (length*width*height),
        NotInitializedObjException("The object has 0 dimension"));

    const Type * maximum = &(*this)[0];
    for(const_iterator value = this->begin(); value != this->end(); value++) {
      if (*value > *maximum) {
        maximum = &(*value);
      }
    }
    return *maximum;
  }

  /**
   * Returns the maximum element of the volume, in respect the given member of
   * the underlying structure in the array.
   *
   * @param memb The pointer to the member in the structure
   */
  template<typename Member>
  const Type max(Member memb) const {
    CHECK_THROW( (length*width*height),
        NotInitializedObjException("The object has 0 dimension"));

    const Type * maximum = &(*this)[0];
    for(const_iterator value = this->begin(); value != this->end(); value++) {
      if ( (*value).*memb > (*maximum).*memb ) {
        maximum = &(*value);
      }
    }
    return *maximum;
  }

  /**
   * Divides all the elements of the matrix by the given value
   *
   * @param value The value that will divide all the elements
   */
  template<typename Type2>
  void divideBy(const Type2 & value) {
    CHECK_THROW((length*width*height),
        NotInitializedObjException("The object has 0 dimension"));
    for(iterator item = this->begin(); item != this->end(); item++) {
      (*item) /= value;
    }
  }
  /**
   * Divides a given member of all the elements of the matrix by the given value
   *
   * @param value The value that will divide all the elements
   * @param memb The pointer to the member in the structure
   */
  template<typename TypeMemb, typename Member>
  void divideBy(const TypeMemb & value, Member memb) {
    CHECK_THROW((length*width*height),
        NotInitializedObjException("The object has 0 dimension"));
    for(iterator item = this->begin(); item != this->end(); item++) {
      (*item).*memb /= value;
    }
  }

  /**
   * Comparison method that tells whether two matrices have the same shape
   *
   * @param other the other matrix
   */
  template<typename Type2>
  bool haveEqualDimensions(const BinVec3D<Type2> & other) const {
    return ((this->getLength() == other.getLength())
               && (this->getWidth() == other.getWidth())
               && (this->getHeight() == other.getHeight()));
  }
};
typedef BinVec3D<float_C>  BinVec3D_D;
typedef BinVec3D<float_S>  BinVec3D_FS;
typedef BinVec3D<bool>     BinVec3D_B;
typedef BinVec3D<uint32_t> BinVec3D_UI32;

/**
 * Vector class specialized in containing angles
 */
class AnglesArray : public BinVec<radians> {
public:
  /**
   * Constructor
   *
   * @param _size length of the array
   */
  AnglesArray(const size_t & _size) : BinVec<radians>(_size) { }
  /**
   * Default constructor
   */
  AnglesArray() { }

  /**
   * Function that for the given number or rotations and the minimum and maximum
   * angles, fills the array with equispaced values.
   */
  void setFixedSpaceAngles( const size_t & totRot, const radians & minAngle,
                            const radians & maxAngle)
  {
    CHECK_THROW(totRot, InitializationException("Number of rotations is 0"));
    this->resize(totRot);
    if (totRot > 1) {
      for(size_t rot = 0; rot < totRot; rot++) {
        const radians angle = minAngle
            + radians(rot) / radians(totRot -1) * (maxAngle-minAngle);
        operator[](rot) = angle;
      }
    } else {
      operator[](0) = minAngle;
    }
  }

  void print() const {
    cout << "print angle array " << endl; 
    for(AnglesArray::const_iterator it = this->begin(); it != this->end(); ++it){
      cout << " " << *it << endl;
    }
  }

  // void toDegree() {
  //   for(AnglesArray::iterator it = this->begin(); it != this->end(); ++it){
  //     *it *= 180/M_PI;
  //   }
  // }

};

} // End of FreeART namespace

#endif /* BINARYVECTORS_H_ */
