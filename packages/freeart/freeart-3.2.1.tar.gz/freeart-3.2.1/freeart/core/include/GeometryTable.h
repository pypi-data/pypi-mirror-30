//+==================================================================================================================
//
// GeometryTable.h
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
 * File:   GeometricalTable.h
 * Author: vigano
 *
 * Created on October 15, 2010, 2:25 PM
 */

#ifndef GEOMETRICALTABLE_H
#define	GEOMETRICALTABLE_H

#include "macros.h"
#include "GeometricTypes.h"
#include "GeometryStructures.h"
#include "RandomAccess.h"
#include "Exceptions.h"
#include "Sinogram.h"
#include "LookupTable.h"
#include "ReconstructionParameters.h"

namespace FREEART_NAMESPACE
{

template <typename TYPE>
class BaseGeometryTable : protected vector<Rotation<TYPE> *> {
private:
  // The structure storing the incomings rays.
  // To reduce memory impact and time allocation we will use 
  // the same for each rotation and update only values at each rotation iteration  
  vector<Ray<TYPE> > incomingRays;
  // The structure storing the outgoing rays.
  vector<Ray<TYPE> > outgoingRays;

public:
  void resizeIncomingRays(const uint32_t nbRays, const uint32_t maxSamplingPointsPerRays, const bool withInterpolation) 
  { 
    incomingRays.resize(nbRays, Ray<TYPE>(maxSamplingPointsPerRays, withInterpolation, 0.0, 0.0, 1.0));
  }
  void resizeOutgoingRays(const uint32_t nbRays, const uint32_t maxSamplingPointsPerRays, const bool withInterpolation) 
  { 
    outgoingRays.resize(nbRays, Ray<TYPE>(maxSamplingPointsPerRays, withInterpolation, 0.0, 0.0, 1.0));
  }

protected:

  /* Let's declare friend classes that can manage the structure of the table */
  template <typename TYPE2> friend class ScannerPhantom2D;
  friend class GeometryFactory;

  /**
   * Lookup Table for the offsets
   */
  LookupTable<TYPE> offsetsTable;

  /**
   * Dimensions of the phantom onto which this geometry is generated
   */
  Dimensions_UI32 phantomDims;

  /**
   * Total number of sampled points over the phantom
   */
  uint64_t totSampledPoints;

  Dimensions_UI32 matrDims;

  /**
   * All the parameters needed for the construction (projector) and the reconstruction
   */
  const ReconstructionParameters<TYPE>* reconsParam;

  void checkBoundaries(const size_t & index) const;
  void clean();

public:
  /**
   * Constructor
   * @param _r The radius of the active region
   */
  BaseGeometryTable(const ReconstructionParameters<TYPE>& _reconsParam);

  /**
   * Destructor
   */
  virtual ~BaseGeometryTable() { clean(); clear(); }

  /**
   * Resets the geometry table.
   */
  void reset();

  /// Phantom length getter (x dim)
  const uint32_t & getPhantomLength() const throw() { return phantomDims.x; }
  /// Phantom width getter (y dim)
  const uint32_t & getPhantomWidth() const throw() { return phantomDims.y; }
  /// Phantom height getter (z dim)
  const uint32_t & getPhantomHeight() const throw() { return phantomDims.z; }
  /// Phantom dimensions getter
  const Dimensions_UI32 & getPhantomDims() const throw() { return phantomDims; }
  /// Phantom dimensions setter
  void setPhantomDims(const Dimensions_UI32 &_d) {phantomDims = _d;}
  /// Phantom length setter (x dim)
  void setPhantomLength(const uint32_t & _l) throw() { phantomDims.x = _l; }
  /// Phantom width setter (x dim)
  void setPhantomWidth(const uint32_t & _w) throw() { phantomDims.y = _w; }
  /// Phantom height setter (x dim)
  void setPhantomHeight(const uint32_t & _h) throw() { phantomDims.z = _h; }

  /// BeamCalculationmethod getter
  RayPointCalculationMethod getRayPointCalculationMethod() const;
  /// OutgoingRayAlgorithm getter
  OutgoingRayAlgorithm getOutgoingRayAlgorithm() const;
  /// Reconstruction params getter
  const ReconstructionParameters<TYPE>* getReconstructionParams() const { return reconsParam;}
  /// Return the number of incoming rays per rotation 
  const uint32_t & getTotIncomingRaysPerRot() const throw() {
    return reconsParam->getTotRaysPerRot().incoming;
  }
  /// Return the number of outgoing rays per rotation 
  const uint32_t & getTotOutgoingRaysPerRot() const throw() {
    return reconsParam->getTotRaysPerRot().outgoing;
  }

  /// Return the offsets between rays
  const LookupTable<TYPE> & getOffsets() const throw() {
    return offsetsTable;
  }

  /**
   * Tells whether this geometry table is compatible with a given phantom (volume)
   * @param vol The reference volume
   */
  bool isCompatibleWith(const BinVec3D<TYPE> & vol) const throw();
  /**
   * Tells whether this geometry table is compatible with a given Sinogram
   * @param sino The reference sinogram
   */
  bool isCompatibleWith(const Sinogram & sino) const throw();

