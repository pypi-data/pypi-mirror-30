//+==================================================================================================================
//
// Detector.h
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
 * File:   Detector.h
 * Author: vigano
 *
 * Created on 7 octobre 2010, 16:16
 */

#ifndef DETECTOR_H
#define	DETECTOR_H

#include "GeometricTypes.h"
#include "ReferencedObject.h"

#include <iostream>

namespace FREEART_NAMESPACE
{

#ifndef M_PI_2
# define M_PI_2 1.57079632679489661923
#endif

// #define DEBUG_SA

/**
 * Class representing the detector
 */
class Detector : public ReferencedObject {
protected:
  /**
   * It is meant from the center of the reference system
   */
  float_C distance;
public:
  Detector(const float_C &d, const radians & a) throw()
    : ReferencedObject(a), distance(d)
  { }
  const float_C &getDistance() const throw() { return distance; }
  void setDistance(const float_C & d) throw() { distance = d; }

  Position_FC getPosition() const throw() {
   return Position_FC(distance*sinAngle, distance*cosAngle);
  }

  Position_FC getPositionVersor() const throw() {
   return Position_FC(sinAngle, cosAngle);
  }
};

class DiffrDetector2D : public Detector {
protected:
  /**
   * It is the aperture angle of the ring of the diffraction pattern
   */
  const radians apertureAngle;
  const float_C cosApertAngle, sinApertAngle;
public:
  DiffrDetector2D(const float_C & d, const radians & a)
    : Detector(d, 0), apertureAngle(fabs(a))
    , cosApertAngle(cos(apertureAngle)), sinApertAngle(sin(apertureAngle))
  {
    CHECK_THROW((apertureAngle < M_PI_2),
              WrongArgException("Aperture angle cannot even reach 90 degrees"));
  }

  Position_FC getLeftDetectorPositionVersor() const throw() {
    return Position_FC(-sinApertAngle, +cosApertAngle);
  }
  Position_FC getRightDetectorPositionVersor() const throw() {
    return Position_FC(+sinApertAngle, +cosApertAngle);
  }

  Position_FC getLeftDetectorPosition() const throw() {
    return Position_FC(-distance*sinApertAngle, +distance*cosApertAngle);
  }
  Position_FC getRightDetectorPosition() const throw() {
    return Position_FC(+distance*sinApertAngle, +distance*cosApertAngle);
  }
};

/**
 * Class representing the detector, assuming a Circular Shape
 */
class FluoDetector : public Detector {
  /**
   * It assumes a circular shape
   */
  float_C surface;
  float_C radius;

public:
  /**
   * Explicit Constructor
   * @param r Radius
   * @param d Distance from the center of reference
   * @param a Angle between the s axis
   */
  FluoDetector(const float_C &r, const float_C &d, const radians &a ) throw()
    : Detector(d, a) { setRadius(r); }

  void setRadius(const float_C & r) throw() {
    radius = r, surface = M_PI * SQUARE(r);
  }
  void setSurface(const float_C & s) throw() {
    surface = s, radius = sqrt(s/M_PI);
  }

  const float_C &getRadius() const throw() { return radius; }
  const float_C &getSurface() const throw() { return surface; }

  radians getApertureAngle() const throw() {
    return atan2(distance, radius);
  }

  /**
   * This method computes the solid angle for the given point in respect to the
   * detector position
   * NOTE: Since we are in 2D, the detector will be a line.
   * NOTE: I'm also assuming that the correction from a flat line to a curved
   *       line is too small. This holds when the detector is much smaller than
   *       the distance from the point and the detector itself
   *
   * @param sampledPoint Position of the point that needs the solid angle
   */
  inline float_C getSolidAngle(const Position_FC & sampledPoint) const throw()
  {
    /* Vector from the given point to the detector */
    const Position_FC pointDist = getPosition() - sampledPoint;
    /* Quadratic norm that is also the square distance from the point and the
     * detector */
    const float_C pointQuadNorm = pointDist.quadNorm();

    /* the solid angle is now the area of the detector (the line lenght in 2D)
     * multiplied by the cosine of the angle between the normal to the surface
     * of the detector and the direction pointing from the point to the detector
     * All is then divided by the square distance between the point and the
     * detector.
//      * Omega = Area_detector * cos(alpha) / (distance)^2 */
#ifdef DEBUG_SA     
     cout << "sampled point = (" << sampledPoint.x << ", " << sampledPoint.y << ")" << endl;
     cout << "getposition = (" << getPosition().x << ", " << getPosition().y << ")" << endl;
     cout << "pointQuadNorm " << pointQuadNorm << ", rad = " << radius << endl;
     nbComputedSA++;
     cout << "nbComputedSA = " << nbComputedSA << endl;
     // return 1.0;
#endif
    return 0.5*(1-(sqrt(pointQuadNorm) / (sqrt(pointQuadNorm + radius*radius))));
  }

