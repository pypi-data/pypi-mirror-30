//+==================================================================================================================
//
// GeometricTYPEs.h
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
 * File:   GeometricTYPEs.h
 * Author: vigano
 *
 * Created on 7 octobre 2010, 15:30
 */

#ifndef GEOMETRIC_TYPES_H_
#define	GEOMETRIC_TYPES_H_

#include <limits>
#include "macros.h"
#include "Exceptions.h"
#include <iostream>
#include "math.h"
#ifdef DEBUG
# include <sstream>
#endif

using namespace std;

namespace FREEART_NAMESPACE
{

#ifndef M_PI
# define M_PI 3.14159265358979323846
#endif

template<typename TYPE>
struct Position {
  TYPE x, y, z;

  Position() throw() : x(0), y(0), z(0) { }
  template<typename TYPE2>
  Position(const TYPE2 & _x,const TYPE2 & _y,const TYPE2 &_z=0) throw()
    : x( (TYPE)_x ), y( (TYPE)_y ),z( (TYPE)_z ) { }
  template<typename TYPE2>
  Position(const Position<TYPE2> & old) throw()
    : x( (TYPE)old.x ), y( (TYPE)old.y ), z( (TYPE)old.z ) { }

  static int isLessByX( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffX = prev.x - next.x;
    return (abs(diffX) > TOLL_COMP) ? (prev.x < next.x) : (prev.y < next.y);
  }
  static int isLessByY( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffY = prev.y - next.y;
    return (abs(diffY) > TOLL_COMP) ? (prev.y < next.y) : (prev.x < next.x);
  }
  static int isLessByZ( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffZ = prev.z - next.z;
    return (abs(diffZ) > TOLL_COMP) ? (prev.z < next.z) : (prev.z < next.z);
  }
  static int isMoreByX( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffX = prev.x - next.x;
    return (abs(diffX) > TOLL_COMP) ? (prev.x > next.x) : (prev.y > next.y);
  }
  static int isMoreByY( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffY = prev.y - next.y;
    return (abs(diffY) > TOLL_COMP) ? (prev.y > next.y) : (prev.x > next.x);
  }
  static int isMoreByZ( const Position<TYPE> & prev,
                        const Position<TYPE> & next)
  throw()
  {
    const TYPE diffZ = prev.z - next.z;
    return (abs(diffZ) > TOLL_COMP) ? (prev.z > next.z) : (prev.z > next.z);
  }
  TYPE operator*(const Position<TYPE> & other) const throw() {
    return (this->x*other.x + this->y*other.y + this->z*other.z);
  }
  template<typename TYPE2>
  Position<TYPE> operator*(const TYPE2 & scalar) const throw() {
    return Position<TYPE>(this->x*scalar, this->y*scalar, this->z*scalar);
  }
  template<typename TYPE2>
  Position<TYPE> operator/(const TYPE2 & scalar) const throw() {
    return Position<TYPE>(this->x/scalar, this->y/scalar, this->z/scalar);
  }
  template<typename TYPE2>
  Position<TYPE> operator+(const Position<TYPE2> & other) const throw() {
    return Position<TYPE>(this->x+(TYPE)other.x, this->y+(TYPE)other.y, this->z+(TYPE)other.z);
  }
  template<typename TYPE2>
  Position<TYPE> & operator+=(const Position<TYPE2> & other) throw() {
    this->x += (TYPE)other.x, this->y += (TYPE)other.y, this->z += (TYPE)other.z;
    return *this;
  }
  template<typename TYPE2>
  Position<TYPE> operator-(const Position<TYPE2> & other) const throw() {
    return Position<TYPE>(this->x-(TYPE)other.x, this->y-(TYPE)other.y, this->z-(TYPE)other.z);
  }
  template<typename TYPE2>
  Position<TYPE> & operator-=(const Position<TYPE2> & other) throw() {
    this->x -= other.x, this->y -= other.y, this->z -= other.z;
    return *this;
  }
  TYPE quadNorm() const throw() {
    return (SQUARE(x) + SQUARE(y) + SQUARE(z));
  }
  TYPE norm() const throw() {
    return sqrt(this->quadNorm());
  }
};

template<typename TYPE>
struct Position_2D {
  TYPE x, y;

