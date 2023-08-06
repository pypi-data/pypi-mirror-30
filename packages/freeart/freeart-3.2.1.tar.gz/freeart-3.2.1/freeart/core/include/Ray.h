//+==================================================================================================================
//
// Ray.h
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
 * File:   Ray.h
 * Author: vigano
 *
 * Created on October, 2010
 *
 * June 2016 : Refactoring : Adding RayPoint to group informations
 *     and simplify the comprehension of this. 
 * Author: payno
 *
 * July 2016 : Refactoring : Rotation class is no more heriting from a vector of Ray. This was to 
 *   heavy to allocate all the memory each time for this large number of Ray and RayPoint (or previously vector of indexes and weights).
 *   So to avoid that we are createing only one set of Ray that will be used reused by each Rotation.
 *   Note : as reauested this has been thaught for a reconstruction/projection manageing in a single thread. We can 
 *      deal with multiple reconstruction so long that they all have their own GeometryTable and incomingRays / outgoingRays vectors
 *      deal with in concurency (If we had an optimization and deal with several Rotation of the same reconstruction at the same time
 *      this will fail).
 * Author: payno
 */

#ifndef RAY_H
#define RAY_H

#include "BinaryVectors.h"
#include <assert.h>

namespace FREEART_NAMESPACE
{

/// This structure reprensents a point sample by the ray
template <typename TYPE>
struct RayPoint{
public: 
  /// The number of voxel sample by this point
  uint8_t nbVoxelsSample;

  /**
   * Indexes of the sampled voxels
   */
  // uint32_t* indexes;
  vector<uint32_t> indexes;
  /**
   * Weights associated to the indexes of the sampled voxels
   */
  // TYPE* weights;  
   vector<TYPE> weights;

  /// Constructor
  /// @param maxPoint : the maxima; number of voxel the point can sample to compute her value
  RayPoint(uint8_t maxPoint) : 
    nbVoxelsSample(0) {
    resize(4);
  }

  /// Destructor
  ~RayPoint() {
  };

  /// Resize of the RayPoinit
  inline void resize(uint8_t maxPoint){
    indexes = vector<uint32_t>(maxPoint);
    weights = vector<TYPE>(maxPoint);
    nbVoxelsSample = 0;
  }

  /// Reset the ray point.
  /// Note : reset is a simple set to 0 ofthe number of sample voxel (aka nbVoxelSample).
  /// We don t want to affect indexes and weights or resize them to be faster.
  /// So we ensure that they will be overwrite
  inline void reset(){
    nbVoxelsSample = 0;
  }

  /// Return the number of voxel sampled by this point
  uint8_t& getNbVoxelsSample() { return nbVoxelsSample;}
  const uint8_t& getNbVoxelsSample() const { return nbVoxelsSample;}

  /**
   * It returns the addres of the index of the initial voxel in the list of the
   * sampled voxels for the pointed point
   */
  const uint32_t * getIndexesList() const throw() { return &indexes[0]; }
  /**
   * It returns the addres of the weight of the initial voxel in the list of the
   * sampled voxels for the pointed point
   */
  const TYPE *  getWeightsList() const throw() { return &weights[0]; }


  /// Return the sum of the square weight
  TYPE getSquareWeightSum() const throw() {
    switch (nbVoxelsSample) {
      case 4: {
        return weights[0] * weights[0]
            +  weights[1] * weights[1]
            +  weights[2] * weights[2]
            +  weights[3] * weights[3];
      }
      case 2: {
        return weights[0] * weights[0]
            +  weights[1] * weights[1];
      }
      case 3: {
        return weights[0] * weights[0]
            +  weights[1] * weights[1]
            +  weights[2] * weights[2];
      }
      case 1: {
        return weights[0] * weights[0];
      }
      default: {
        return 0;
      }
    }
  }

