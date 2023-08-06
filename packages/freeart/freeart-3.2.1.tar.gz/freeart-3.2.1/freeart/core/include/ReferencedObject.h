//+==================================================================================================================
//
// ReferencedObject.h
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
 * File:   ReferencedObject.h
 * Author: vigano
 *
 * Created on 7 octobre 2010, 17:59
 */

#ifndef REFERENCEDOBJECT_H
#define	REFERENCEDOBJECT_H

#include "GeometricTypes.h"
#include "BinaryVectors.h"

namespace FREEART_NAMESPACE
{

/**
 * Base class for reference systems
 */
class ReferencedObject {
protected:
  /**
   * The angle formed with the axes of another reference system
   */
  radians rotAngle;
  /**
   * Cosine of the angle
   */
  float_C cosAngle;
  /**
   * Sine of the angle
   */
  float_C sinAngle;
  /**
   * Absolute value of the cosine of the angle
   */
  float_C absCosAngle;
  /**
   * Absolute value of the sine of the angle
   */
  float_C absSinAngle;
  /**
   * Physical length of voxels
   */
  float_C voxelLength;
  /**
   * Physical width of voxels
   */
  float_C voxelWidth;

  float_C cosMulLength, cosMulWidth, sinMulLength, sinMulWidth;
  float_C cosDivLength, cosDivWidth, sinDivLength, sinDivWidth;

  void updateProspective() throw() {
    cosMulLength  = cosAngle*voxelLength;
    sinMulLength  = sinAngle*voxelLength;
    cosMulWidth = cosAngle*voxelWidth;
    sinMulWidth = sinAngle*voxelWidth;
    cosDivLength  = cosAngle/voxelLength;
    sinDivLength  = sinAngle/voxelLength;
    cosDivWidth = cosAngle/voxelWidth;
    sinDivWidth = sinAngle/voxelWidth;
  }

  // radians fromDegreesToRadians(const degrees & a) const throw() {
  //   return (a * M_PI / 180);
  // }

public:
  void printInfo() const
  {
    cout << "rot angle = " << rotAngle << endl;
  }  
  /**
   * Constructor
   *
   * @param a The angle formed with the reference system
   * @param vLength Physical length of voxels
   * @param vWidth Physical width of voxels
   */
  ReferencedObject( const radians & a, const float_C & vLength = 1.0,
                    const float_C & vWidth = 1.0)
    throw()
    : voxelLength(vLength), voxelWidth(vWidth)
  {
    setRotAngleRadians(a);
  }

  /**
   * Sets the physical sizes of the voxels
   *
   * @param vLength Physical length of voxels
   * @param vWidth Physical width of voxels
   */
  void setSize(const float_C & vLength, const float_C & vWidth) throw() {
    voxelLength = vLength;
    voxelWidth = vWidth;
    updateProspective();
  }

  /**
   * Angle given in radiant so we don't need to perform conversions
   * @param rad The angle in radiant
   */
  void setRotAngleRadians( const radians &rad ) throw() {
    rotAngle = rad;
    sinAngle = sin(rotAngle);
    cosAngle = cos(rotAngle);
    absSinAngle = fabs(sinAngle);
    absCosAngle = fabs(cosAngle);
    updateProspective();
  }

  /**
   * The angle is given in degrees, and converted in radians
   * Then it updates sine and cosine
   * @param degr
   */
  // void setRotAngleDegree( const degrees &degr ) throw() {
  //   setRotAngleRadians(fromDegreesToRadians(degr));
  // }

  const radians &getAngle() const throw() { return rotAngle; }
  const float_C &getSinAngle() const throw() { return sinAngle; }
  const float_C &getCosAngle() const throw() { return cosAngle; }
  const float_C &getAbsSinAngle() const throw() { return absSinAngle; }
  const float_C &getAbsCosAngle() const throw() { return absCosAngle; }

  const float_C &getvLength() const throw() { return voxelLength; }
  const float_C &getvWidth() const throw() { return voxelWidth; }

  /**
   * It changes the system of reference of the given components to the internal
   * and centered system of reference of the given ReferenceObject
   *
   * @param extY the value on the Y axis of the external system
   * @param extX the value on the X axis of the external system
   */
  template<typename TypeIn, typename TypeOut>
  const Position<TypeOut> toInternalCentered( const TypeIn &extY,
                                              const TypeIn &extX)
    const throw()
  {
    return Position<TypeOut>( (extX*cosDivLength - extY*sinDivWidth),
                              (extX*sinDivLength + extY*cosDivWidth) );
  }
  /**
   * It changes the system of reference of the given components to the internal
   * and centered system of reference of the given ReferenceObject
   *
   * @param ext the vector in the external system
   */
  template<typename TypeIn, typename TypeOut>
  const Position<TypeOut> toInternalCentered(const Position<TypeIn> & ext)
    const throw()
  {
    return Position<TypeOut>( (ext.x*cosDivLength - ext.y*sinDivWidth),
                              (ext.x*sinDivLength + ext.y*cosDivWidth) );
  }

  /**
   * It changes the system of reference of the given components to the external
   * and centered system of reference from the given ReferenceObject
   *
   * @param inY the value on the Y axis of the internal system
   * @param inX the value on the X axis of the internal system
   */
  template<typename TypeIn, typename TypeOut>
  const Position<TypeOut> toExternalCentered( const TypeIn &inY,
                                              const TypeIn &inX)
    const throw()
  {
    return Position<TypeOut>( + inX*cosMulLength + inY*sinMulWidth,
                              - inX*sinMulLength + inY*cosMulWidth );
  }

  /**
   * It changes the system of reference of the given components to the external
   * and centered system of reference from the given ReferenceObject
   *
   * @param in the vector in the internal system
   */
  template<typename TypeIn, typename TypeOut>
  const Position<TypeOut> toExternalCentered(const Position<TypeIn> & in)
    const throw()
  {
    return Position<TypeOut>( + in.x*cosMulLength + in.y*sinMulWidth,
                              - in.x*sinMulLength + in.y*cosMulWidth );
  }

  /**
   * It changes the system of reference of the given vector of components to the
   * external and centered system of reference from the given ReferenceObject
   * It's much faster when a vector of components need to be processed
   *
   * @param ext the vector in the extternal system
   * @param in the vector in the internal system
   */
  template<typename TypeIn, typename TypeOut>
  void toExternalCentered(const BinVec< Position<TypeIn> > & ext,
                          BinVec< Position<TypeOut> > & in)
    const throw()
  {
    /* Don't be scared by the typename keyword: it's just telling to the
     * compiler that the expression yelds a type, since we are passing a
     * template parameter of this function as template parameter to another
     * template. Nothing is illegal but must be declared! */
    typename BinVec<Position<TypeOut> >::iterator intern = in.begin();
    const typename BinVec<Position<TypeIn> >::const_iterator endPos = ext.end();
    for(typename BinVec< Position<TypeIn> >::const_iterator pos = ext.begin();
        pos != endPos; pos++, intern++)
    {
      intern->x = (TypeOut) (+ pos->x*cosMulLength + pos->y*sinMulWidth),
      intern->y = (TypeOut) (- pos->x*sinMulLength + pos->y*cosMulWidth);
    }
  }
};

} // End of FreeART namespace

#endif	/* REFERENCEDOBJECT_H */