  /**
   * Getter for the rotations
   * @param numRot the cardinal number of the rotation
   */
  const Rotation<TYPE> & getRotation(const size_t & numRot) const
  {
    DEBUG_CHECK( checkBoundaries(numRot) );
    return *(*this)[numRot];
  }
  /**
   * Getter for the rotations
   * @param numRot the cardinal number of the rotation
   */
  Rotation<TYPE> & getRotation(const size_t & numRot)
  {
    DEBUG_CHECK( checkBoundaries(numRot) );
    return *(*this)[numRot];
  }

  void initRaysAllocation(const Dimensions_UI32& matDimensions);

  void computeGeometryForSliceRotation(const size_t &, const size_t &, const GenericSinogram3D<TYPE> &, bool withInterpolation);
  void computeGeometryForSliceRotation(const size_t &, const radians &, bool withInterpolation);

  const uint64_t & getTotSampledPoints() const throw() {return totSampledPoints;}

  const Dimensions_UI32 &getMatrDims() {return matrDims;}
  void setMatrDims(const Dimensions_UI32 &_pos) {matrDims = _pos;}

  // Return the vector containing the incoming rays
  const vector<Ray<TYPE> >& getIncomingRays() const { return incomingRays;}
  vector<Ray<TYPE> >& getIncomingRays() { return incomingRays;}
  // Return the vector containing the outoging rays
  const vector<Ray<TYPE> >& getOutgoingRays() const { return outgoingRays;}
  vector<Ray<TYPE> >& getOutgoingRays() { return outgoingRays;}


  /* Let's grant again public access to evaluation functions in the base class,
   * inherited as protected */
  using vector<Rotation<TYPE> *>::clear;
  using vector<Rotation<TYPE> *>::operator[];
  using vector<Rotation<TYPE> *>::empty;
  using vector<Rotation<TYPE> *>::size;
  using vector<Rotation<TYPE> *>::reserve;
};

#ifdef USER_DOC
/**
 * Class used to store a reconstruction geometry
 *
 * This class is used to store the reconstruction geometry. It is created by the factory class GeometryFactory.
 *
 * @headerfile FreeART.h
 */

class GeometryTable {
#else
template <typename TYPE>
class GeometryTable : public BaseGeometryTable<TYPE> {
#endif

  /* Let's declare friend classes that can manage the structure of the table */
  template <typename TYPE2>friend class ScannerPhantom2D;
  friend class GeometryFactory;

  /**
   * The solid angles associated to the detector from the position of the voxels
   */
  TYPE *solidAngles;

  /**
   * Loss fractions of the incident radiation (is the integral of the
   * absorption coefficient on the rout of the ray to the voxels)
   */
  TYPE *lossFractionIncident;

  /**
   * Collection of the geometries for the self absorption case
   */
  BinVec<BaseGeometryTable<TYPE> >     selfAbsGeometries;
  /**
   * Matrices for all the rotations of all the geometries that associate a
   * self-absorption factor to every voxel in the phantom
   */
  PointedBinVec2D<BinVec3D<TYPE> >  selfAbsAttenuations;
  /**
   * List of rotation angles (used when generating Sinograms)
   */
  AnglesArray rotAnglesArray;

  /**
   * Clean method for resetting the table and releasing the memory
   */
  void clean();

public:
#ifdef USER_DOC
///@privatesection
#endif
  /**
   * Constructor
   * @param _r The radius of the active region
   */
  GeometryTable(const ReconstructionParameters<TYPE> &);

  /**
   * Destructor
   */
  ~GeometryTable() { clean(); this->clear(); }

  /**
   * Resets the geometry table.
   */
  void reset();

  const TYPE * getSolidAngles() const throw() {
    return solidAngles;
  }
  const TYPE * getIncidentLossFractions() const throw() {
    return lossFractionIncident;
  }

  const BinVec3D<TYPE> & getSelfAbsorpAttenuation(const uint32_t & detector,
                                               const uint32_t & numRot)
    const
  {
    return selfAbsAttenuations.get(detector, numRot);
  }

  void setSelfAbsMatriceForFluo(BinVec3D<TYPE> mat);

  void computeGeometryForFluoDetector(const double, const RayPointCalculationMethod beamCalculationMethod);
  void computeGeometryForDiffractDetector(const vector<double> &, const RayPointCalculationMethod beamCalculationMethod);

  void createInitLossFractionIncident();

  PointedBinVec2D<BinVec3D<TYPE> >  &getSelfAbsAttenuations() {return selfAbsAttenuations;}
  BinVec<BaseGeometryTable<TYPE> >     &getSelfAbsGeometries() {return selfAbsGeometries;}

  AnglesArray &getRotAnglesArray() {return rotAnglesArray;}
  const AnglesArray &getRotAnglesArray() const {return rotAnglesArray;}

};

} // End of FreeART namespace

#endif	/* GEOMETRICALTABLE_H */