  /// Return the value of the RayPoint from
  /// the voxel indexes sample and the given volum (vol)
  INLINE TYPE getMeanField(const BinVec3D<TYPE> &vol) const throw() {
    switch (nbVoxelsSample) {
      case 4: {
        if(vol.size() <= indexes[0]){
          cout << "vol.size() " << vol.size() << endl;
          cout << "indexes[0] " << indexes[0] << endl;
        }
        assert(vol.size() > indexes[0] );
        assert(vol.size() > indexes[1] );
        assert(vol.size() > indexes[2] );
        assert(vol.size() > indexes[3] );
        return vol.get(indexes[0]) * weights[0]
            +  vol.get(indexes[1]) * weights[1]
            +  vol.get(indexes[2]) * weights[2]
            +  vol.get(indexes[3]) * weights[3];
      }
      case 2: {
        if(vol.size() <= indexes[0]){
          cout << "vol.size() " << vol.size() << endl;
          cout << "indexes[0] " << indexes[0] << endl;
        }        
        assert(vol.size() > indexes[0] );
        assert(vol.size() > indexes[1] );
        return vol.get(indexes[0]) * weights[0]
            +  vol.get(indexes[1]) * weights[1];
      }
      case 3: {
        if(vol.size() <= indexes[0]){
          cout << "vol.size() " << vol.size() << endl;
          cout << "indexes[0] " << indexes[0] << endl;
        }        
        assert(vol.size() > indexes[0] );
        assert(vol.size() > indexes[1] );
        assert(vol.size() > indexes[2] );
        return vol.get(indexes[0]) * weights[0]
            +  vol.get(indexes[1]) * weights[1]
            +  vol.get(indexes[2]) * weights[2];
      }
      case 1: {
        if(vol.size() <= indexes[0]){
          cout << "vol.size() " << vol.size() << endl;
          cout << "indexes[0] " << indexes[0] << endl;
        }        
        assert(vol.size() > indexes[0] );
        return vol.get(indexes[0]) * weights[0];
      }
      default: {
        return 0;
      }
    }
  }

  /// Return the value of the RayPoint from
  /// the voxel indexes (indexes), the voxel weights (weights) and the given volum/phantom (vol)
  INLINE TYPE getMeanField(const BinVec3D<TYPE>& vol, const vector<uint32_t>& indexes, const vector<TYPE>& weights) const{
    TYPE val = 0;
    for (uint32_t i = 0; i < nbVoxelsSample; i++ ){
      val += vol.get(indexes[i]) * weights[i];
    }
    return val;
  }

};

/// This tructure is basically the ray without a reference system
template <typename TYPE>
class SubRay {
private:
  /// Resize the rays <=> make allocation of the maximal number of points this rays can sample.
  /// @param _size the maximal number of point this ray can sample
  /// @param withinteprolation True if the point sampled by the ray can have their value from an interpolation between neighbooring voxels 
  void resize(uint32_t _size, bool withInterpolation){
    points.resize(_size, RayPoint<TYPE>(withInterpolation ? max_size : 1));
  }

  /// Return the maximal number of points that the ray can sample 
  const size_t _size() const throw() { return points.size(); }


protected:
    /**
   * Weights associated to the indexes of the sampled points
   */
  vector<RayPoint<TYPE> >   points;

  ///
  /// Has explained in the history of the file we are now creating a set of ray with the maximal number of sample point
  /// the algorithm can need to avoid massive reallocation.
  /// But has the number of sample point by the ray can change from a rotation to an other we added the
  /// information about the current size. Which is the number of points sampled/registred by the ray for the curernt rotation 
  uint32_t currentSize;

public:
  /**
   * Default constructor
   * Note : this constructor has been removed and let here
   * to specify that we don t want to have rays without a fix sampling points size
   * Because we want to avoid the reallocation of such points.
   * The policy is now to have a set fix of ray containing all rays for one rotation.
   * And this set of ray will be used and updated for each rotation
   */
  // SubRay() : points(0, RayPoint<TYPE>(max_size)), currentSize(0), weight(1), lossFractionOutput(1) { }

  /// Constructor
  /// @param _maxsize : what is the maximal number of points the ray can sample
  /// @param withInterpolation : do we want to make the sampling with or without the interpolation.
  ///    Note : this directly affect the size of RayPoint because with interpolation we are reserving four spots for
  ///           weights and indexes. In the other case we will only reserve one.
  SubRay(uint32_t _maxSize, bool withInterpolation):
    points(vector<RayPoint<TYPE> >()), currentSize(0) 
  {
    // that a non sense that to call this function without resizing the RayPoint
    assert(_maxSize > 0);
    this->resize(_maxSize, withInterpolation);
  }

  /**
   * Max size of the samplable voxels in a 2D geometry
   */
  static const unsigned int max_size = 4;

  /**
   * Weight of the given subray: it's useful when many rays are there, and
   * you want a Gaussian shape for the ray.
   */
  TYPE weight;

  /**
   * This is the output of the ray in the transmission setup. In principle this
   * is the integral over the absorption coefficient
   */
  TYPE lossFractionOutput;

  /**
   * Position of the initial point in the ray
   */
  Position<TYPE> initPosition;

  /**
   * The incrementation to do to go from one point to an other
   */
  Position_FS pointIncrement;  

  /// Return the current number of points sampled by the ray for this Rotation
  const size_t size() const throw() { return currentSize; }
  
  /// Set the number of points sample by the voxel
  /// Warning : this value can t overstep the maximal number of points sampled by the ray
  inline void setCurrentSize(uint32_t s) {
    // Now the same set of rays is used for each rotation.
    // The maximal number of sample point is points.size(). Make sure we don t want to go "for more" 
    assert(s <= points.size());
    currentSize = s; 
  }

