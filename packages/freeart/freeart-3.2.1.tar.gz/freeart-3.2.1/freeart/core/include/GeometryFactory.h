//+==================================================================================================================
//
// GeometryFactory.h
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
 * GeometryFactory.h
 *
 *  Created on: Dec 20, 2010
 *      Author: vigano
 */

#ifndef GEOMETRYFACTORY_H_
#define GEOMETRYFACTORY_H_

#include "Sinogram.h"
#include "GeometryTable.h"
#include "Detector.h"
#include "ScannerPhantom2D.h"

#include <bitset>

namespace FREEART_NAMESPACE
{

/**
 * Factory for reconstruction geometries
 *
 * This class is a factory to create the geometries used during the reconstruction process
 *
 * @headerfile FreeART.h
 */

class GeometryFactory {
template <typename TYPE> friend class BaseGeometryTable;
private:
  Position_UI32 matrDims;

  /**
   * Method to help in guessing the right geometry for the given sinogram, based
   * on the chosen preferences
   *
   * @param width Number of points in a slice (row) of the sinogram
   * @param voxWidth Physical width of a voxel
   * @param voxHeight Physical height of a voxel
   */
  const Position_UI32 guessPhantomDims(const uint32_t & width,
      const float_C & voxWidth, const float_C & voxHeight)
    const;

  /**
   * Adds a new rotation object to the given geometry table.
   *
   * @param gt The geometry table to modify
   * @param angle the angle for the given rotation
   * @param ray Contains the information about intensity and width of the rays
   * @param isIncoming true if the rotation we want to add concern an incoming ray
   *                   false if concern an outgoing ray
   */
  template <typename TYPE>
  void addRotation(BaseGeometryTable<TYPE> & gt, const radians & angle,
      const RayProperties<TYPE>& ray, const bool isIncoming);

  /**
  * Add rotation for incomings rays
   * @param gt The geometry table to modify
   * @param angle the angle for the given rotation
   * @param ray Contains the information about intensity and width of the rays  
  */
  template <typename TYPE>
  void addRotationIncomingRays(BaseGeometryTable<TYPE> & gt, const radians & angle,
      const RayProperties<TYPE>& ray){
    addRotation(gt, angle, ray, true);
  }

  /**
  * Add rotation for outgoing rays
   * @param gt The geometry table to modify
   * @param angle the angle for the given rotation
   * @param ray Contains the information about intensity and width of the rays  
  */
  template <typename TYPE>
  void addRotationOutgoingRays(BaseGeometryTable<TYPE> & gt, const radians & angle,
      const RayProperties<TYPE>& ray){
    addRotation(gt, angle, ray, false);
  }


  /**
   * Prepares the table and returns the information about the rays
   *
   * @param gt The geometry table to prepare
   */
  template <typename TYPE>
  RayProperties<TYPE> prepareTable( BaseGeometryTable<TYPE> & gt, const bool isIncoming );

  /**
   * Creates the headings of the table, using the angles in the sinogram
   *
   * @param gt The Geometry Table to create
   * @param sino The sinogram from which to make the geometry
   */
  template <typename TYPE>
  void createTable( BaseGeometryTable<TYPE> & gt, const Sinogram & sino, const bool isIncoming);

  /**
   * Creates the headings of the table, using the angles in the sinogram
   *
   * @param gt The Geometry Table to create
   * @param sino The sinogram from which to make the geometry
   */
  template <typename TYPE>
  void createTableForIncomingRays( BaseGeometryTable<TYPE> & gt, const Sinogram & sino){
    return createTable(gt, sino, true);
  }

  /**
   * Creates the headings of the table, using the angles in the sinogram
   *
   * @param gt The Geometry Table to create
   * @param sino The sinogram from which to make the geometry
   */
  template <typename TYPE>
  void createTableForOutgoingRays( BaseGeometryTable<TYPE> & gt, const Sinogram & sino){
    return createTable(gt, sino, false);
  }

