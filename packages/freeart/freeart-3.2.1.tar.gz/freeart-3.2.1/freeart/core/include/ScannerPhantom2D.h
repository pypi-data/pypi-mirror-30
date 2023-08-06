//+==================================================================================================================
//
// ScannerPhantom2D.h
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
 * ScannerPhantom2D.h
 *
 *  Created on: Dec 7, 2010
 *      Author: vigano
 *
 *  Refactoring on June, 2016 : Creation of VoxelSelector class.
 *      Author: payno
 */

#ifndef SCANNERPHANTOM2D_H_
#define SCANNERPHANTOM2D_H_

#include "GeometryStructures.h"
#include "GeometryTable.h"
#include "ReferencedObject.h"
#include "BinaryVectors.h"
#include "Exceptions.h"
#include "Sinogram.h"
#include "ReconstructionParameters.h"

#include "RayHelpers.h"

namespace FREEART_NAMESPACE
{

/**
 * Class that is the engine of sampling for the construction of the geometry
 * table
 */
/**
 * Data structure that holds the data for one rotation
 */
template <typename TYPE>
struct RotationData {
  ReferencedObject refSys;

  bool forward;
  bool alongX;
  Position<TYPE> pointIncrement;

  RotationData(const float_C & vw, const float_C & vh) : refSys(0.0, vw, vh)
  { }

  void printInfo() const {
    cout << " forward = " << forward << endl;
    cout << "alongX = " << alongX << endl;
    cout << "pointIncrement : (" << pointIncrement.x << ", " << pointIncrement.y << " )" << endl;
    refSys.printInfo();
  }
};

/**
 * Data structure that holds the data for an iteration, updated every time we
 * select a new point to sample
 */
template <typename TYPE>
struct IterationData {
  RotationData<TYPE> rot;
  const float_C increment;
  Range2D_D limits;
  StraightLine line;

  // uint32_t sampComplete, sampPartial;

  IterationData(RotationData<TYPE> & _rot, const float_C & incr) throw()
    : rot(_rot), increment(incr), limits(Range_D(0.0,0.0), Range_D(0.0,0.0))
    , line(0,0) //, sampComplete(0), sampPartial(0)
  { }
  void setPosition(Position<TYPE> _pos) { pos = _pos;}
  Position<TYPE>& getPosition() { return pos;}
  void printInfo() const { 
    cout << "pos = (" << pos.x << ", " << pos.y << ")" << endl;
    rot.printInfo(); 
  }
private:
  Position<TYPE> pos;
};


/**
* The VoxelSelector class is used to select for a given point
* the voxels (cells) we have to sample to get his value.
* Note : those functions were part of the ScannerPhantom2D previously.
*/

template <typename TYPE>
class VoxelSelector{
protected:

  const ReconstructionParameters<TYPE>& rp;
  const uint32_t phantomWidth, phantomLength;
  const float_C semiX, semiY;
  bool isIncoming; // True if we are selecting voxels for the incoming beam


public:
  /// Constructor
  VoxelSelector(const ReconstructionParameters<TYPE>& _rp, const uint32_t _phantomLength, const uint32_t _phantomWidth):
    rp(_rp), phantomWidth(_phantomWidth), phantomLength(_phantomLength), 
    semiX( GET_C_SEMI(_phantomWidth) ), semiY( GET_C_SEMI(_phantomWidth)  ),
    isIncoming(true) {

    }


  /// Destructor
  ~VoxelSelector(){};

  /**
   * Compute the indexes and the weights for sampling the point at pos in the phantom with dimensions phantomWidth * phantomLength
   *
   * @param pos the position of the point to sample
   * @param phantomWidth the width of the phantom 
   * @param phantomLength the length of the phantom
   * @param rp the reconstructionParameters
   * @param indexes : indexes of the voxels to use to cpmpute the sample values 
   * @param weights : weights of the voxels selected
   * @param semiX 
   * @param semiY 
   */
  uint8_t selectVoxels( const Position<TYPE> & pos, vector<uint32_t>& indexes, vector<TYPE>& weights, uint8_t& sizes );