  Position_2D() throw() : x(0), y(0) { }
  template<typename TYPE2>
  Position_2D(const TYPE2 & _x,const TYPE2 & _y) throw()
    : x( (TYPE)_x ), y( (TYPE)_y ) { }
  template<typename TYPE2>
  Position_2D(const Position_2D<TYPE2> & old) throw()
    : x( (TYPE)old.x ), y( (TYPE)old.y ) { }

  static int isLessByX( const Position_2D<TYPE> & prev,
                        const Position_2D<TYPE> & next)
  throw()
  {
    const TYPE diffX = prev.x - next.x;
    return (abs(diffX) > TOLL_COMP) ? (prev.x < next.x) : (prev.y < next.y);
  }
  static int isLessByY( const Position_2D<TYPE> & prev,
                        const Position_2D<TYPE> & next)
  throw()
  {
    const TYPE diffY = prev.y - next.y;
    return (abs(diffY) > TOLL_COMP) ? (prev.y < next.y) : (prev.x < next.x);
  }
  static int isMoreByX( const Position_2D<TYPE> & prev,
                        const Position_2D<TYPE> & next)
  throw()
  {
    const TYPE diffX = prev.x - next.x;
    return (abs(diffX) > TOLL_COMP) ? (prev.x > next.x) : (prev.y > next.y);
  }
  static int isMoreByY( const Position_2D<TYPE> & prev,
                        const Position_2D<TYPE> & next)
  throw()
  {
    const TYPE diffY = prev.y - next.y;
    return (abs(diffY) > TOLL_COMP) ? (prev.y > next.y) : (prev.x > next.x);
  }
  TYPE operator==(const Position_2D<TYPE> & other) const throw() {
    return (this->x==other.x && this->y==other.y);
  }  
  TYPE operator*(const Position_2D<TYPE> & other) const throw() {
    return (this->x*other.x + this->y*other.y);
  }
  template<typename TYPE2>
  Position_2D<TYPE> operator*(const TYPE2 & scalar) const throw() {
    return Position_2D<TYPE>(this->x*scalar, this->y*scalar);
  }
  template<typename TYPE2>
  Position_2D<TYPE> operator/(const TYPE2 & scalar) const throw() {
    return Position_2D<TYPE>(this->x/scalar, this->y/scalar);
  }
  template<typename TYPE2>
  Position_2D<TYPE> operator+(const Position_2D<TYPE2> & other) const throw() {
    return Position_2D<TYPE>(this->x+other.x, this->y+other.y);
  }
  template<typename TYPE2>
  Position_2D<TYPE> & operator+=(const Position_2D<TYPE2> & other) throw() {
    this->x += other.x, this->y += other.y;
    return *this;
  }
  template<typename TYPE2>
  Position_2D<TYPE> operator-(const Position_2D<TYPE2> & other) const throw() {
    return Position_2D<TYPE>(this->x-other.x, this->y-other.y);
  }
  template<typename TYPE2>
  Position_2D<TYPE> & operator-=(const Position_2D<TYPE2> & other) throw() {
    this->x -= other.x, this->y -= other.y;
    return *this;
  }
  TYPE quadNorm() const throw() {
    return (SQUARE(x) + SQUARE(y));
  }
  TYPE norm() const throw() {
    return sqrt(this->quadNorm());
  }

  static Position_2D<TYPE> getOrigin() { return Position_2D<TYPE>((TYPE)0.0, (TYPE)0.0);}

};

template<typename TYPE>
struct Vector_2D : Position_2D<TYPE> 
{
  TYPE x, y;
  TYPE dot(const Vector_2D& v2) const{
    return x*v2.x + v2.y*y;
  }