  /**
   * Loads the interpolated coefficients of absorption from the absorption
   * matrix and puts them in the given vector
   *
   * @param subray The subray with the points to interpolate
   * @param matr The absorption matrix
   * @param coeff A pointer to the C vector of the interpolated coefficients
   */
  template <typename TYPE>
  void loadMeanCoeffs(const SubRay<TYPE> & subray, const BinVec3D<TYPE> & matr,TYPE * coeff);

  template <typename TYPE>
  void loadMeanCoeffs_withFactorOnIndexes(const SubRay<TYPE> & subray, const BinVec3D<TYPE> & matr,TYPE * coeff, 
    uint32_t loadMeanCoeffs_withFactorOnIndexes = 1);


  /**
   * Updates the given self-absorption correction matrix, from the geometry
   * slice in the rotation object and the absorption coefficients matrix
   *
   * @param rot The Rotation object with the information on the geometry
   * @param absorbMatr Matrix of the absorption coefficients
   * @param selfAbsorbMatr Matrix of the corrections for self-absorption
   * @param overSampling The over sampling factor
   */
  template <typename TYPE>
  void updateSelfAbsorptionMatrices(Rotation<TYPE> & rot,
      const BinVec3D<TYPE> & absorbMatr, BinVec3D<TYPE> & selfAbsorbMatr,
      const ReconstructionParameters<TYPE>& );
  /**
   * Builds and calculates the incoming loss fraction for the given Geometry
   * from the given matrix of absorption coefficients
   *
   * @param gt The Geometry Table
   * @param absorbMatr The matrix with the absorption coefficients
   */
  template <typename TYPE>
  void buildIncomingLossFraction(GeometryTable<TYPE> & gt,const BinVec3D<TYPE> & absorbMatr);

  /**
   * Updates the incoming loss fraction for the points in the given rotation
   *
   * @param rot Geometry information about the selected rotation
   * @param absMatr The matrix with the absorption coefficients
   * @param lossFractionIncident C vector containing the loss fractions
   * @param stepLength The length between two sample point 
   */
  template <typename TYPE>
  void updateIncomingLossFraction(Rotation<TYPE> & rot, const BinVec3D<TYPE> & absMatr,
      TYPE * lossFractionIncident, const TYPE stepLength, const TYPE physicalSize);

  /**
   * Will create the matrice containing for each voxel the total attenuation
   * from a voxel to the detector
   *
   * @param rot Geometry information about the selected rotation
   * @param initialSelfAbsorbMatr the matrice containing the absorption 
   *        of the outgoing beam for each voxel
   * @param OBLossFractionBuffer contains all rays of all rotation. 
   *        This is the raw data used to create the outgoingBeamTotalAttenuationMatrice
   * @param outgoingBeamTotalAttenuationMatrice the matrice we want to fill
   *        with for each voxel the total attenuation from this voxel
   *        to the detector.    
   */
  template<typename TYPE>
  void createSelfAbsorptionMatriceFromRays( const Rotation<TYPE>& rot, const BinVec3D<TYPE>& initialSelfAbsorbMatr,
      BinVec<TYPE>& OBLossFractionBuffer, BinVec3D<TYPE>& outgoingBeamTotalAttenuationMatrice );


  /**
   * Compute the self absorption (absorption of the outgoing ray) trhought the given ray.
   * @param rot the rotation information about the incoming ray
   * @param initPos the position of the sampled point (origin of the new outgoing ray)
   * @param ray : the new outgoing ray which goes to the detector.
   * @param selfAbsMatrix : the matrice storing the attenuation of the outgoing beam for each 
   *          voxels
   * @param rotData all the datas concerning the current rotation
   * @param lineDenom the denominator needed for the Joseph sampling algorithm
   * @param angularCoeff the angular coefficient needed by the Joseph sampling algorithm
   * @param scanner the engine that is 'running' the expreiment
   * @param outgoingAngle the angle of the outgoing ray within the sample (compare to the vector 0, 1 ). Clockwise oriented. 
   */
  template <typename TYPE>
  TYPE getOutgoingLossFraction(const Rotation<TYPE>& rot, const Position<TYPE>& initPos, Ray<TYPE>& ray, 
    const BinVec3D<TYPE>& selfAbsMatrix, RotationData<TYPE> rotData, TYPE lineDenom, 
    TYPE angularCoeff, ScannerPhantom2D<TYPE>& scanner, const radians& outgoingAngle, 
    const ReconstructionParameters<TYPE>& rp );