  /// Flag the scanner to notice if we are working on incoming rays or outgoing rays (aka seconderies rays)
  void setIsIncomingBeam(bool b) { isIncoming = b;}


private:
  /**
   * store the voxel with position iy, ix amd weight to the corresponding buffers
   * @param iy y position of the voxel to store
   * @param ix x position of the voxel to store
   * @param weight the weight to attribute to this voxel
   * @param indexes where to store this voxel
   * @param weights where to sotre the weight
   * @param semiX 
   * @param semiY 
   */
  // void storeVoxel(const float_C& iy, const float_C& ix, const float_C& weight, BinVec_UI32& indexes, BinVec<TYPE>& weights );


  /**
   * Adds the voxel at the given position, with their weights, to the list of
   * sampled voxels for the given sampling point
   *
   * @param weights List of voxels+weights to fill
   * @param iy The position of the voxel on the Y axis
   * @param ix The position of the voxel on the X axis
   * @param weight the weight of the given voxel
   * @param firstVoxelSample is it the first voxel we are using for this point (then need to add a 'size' value otherwise will update this value)
   * @param isIncoming True if the subRay we are saving a voxel for is an incoming subRay (incoming Beam)
   */
  bool saveVoxel( const float_C& iy, const float_C& ix, const TYPE& weight, 
  vector<uint32_t>& indexes, vector<TYPE>& weights, uint8_t& size );



};

template <typename TYPE>
class ScannerPhantom2D : public VoxelSelector<TYPE>{

private:
  /**
   * The geometry table to fill
   */
  BaseGeometryTable<TYPE> & gt;

  /**
   * Adds the voxel at the given position, with their weights, to the list of
   * sampled voxels for the given sampling point
   *
   * @param weights List of voxels+weights to fill
   * @param iy The position of the voxel on the Y axis
   * @param ix The position of the voxel on the X axis
   * @param weight the weight of the given voxel
   * @param firstVoxelSample is it the first voxel we are using for this point (then need to add a 'size' value otherwise will update this value)
   * @param isIncoming True if the subRay we are saving a voxel for is an incoming subRay (incoming Beam)
   */
  bool saveVoxel( SubRay<TYPE>& subray, const float_C& iy,
                  const float_C& ix, const float_C& weight, 
                  const bool firstVoxelSample);

  /**
   * Method that samples the given points and selects the voxels if they are
   * in the active region
   *
   * @param subRay the subRay for which we are selecting voxels
   * @param pos the position of the point we want to selecVoxelsFor (aka the sampling point)
   * @param rp the reconsturction parameters. Needed to know how to select voxels
   * @param isIncomingRay True if the subRay we are saving a voxel for is an incoming subRay (incoming Beam)
   */
  unsigned int selectVoxels(SubRay<TYPE> & subRay, const Position<TYPE> &pos );

  /**
   * It fixes the first poin of the scanning process
   *
   * @param data The scanning data
   * @param offset The actual offset of the ray in the other frame of reference
   * @param isIncoming True if the ray we are looking at is the an incoming ray 
   *        (needed initially because for the option outgoingrayPointCalculationMethod == matriceSubdivision )
   *        we have to take into account of the scaling of the selfAbs matrice.
   */
  void fixRayEntrance(IterationData<TYPE> &data, const float_C &offset);

public:

  /// Constructor
  ScannerPhantom2D( BaseGeometryTable<TYPE> & _gt): 
    VoxelSelector<TYPE>(*_gt.getReconstructionParams(), _gt.getPhantomLength(), _gt.getPhantomWidth() ),
    gt(_gt)
  { }
  /**
   * Destructor: it frees the unused pre-allocated memory once finished
   */
  ~ScannerPhantom2D() { }

  /**
   * Main method for sampling the phantom. Samples one rotation per time.
   *
   * @param gt the geometry table
   * @param isIncoming true if we want to sample voxels for incoming rays. Then we will sample the matrice
   * of the incoming beams (aka absMatrice). Otherwise we will sample the matrice of the outgoing beams (aka selfAbsMatrice) 
   */
  void sampleVoxels(BaseGeometryTable<TYPE>& gt, const bool isIncomingRay);