  Vector_2D(TYPE _x, TYPE _y):
    x(_x), y(_y)
  {}

  void normalize(){
    TYPE length = getLength();
    x /= length;
    y /= length;
  }

  TYPE getLength() const {
    return sqrt(x*x+y*y);
  }

  // return the signed angle between V2 and this vector
  TYPE getSignedAngle(const Vector_2D& v2){
      return fmod(atan2(v2.y, v2.x) - atan2(y, x), (2.0*M_PI) );
  }
};

typedef Position<uint32_t> Position_UI32;
typedef Position<float_C>  Position_FC;
typedef Position<float_S>  Position_FS;

typedef Position<uint32_t> Dimensions_UI32;

template<class TYPE>
struct Range {
  TYPE min, max;

  Range(const TYPE & _min, const TYPE & _max) : min(_min), max(_max)
  {
    CHECK_THROW((min <= max),
        InitializationException("Minimum is higher than maximum"));
  }

  static Range<TYPE> getMaxRange() throw() {
    /* It could just be: numeric_limits<int>, since we will work on a small
     * range */
    return Range<TYPE>(numeric_limits<TYPE>::min(),numeric_limits<TYPE>::max());
  }

  const TYPE getLength() const throw() { return (max-min+1); }

  template<typename TYPE2>
  bool contains(const Range<TYPE2> & range) const throw() {
    return (min <= range.min && max >= range.max);
  }
  template<typename TYPE2>
  bool contains(const TYPE2 & pos) const throw() {
    return (min <= pos && max >= pos);
  }
  template<typename TYPE2>
  Range<TYPE> operator-(const TYPE2 & scalar) const throw() {
    return Range<TYPE>( (TYPE) (this->min-scalar), (TYPE) (this->max-scalar));
  }
  template<typename TYPE2>
  Range<TYPE> operator-=(const TYPE2 & scalar) throw() {
    this->min -= scalar; this->max -= scalar;
    return *this;
  }
  template<typename TYPE2>
  Range<TYPE> operator+(const TYPE2 & scalar) const throw() {
    return Range<TYPE>(this->min+scalar, this->max+scalar);
  }
  template<typename TYPE2>
  Range<TYPE> operator+=(const TYPE2 & scalar) throw() {
    this->min += scalar; this->max += scalar;
    return *this;
  }
  template<typename TYPE2>
  Range<TYPE> enlarge(const TYPE2 & scalar) const throw() {
    return Range<TYPE>(this->min-scalar, this->max+scalar);
  }
};

typedef Range<int32_t> Range_I32;
typedef Range<float_C> Range_D;

template<class TYPE>
struct Range2D {
  Range<TYPE> x;
  Range<TYPE> y;

  Range2D(const Range<TYPE> & _x, const Range<TYPE> & _y) : x(_x), y(_y) { }

  static Range2D<TYPE> getMaxRange() throw() {
    return Range2D<TYPE>(Range<TYPE>::getMaxRange(),Range<TYPE>::getMaxRange());
  }
  const TYPE getSurface() const throw() { return x.getLength()*y.getLength(); }
  const Position_FC getCenter() const throw() {
    return Position_FC( x.min + (x.getLength())/2, y.min + (x.getLength())/2 );
  }

  template<typename TYPE2>
  bool contains(const Position<TYPE2> & pos) const throw() {
    return (x.contains(pos.x) && y.contains(pos.y));
  }
  template<typename TYPE2>
  bool contains(const Range2D<TYPE2> & range) const throw() {
    return (x.contains(range.x) && y.contains(range.y));
  }
};

typedef Range2D<int32_t> Range2D_I32;
typedef Range2D<float_C> Range2D_D;

} // End of FreeART namespace

#endif	/* GEOMETRIC_TYPES_H_ */