  /**
   * Updates the incoming loss fraction (which should have been calculated previously)
   * for each sample point by mulplying it by the outgoing loss fraction.
   * calculated at this point.
   * NOTE : this function will create for each sample point in the lossFractionIncident
   * the correcponding outgoing ray to compute the outgoing qbsorption. This can be costly.
   * @param rot Geometry information about the selected rotation
   * @param absMatr The matrix with the self absorption coefficients (absorption of the outgoing ray)
   * @param lossFractionIncident C vector containing the loss fractions   
   * @param gt the geometry table
   * @param scanner the scanner.
   */
  template <typename TYPE>
  void updateIncomingLossFractionWithOutgoingLossFraction(  Rotation<TYPE>& incomingRot, const BinVec3D<TYPE> & selfAbsMatrice,
      TYPE* incomingLossFraction, GeometryTable<TYPE>& gt, ScannerPhantom2D<TYPE>& scanner, radians detAngle);

public:
  /**
   * Constructor
   *
   */
  GeometryFactory() { }

  /**
   * Method that creates a Geometry table from the given phantom shape and
   * sinogram structure
   *
   * @param sino The sinogram
   * @param reconsType The reconstruction type (Tx, Fluo, ...)
   * @param selfAbs Self absorption flag
   */
  template <typename TYPE>
  GeometryTable<TYPE> * getGeometryFromSinogram(const GenericSinogram3D<TYPE> & sino, bitset<MAX_TYPES> reconsType,
                                                const ReconstructionParameters<TYPE>& rp, const bool selfAbs);

  /**
   * Creates the geometry table from the given angles, or if none given, from
   * fixed angles.
   *
   * @param ph The phantom
   * @param reconsType The reconstruction type (Tx, Fluo, ...)
   * @param selfAbs Self absorption flag
   * @param angles The array of the angles
   */
  template <typename TYPE>
  GeometryTable<TYPE> * getGeometryFromPhantom(const BinVec3D<TYPE> &, const TYPE,bitset<MAX_TYPES> reconsType,
    const ReconstructionParameters<TYPE>& rp, const bool selfAbs,
    const AnglesArray & angles = AnglesArray());

#ifdef USER_DOC
///@privatesection
#endif
  /**
   * Evaluates the Incoming Loss Fraction for all the voxels in the given
   * projection
   * @param gt The geometry table
   * @param matr The absorption coefficients matrix
   * @param numRot The number of the rotation to consider
   */
  template <typename TYPE>
  void updateIncomingLossFraction(GeometryTable<TYPE> & gt, const BinVec3D<TYPE> & matr,const uint32_t & numRot);
  /**
   * Evaluates the Incoming Loss Fraction for all the voxels in all the
   * projections
   * @param gt The geometry table
   * @param matr The absorption coefficients matrix
   */
  template <typename TYPE>
  void updateIncomingLossFraction(GeometryTable<TYPE> & gt, const BinVec3D<TYPE> & matr);
  /**
   * Generates the Self-Absorption geometry that can be used later to generate
   * the corrections. This is independent of the later input matrices.
   *
   * @param gt The geometry table that contains the whole geometry
   * @param numRot The rotation number
   * @param reconsType The reconstruction type (Tx, Fluo,...)
   */
  template <typename TYPE>
  void buildSelfAbsorptionGeometry(GeometryTable<TYPE> & gt,size_t numRot,const bitset<MAX_TYPES> reconsType);
  /**
   * Evaluates the Outgoing Loss Fraction for all the voxels in the list
   * This is the real contribution from the self-absorption
   * @param gt The geometry table
   * @param absorbMatr The matrix with the absorption coefficients
   * @param createOneRayPerSamplePoint create the "real" outgoing ray for each sample point in the incoming ray
   */
  template <typename TYPE>
  void updateSelfAbsorptionMatrices(GeometryTable<TYPE> & gt,
      const BinVec3D<TYPE> & absorbMatr, const radians detAngle);
 /**
   * It assigns the fields of the solid angle to the sampled points
   *
   * @param gt The geometry table
   * @param det The position of the detector (for solid angles/self-abs)
   */
  template <typename TYPE>
  void assignSolidAngles(GeometryTable<TYPE> & gt, const FluoDetector & det);
  /**
   * Fills the geometry table with the sampled points, based on phantom,
   * for the projection to a sinogram
   *
   * @param gt The Geometry Table to create
   * @param isIncoming : True is we are sampling the table for incoming rays. Otherwise will outgoings rays.
   */
  template <typename TYPE>
  void sampleTable(BaseGeometryTable<TYPE> & gt, const bool isIncoming);