  /* Set the final point and the data limits, direction... from a begin point and an angle
   * basically the angle is representing a direction, and added to the begin point we have line.
   * Has the angle is signed we even have an half-line and we can determine the intersection 
   * between the circle and the half line. This is the end point
   * @param data : the scanning data. Will store sampling limitation.
   * @param angle : the angle that the rai is making with the sanple. 
   *        WARNING : this angle must be signed, otherwise the algorithm might and up with the wrong intersection point
   *                  between the circle and the line
   * @param beginPoint the origin of the ray / halfLine
   */
  void fixRayExit(IterationData<TYPE>& data, const radians& angle, const Position<TYPE>& beginPoint);
  /**
   * Method that samples a straight line (called by 'sampleVoxels' and does
   * the core business of that method)
   *
   * @param vwlist the subray to sample
   * @param data The scanning data
   * @param reconstr The boolean that says if we are reconstructing
   * @param isIncoming true if we are sampling a line for an incoming ray
   */
  void sampleLine(SubRay<TYPE> &vwlist, IterationData<TYPE> &data );

  /**
   * Method to sample the line / subray knowing her origin (data.pos) and her direction (data.rot.pointIncrement)
   * @param vwlist the subray to sample
   * @param data The scanning data. Must have the line origin (data.pos) and the line direction (data.rot.pointIncrement) up to date
   * @param rp the reconsturctionParameters
   */
  void sampleLineFromOriginAndDirection(SubRay<TYPE> &vwlist, IterationData<TYPE> &data );

  /**
   * Set all informations needed by the rotation data such as the direction... fron her original rotation
   * @param rotData data to set according to the ref system
   * @param rot information about the current rotation
   * @param angular out variable. Used for the Joseph ampling algorithm
   * @param lineDenom out variable. Used for the Joseph sampling algorithm
   * @param overSamp the oversampling number
   */
  void setRotData(RotationData<TYPE>& rotData, Rotation<TYPE>& rot, TYPE& angularCoeff, TYPE& lineDenom, const uint32_t overSamp );  

  /**
   * Set all informations needed by the rotation data such as the direction... fron her original rotation
   * @param rotData data to set according to the ref system
   * @param angular out variable. Used for the Joseph ampling algorithm
   * @param lineDenom out variable. Used for the Joseph sampling algorithm
   * @param overSamp the oversampling number
   */
  void setRotData(RotationData<TYPE>& rotData, TYPE& angularCoeff, TYPE& lineDenom, const uint32_t overSamp);

  /**
   * Compute the indexes and the weights for sampling the point at pos in the phantom with dimensions phantomWidth * phantomLength
   *
   * @param pos the position of the point to sample
   * @param phantomWidth the width of the phantom 
   * @param phantomLength the length of the phantom
   * @param rp the reconstructionParameters
   * @param indexes : indexes of the voxels to use to cpmpute the sample values 
   * @param weights : weights of the voxels selected
   * @param semiX 
   * @param semiY 
   */
  static void computeIndexesAndWeights( const Position<TYPE> & pos, const uint32_t phantomWidth, const uint32_t phantomLength, 
    vector<uint32_t>& indexes, vector<TYPE>& weights, const TYPE& semiX, const TYPE& semiY  );

  /**
   * store the voxel with position iy, ix amd weight to the corresponding buffers
   * @param iy y position of the voxel to store
   * @param ix x position of the voxel to store
   * @param weight the weight to attribute to this voxel
   * @param indexes where to store this voxel
   * @param weights where to sotre the weight
   * @param semiX 
   * @param semiY 
   */
  static void storeVoxel(const float_C& iy, const float_C& ix, const float_C& weight, vector<uint32_t>& indexes, vector<TYPE>& weights, 
    const uint32_t & phWidth, const TYPE& semiX, const TYPE& semiY );

};

} // End of FreeART namespace

#endif /* SCANNERPHANTOM2D_H_ */