  /**
   * This method computes the solid angles for the given points in respect to
   * the detector position
   * NOTE: Since we are in 2D, the detector will be a line.
   * NOTE: I'm also assuming that the correction from a flat line to a curved
   *       line is too small. This holds when the detector is much smaller than
   *       the distance from the point and the detector itself
   *
   * @param sampledPoints Vector of positions that need the solid angles
   * @param pointsBuffer Buffer used to store modified positions
   * @param quadNormBuffer Buffer used to store data
   * @param normBuffer Buffer used to store data
   * @param solidAngles Destination where to put the angles
   */
  template<typename TypeIn, typename TypeOut>
  void solidAngles( const BinVec<Position<TypeIn> > & sampledPoints,
      BinVec<Position<TypeIn> > & pointsBuffer,
      BinVec<TypeOut> & quadNormBuffer, BinVec<TypeOut> & normBuffer,
      TypeOut * solidAngles )
    const throw()
  {
    /* Let's define these types for easiness of usage later
     * Again don't be afraid of typename keyword since it just says to the
     * compiler that the expression will be a type when we pass a template
     * argument as an argument to another template and try to get an iterator */
    typedef typename BinVec<Position<TypeIn> >::const_iterator InVecPos_ConstIt;
    typedef typename BinVec<Position<TypeIn> >::iterator       InVecPos_It;
    typedef typename BinVec<TypeOut>::const_iterator           OutVec_ConstIt;
    typedef typename BinVec<TypeOut>::iterator                 OutVec_It;

    /* Ends of the buffers */
    const InVecPos_ConstIt endPos = sampledPoints.end();
    const InVecPos_It  endBuffPos = pointsBuffer.end();
    const OutVec_ConstIt endQuadNorm = quadNormBuffer.end();
    const OutVec_ConstIt endNorm     = normBuffer.end();

    /* Constant detector positions (properly converted) */
    const Position<TypeIn> detPos = (Position<TypeIn>) getPosition();
    const Position<TypeIn> detVersPos = (Position<TypeIn>) getPositionVersor();

    /* First of all let's compute all the vectors that point from the given
     * points to the detector */
    InVecPos_It buff = pointsBuffer.begin();
    for(InVecPos_ConstIt pos = sampledPoints.begin();
        pos != endPos; pos++, buff++)
    {
      *buff = detPos - *pos;
    }

    /* Then let's compute some parameters like the norm and quad norm of those
     * vectors */
    OutVec_It quadNormBuff = quadNormBuffer.begin();
    OutVec_It normBuff     = normBuffer.begin();
    for(InVecPos_ConstIt pos = pointsBuffer.begin();
        pos != endBuffPos; pos++, quadNormBuff++, normBuff++)
    {
      *quadNormBuff = pos->quadNorm();
      *normBuff     = sqrt(*quadNormBuff);
    }
    /* We now scale all the previous vectors to obtain their versors */
    normBuff = normBuffer.begin();
    for(InVecPos_It pos = pointsBuffer.begin();
        pos != endBuffPos; pos++, normBuff++)
    {
      pos->x /= *normBuff, pos->y /= *normBuff;
    }
    /* We now get the cosine of the angle between the vectors pointing from the
     * given points to the detector and the direction normal to the surface of
     * the detector: this quantity is the scalar product between the versors */
    normBuff = normBuffer.begin();
    for(InVecPos_ConstIt pos = pointsBuffer.begin();
        pos != endBuffPos; pos++, normBuff++)
    {
      *normBuff = (pos->x * detVersPos.x + pos->y * detVersPos.y);
    }
    /* finally the solid angle will be the area of the detector divided by the
     * square of the distance from the points and multiplied by the cosine of
     * the angles */
    quadNormBuff = quadNormBuffer.begin();
    for(normBuff = normBuffer.begin(); normBuff != endNorm;
        normBuff++, quadNormBuff++, solidAngles++)
    {
      *solidAngles = 0.5*(1-(sqrt(*normBuff) / (sqrt(*quadNormBuff + radius*radius))));
    }
  }
};

} // End of FreeART namespace

#endif	/* DETECTOR_H */