  /**
   * Fills the geometry table with the sampled points for incoming rays, based on phantom,
   * for the projection to a sinogram
   *
   * @param gt The Geometry Table to create
   */
  template <typename TYPE>
  void sampleTableForIncomingRays(BaseGeometryTable<TYPE> & gt ){
    return sampleTable(gt, true);
  }  

  /**
   * Fills the geometry table with the sampled points for outgoings rays, based on phantom,
   * for the projection to a sinogram
   *
   * @param gt The Geometry Table to create
   */
  template <typename TYPE>
  void sampleTableForOutgoingRays(BaseGeometryTable<TYPE> & gt ){
    return sampleTable(gt, false);
  }  

  /**
   * Creates the headings of the table, using the list of given angles
   *
   * @param gt The Geometry Table to create
   * @param angles a list of angles (in degrees)
   * @param isIncoming true if we are creating a table for the incoming ray. Otherwise is the outgoing ray
   */
  template <typename TYPE>
  void createTable( BaseGeometryTable<TYPE> & gt, const AnglesArray & angles, const bool isIncoming);

  /**
   * Creates the headings of the table for inconing ray, using the list of given angles
   *
   * @param gt The Geometry Table to create
   * @param angles a list of angles (in degrees)
   */
  template <typename TYPE>
  void createTableForIncomingRays( BaseGeometryTable<TYPE> & gt, const AnglesArray & angles){
    return createTable(gt, angles, true);
  }

  /**
   * Creates the headings of the table for outgoing ray, using the list of given angles
   *
   * @param gt The Geometry Table to create
   * @param angles a list of angles (in degrees)
   */

  template <typename TYPE>
  void createTableForOutgoingRays( BaseGeometryTable<TYPE> & gt, const AnglesArray & angles){
    return createTable(gt, angles, false);
  }

  /**
   * Creates the headings of the table, using the specified angle
   *
   * @param gt The Geometry Table to create
   * @param angle The angle (in degrees)
   * @param isIncoming true if we are creating table for incoming rays. False otherwise
   */
  template <typename TYPE>
  void createTable( BaseGeometryTable<TYPE> & gt, const radians & angle, const bool isIncoming);

  template <typename TYPE>
  void createTableForIncomingRays( BaseGeometryTable<TYPE> & gt, const radians & angle){
    createTable(gt, angle, true);
  }


  template <typename TYPE>
  void createTableForOutgoingRays( BaseGeometryTable<TYPE> & gt, const radians & angle){
    createTable(gt, angle, false);
  }

  /// Return the dimensions of the matrices (aka phantom, ansMat and selfAnsMat)
  const Dimensions_UI32 &getMatrDims() {return matrDims;}
  /// set dimensions of the matrices (aka phantom, ansMat and selfAnsMat)
  void setMatrDims(const Dimensions_UI32 &_pos) {matrDims = _pos;}

  /**
   * Scale a given matrice of the scaleFactor
   *
   * @param matrToScale the matrice to scale
   * @param scaledMatr the matrice ti update/scale
   * @param scaleFactor the scale factor 
   *
   */
  template <typename TYPE>
  void scaleMatrice_xy(const BinVec3D<TYPE>& matrToScale, BinVec3D<TYPE>& scaledMatr, const uint32_t scaleFactor);

};

} // End of FreeART namespace

#endif /* GEOMETRYFACTORY_H_ */
