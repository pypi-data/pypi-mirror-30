//+==================================================================================================================
//
// GeometryStructures.h
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
 * File:   GeometryStructures.h
 * Author: vigano
 *
 * Created on October 18, 2010, 12:02 PM
 *
 * Refactoring 05/2016.
 *    Adding structs StraightLine, Line_2D, Circle_2D to increase readebility
 *
 * Refactoring 07/2016. 
 *    Rotation is no more heriting from vector<Ray>
 *    Because we want to light the memory allocation we will now allocate one set of rays 
 *    with the maximal size and use it for each rotation which will update it at each new rotation
 *    Author : payno
 *
 */

#ifndef GEOMETRYSTRUCTURES_H
#define	GEOMETRYSTRUCTURES_H

#include "Ray.h"
 #include <assert.h>

#ifdef DEBUG
# include "Exceptions.h"
# include <sstream>
#endif

namespace FREEART_NAMESPACE
{
template <typename TYPE>
class Rotation {
#ifdef DEBUG
  void checkBoundary(const size_t & index) const {
    if (index >= this->size()) {
      stringstream stream;
      stream  << "Out of boundaries for rotation: " << index << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif

public:

  /*
   * The set of ray used for this rotation
   */
  vector<Ray<TYPE> >& rays; 

  /**
   * Angle of the rotation
   */
  radians angle;

  /**
   * Used to normalize the line integral
   */
  TYPE integralNormalization;

  /**
   * Increment from one point and the next
   */
  Position<TYPE> increment;

  /**
   * Number of total sampled points in this rotation
   */
  unsigned int totSampledPoints;


  /**
   * Constructor, creates a new rotation, given the rotation angle
   * @param _a Rotation angle in degrees
   */
  Rotation(const radians & _a, vector<Ray<TYPE> >& _rays) : 
    rays(_rays), angle(_a), integralNormalization(1), totSampledPoints(0)
  {

  }

  /**
   * Const getter for the given ray number
   * @param numRay Cardinal number of the ray to select
   * @return a const reference to the selected ray
   */
  const Ray<TYPE> & getRay(const size_t & numRay) const
  {
    assert(numRay >= 0);
    assert(numRay < rays.size());
    return rays[numRay];
  }

  /**
   * Getter for the given ray number
   * @param numRay Cardinal number of the ray to select
   * @return a reference to the selected ray
   */
  Ray<TYPE> & getRay(const size_t & numRay)
  {
    assert(numRay >= 0);
    assert(numRay < rays.size());
    return rays[numRay];
  }

  typename vector<Ray<TYPE> >::const_iterator begin() const {return rays.begin();}
  typename vector<Ray<TYPE> >::iterator begin() {return rays.begin();}
  typename vector<Ray<TYPE> >::const_iterator end() const { return rays.end(); }
  typename vector<Ray<TYPE> >::iterator end() { return rays.end(); }
};

class StraightLine {
  float_C coeff;
  float_C offset;
public:
  StraightLine(const float_C & _coeff, const float_C & _offset) throw()
    : coeff(_coeff), offset(_offset) { }

  float_C operator()(const float_C &indip) const throw() {
    return (coeff * indip + offset);
  }

  const float_C &getCoeff() const throw() { return coeff; }
  const float_C &getOffset() const throw() { return offset; }
};

/*
 * a simple line structure. 
 * The line is defined by an origin and a direction
 */

template<typename TYPE>
struct Line_2D
{
  Position_2D<TYPE> origin;  // The origin of the line
  Vector_2D<TYPE> direction; // The direction of the line
  /**
   * Constructor
   */
  Line_2D(Position_2D<TYPE> _origin, Vector_2D<TYPE> _direction):
    origin(_origin), direction(_direction)
  {
    direction.normalize();
  }
};

// a simple Circle structure
template<typename TYPE>
struct Circle_2D
{
  Position_2D<TYPE> center;  // < the center of the circle
  TYPE radius;      // < the radius of the circle
  /**
   * Constructor
   */
  Circle_2D(Position_2D<TYPE> _center, TYPE _radius):
    center(_center), radius(_radius)
  {

  }
  /**
   * Return the square of the circle radius
   */
  TYPE getSquareRadius() { return radius*radius;}

  vector<Position_2D<TYPE> > getIntersections(const Line_2D<TYPE>& line){
    vector<Position_2D<TYPE> > res;
    // particular case when the line origin and the circle origin are at the same position
    if(this->center == line.origin){
      res.push_back(Position_2D<TYPE>(line.direction.x * this->radius, line.direction.y * this->radius)); 
      res.push_back(Position_2D<TYPE>(-line.direction.x * this->radius, -line.direction.y * this->radius)); 
      return res;
    }

    Vector_2D<TYPE> v_origins(line.origin.x-this->center.x, line.origin.y-this->center.y);
    v_origins.normalize();

    TYPE a = line.direction.dot(line.direction);
    TYPE b = v_origins.dot(line.direction);
    TYPE c = v_origins.dot(v_origins) - this->getSquareRadius();

    TYPE delta = sqrt(b*b -a*c);

    // if no interscetion between the circle and the line
    if(delta < 0.0){
      return res;
    }

    // if only one intersection
    if(delta == 0.0){
      Position_2D<TYPE> interPoint(line.direction.x * (-b/a) + line.origin.x, line.direction.y * (-b/a) + line.origin.y);
      res.push_back( interPoint );
    }else{
      // WARNING : always let this intersection first in the vector of solutions. Remove one costly test in fixRayExit function
      Position_2D<TYPE> inter1((line.direction.x * (-b+delta/a) + line.origin.x ), (line.direction.y * (-b+delta/a) + line.origin.y));
      res.push_back( inter1  );
      Position_2D<TYPE> inter2((line.direction.x * (-b-delta/a) + line.origin.x ), (line.direction.y * (-b-delta/a) + line.origin.y));
      res.push_back( inter2 );
    }
    return res;
  }
};


} // End of FreeART namespace

#endif	/* GEOMETRYSTRUCTURES_H */