  /// Reset to 0 for all sampled points by the ray, the number of voxel used for each sampled points.
  void resetAllIndexes(){
    for (typename vector<RayPoint<TYPE> >::iterator it = points.begin(); it != points.end(); ++it ){
      it->reset();
    }   
  }

  /// reset to 0 all sample points by the Ray from the first to points.begin() + currentSize, the "size" parameter (aka number of sample voxel)
  /// This can afford some over iterations
  void resetActualIndexes(){
    for (typename vector<RayPoint<TYPE> >::iterator it = samplePointsBegin(); it != samplePointsEnd(); ++it ){
      it->reset();
    } 
  }

  /// reset the actual sample points of the Ray and change the current size of the ray to newSize
  /// @param newSize the new number of sample point by the Ray
  void reset(uint32_t newSize){
    this->resetActualIndexes();
    this->setCurrentSize(newSize);
  }

  /// Simple information print
  void printInfo() const{
    cout << "current number of sampled points = " << currentSize << endl;
    cout << "maximal number of sampled points by the Ray = " << points.size() << endl;
  }

  /// Getter to the first element of sampled point by the ray
  typename vector<RayPoint<TYPE> >::const_iterator samplePointsBegin() const {return points.begin();}
  /// Getter to the first element of sampled point by the ray
  typename vector<RayPoint<TYPE> >::iterator samplePointsBegin() {return points.begin();}

  /// Getter to the last element of the current sampled point by the ray
  typename vector<RayPoint<TYPE> >::const_iterator samplePointsEnd() const {return points.begin() + currentSize;}
  /// Getter to the last element of the current sampled point by the ray
  typename vector<RayPoint<TYPE> >::iterator samplePointsEnd() {return points.begin() + currentSize;}


#ifdef DEBUG
  static void checkIndex(const uint8_t & lsize, const uint32_t & index)
  {
    if (index >= lsize) {
      stringstream stream;
      stream  << "Out of boundaries for point: " << index
                << ", _size: " << lsize << "\n";
      throw OutOfBoundException(stream.str());
    }
  }
  static void checkSize(const uint8_t & lsize)
  {
    if (lsize >= max_size) {
      stringstream stream;
      stream  << "No place for adding a new point\n";
      throw OutOfBoundException(stream.str());
    }
  }
#endif
};

template <typename TYPE>
struct RayProperties{

  /**
   * Width of the Ray
   */
  TYPE width;

  /**
   * Offset of the ray respect to the center of the axes
   */
  TYPE offset;

  /**
   * The initial intensity of the ray
   */
  TYPE I0; 


  /// Constructor
  RayProperties(TYPE _width, TYPE _offset, TYPE _I0):
    width(_width), offset(_offset), I0(_I0)
  {}

  /// width setter
  void setWidth(TYPE _width) { width = _width;}
  /// offset setter
  void setOffset(TYPE _offset) {offset = _offset;}
  /// Intensity at the origin of the Ray setter
  void setI0(TYPE _I0) { I0 = _I0;}

  /// width getter
  const TYPE& getWidth() const { return width;}
  /// offset getter
  const TYPE& getOffset() const { return offset;}
  /// Intensity at the origin of the Ray getter
  const TYPE& getI0() const { return I0;}

};

template <typename TYPE>
struct Ray : public RayProperties<TYPE>, public SubRay<TYPE> {

  /**
   * Constructor
   * @param w Width of the ray
   * @param o Offset of the ray
   *   Note : we removed this constructor because we don t wan t to have inopportune reallocation of the points vector or stuff like that.
   *     So by using the second constructor we are allocating in one time the full vector for the entire reconstruction and 
   *     we fix his size.
   */
  // Ray(const TYPE &w, const TYPE &o, const TYPE &i): 
  //   RayProperties<TYPE>(w, o, i) { }

  /// Constructor
  /// @param lMaxSize the maximal number of point the ray can sample
  /// @param withInterpolation True if all sample point will get their values from an interpolation between neighbooring voxels. 
  Ray(const uint32_t lMaxSize, const bool withInterpolation , const TYPE &w, const TYPE &o, const TYPE &i): 
    RayProperties<TYPE>(w, o, i),
    SubRay<TYPE>(lMaxSize, withInterpolation) { }        

  /// Simple information print
  void printInfo() const {
    cout << "width = " << RayProperties<TYPE>::width << endl;
    cout << "offset = " << RayProperties<TYPE>::offset << endl;
    cout << "I0 = " << RayProperties<TYPE>::I0 << endl;
    SubRay<TYPE>::printInfo();
  }
};

} // End of FreeART namespace

#endif
