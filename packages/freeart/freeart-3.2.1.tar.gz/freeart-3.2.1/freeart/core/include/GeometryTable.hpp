//+==================================================================================================================
//
// GeometryTable.tpp
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

#include "FreeARTAlgorithm.h"
#include <assert.h>

namespace FREEART_NAMESPACE
{

using namespace std;

//--------------------------------------------------------------------------------------------------
//
//                  BaseGeometryTable class methods
//
//--------------------------------------------------------------------------------------------------

#if defined(DEBUG) /* Begin Debug Zone */
# include <sstream>

using namespace std;

template <typename TYPE>
void BaseGeometryTable<TYPE>::checkBoundaries(const size_t & index) const
{
  if (index >= this->size()) {
    stringstream stream;
    stream  << "Out of boundaries for rotation: " << index
            << ", table size: " << this->size() << "\n";
    throw OutOfBoundException(stream.str());
  }
}
#endif /* End Debug Zone */

template <typename TYPE>
BaseGeometryTable<TYPE>::BaseGeometryTable(const ReconstructionParameters<TYPE>& _reconsParam)
  : phantomDims(0,0), totSampledPoints(0), reconsParam(&_reconsParam)
{ }

template <typename TYPE>
void BaseGeometryTable<TYPE>::clean()
{
  DebugPrintf(("Cleaned Geometry Table!\n"));
  const size_t & totRots = size();
  for(uint32_t numRot = 0; numRot < totRots; numRot++ ) {
    delete (*this)[numRot];
  }
  setPhantomLength(0);
  setPhantomWidth(0);
  totSampledPoints = 0;
}

template <typename TYPE>
void BaseGeometryTable<TYPE>::reset()
{
  this->clean();
  this->clear();
}

template <typename TYPE>
bool BaseGeometryTable<TYPE>::isCompatibleWith(const BinVec3D<TYPE> &vol) const throw()
{
  return (getPhantomLength() == vol.getLength()
            && getPhantomWidth() == vol.getWidth()
            && getPhantomHeight() == vol.getHeight());
}

template <typename TYPE>
bool BaseGeometryTable<TYPE>::isCompatibleWith(const Sinogram & sino) const throw()
{
  /* It verifies that both sinogram and geometry table have the same number of
   * Rays and rotations */
  const size_t & totRots = size();
  const bool equalSizes = (totRots == sino.size())
                            && (totRots && (this->getTotRaysPerRot() == sino.getWidth()));

  if (equalSizes) {
    /* If the previous condition holds, it checks if the rotation angles are
     * the same, too */
    for(uint32_t numRot = 0; numRot < totRots; numRot++) {
      if ( abs(getRotation(numRot).angle - sino.getRotation(numRot).angle)
            > TOLL_COMP )
      {
        return false;
      }
    }
  }
  return equalSizes;
}

template <typename TYPE>
void BaseGeometryTable<TYPE>::computeGeometryForSliceRotation(const size_t &sliceNum, const radians &angle, bool withInterpolation)
{
    (void)sliceNum;

    GeometryFactory geomFactory;
    geomFactory.setMatrDims(getMatrDims());

    const RayProperties<TYPE> rayProp = geomFactory.prepareTable(*this, true);

    reserve(1);

    geomFactory.addRotationIncomingRays(*this,angle,rayProp);

    /* It's now time to fill the table sampling the points in the active area */
    geomFactory.sampleTable(*this, true);
}


template <typename TYPE>
void BaseGeometryTable<TYPE>::computeGeometryForSliceRotation(const size_t &numSlice, const size_t &numRot, const GenericSinogram3D<TYPE> &sino, bool withInterpolation)
{
    GeometryFactory geomFactory;
    geomFactory.setMatrDims(getMatrDims());

    const RayProperties<TYPE> rayProp = geomFactory.prepareTable(*this, true);

    reserve(1);

    const GenericSinogramProj<TYPE> &sp = sino.getRotation(numSlice,numRot);
    geomFactory.addRotationIncomingRays(*this,sp.angle, rayProp);

    /* It's now time to fill the table sampling the points in the active area */
    geomFactory.sampleTable(*this, true);
}

template<typename TYPE>
RayPointCalculationMethod BaseGeometryTable<TYPE>::getRayPointCalculationMethod() const 
{ 
  assert(reconsParam);
  return reconsParam->getRayPointCalculationMethod(); 
}

template<typename TYPE>
OutgoingRayAlgorithm BaseGeometryTable<TYPE>::getOutgoingRayAlgorithm() const 
{ 
  assert(reconsParam);
  return reconsParam->getOutgoingRayAlgorithm(); 
}

template <typename TYPE>
void BaseGeometryTable<TYPE>::initRaysAllocation(const Dimensions_UI32& dims)
{
  uint32_t higherDim = max(max(dims.x, dims.y), dims.z);
  assert(higherDim > 0);
  // needed because we can sample until max(width, height) +1 point
  higherDim += 1;

  uint32_t incomingRaysMaxSize = reconsParam->getOverSampling() * higherDim;
  resizeIncomingRays(this->getTotIncomingRaysPerRot(), incomingRaysMaxSize, reconsParam->getRayPointCalculationMethod()==withInterpolation);

  bitset<MAX_TYPES> reconsType = reconsParam->getReconstructionType();
  if (reconsType.test(FLUORESCENCE_TYPE) == true ||
      reconsType.test(COMPTON_TYPE) == true ||
      reconsType.test(DIFFRACTION_TYPE) == true)
  {
    uint32_t outgoingRaysMaxSize = incomingRaysMaxSize;
    if(reconsParam->getOutgoingRayAlgorithm() == matriceSubdivision)
    {
      outgoingRaysMaxSize *= reconsParam->getSubdivisionSelfAbsMat();
    }
    resizeOutgoingRays(this->getTotOutgoingRaysPerRot(), outgoingRaysMaxSize, reconsParam->getRayPointCalculationMethod()==withInterpolation);  
  }
}


//--------------------------------------------------------------------------------------------------
//
//                  GeometryTable class methods
//
//--------------------------------------------------------------------------------------------------

template <typename TYPE>
GeometryTable<TYPE>::GeometryTable(const ReconstructionParameters<TYPE>& _reconsParam) : 
  BaseGeometryTable<TYPE>(_reconsParam),
  solidAngles(NULL),
  lossFractionIncident(NULL),
  selfAbsGeometries(0, BaseGeometryTable<TYPE>(_reconsParam)),
  selfAbsAttenuations(0, BinVec3D<TYPE>(0, 0, 0, 1.0))
{ }


template <typename TYPE>
void GeometryTable<TYPE>::clean()
{
  BaseGeometryTable<TYPE>::clean();
  DESTROY_C_ARRAY(solidAngles);
  DESTROY_C_ARRAY(lossFractionIncident);
}


template <typename TYPE>
void GeometryTable<TYPE>::reset()
{
  this->clean();
  this->clear();
}


template <typename TYPE>
void GeometryTable<TYPE>::setSelfAbsMatriceForFluo(BinVec3D<TYPE> mat)
{
  if(selfAbsAttenuations.size() == 1)
  {
    selfAbsAttenuations.set(0, 0, mat);
  }else{
      stringstream stream;
      stream << "GeometryTable : can t set the matrice of self absorption." ;
      stream << "Maybe the geometry haven t been well defined or the geometry table haven t been defined as a fluorescence geometry.";
      stream << " size = " << selfAbsAttenuations.size() << endl;
      throw BasicException(stream.str());
  }
}


template <typename TYPE>
void GeometryTable<TYPE>::createInitLossFractionIncident()
{
    ASSIGN_NEW_C_ARRAY(lossFractionIncident, new TYPE[(unsigned int)this->totSampledPoints]);
    for (uint64_t ind = 0;ind < this->totSampledPoints;ind++){
      lossFractionIncident[ind] = 1.0;
    }
}

// storing his rotation. So we should remove it from the constructor
template <typename TYPE>
void GeometryTable<TYPE>::computeGeometryForFluoDetector(const double _detAngle, const RayPointCalculationMethod beamCalculationMathod)
{
    GeometryFactory geomFactory;
    geomFactory.setMatrDims(this->getMatrDims());

    /* We rotate the matrix like if detector was emitting parallel rays */
    BaseGeometryTable<TYPE> & emGT = this->selfAbsGeometries[0];

    // TODO henri : each gt has his own incoming and outgoing rays, but this is not usefull. each gt can have only one set of rays.
    emGT.initRaysAllocation(this->getPhantomDims());

    /* The geometries of the self-absorption are just like the main geometry */
    DebugPrintf(("Generating self-absorption matrices for Fluo detector: 1\n"));
    geomFactory.createTableForOutgoingRays(emGT, _detAngle);
    geomFactory.sampleTableForOutgoingRays(emGT);
}

template <typename TYPE>
void GeometryTable<TYPE>::computeGeometryForDiffractDetector(const vector<double> &detAngles, const RayPointCalculationMethod beamCalculationMathod)
{
    GeometryFactory geomFactory;
    geomFactory.setMatrDims(this->getMatrDims());

    /* We rotate the matrix like if detectors were emitting parallel rays */
    const radians leftDetAngle  = detAngles[0];
    const radians rightDetAngle = detAngles[1];

    BaseGeometryTable<TYPE> & lemGT = selfAbsGeometries[0];
    BaseGeometryTable<TYPE> & remGT = selfAbsGeometries[1];

    radians leftDetAngleRot, rightDetAngleRot;
    leftDetAngleRot  = this->getRotation(0).angle + leftDetAngle;
    rightDetAngleRot = this->getRotation(0).angle + rightDetAngle;

    /* The geometries of the self-absorption are just like the main geometry */
    DebugPrintf(("Generating self-absorption matrices for Diffract detector: 1\n"));
    geomFactory.createTableForOutgoingRays(lemGT, leftDetAngleRot);
    geomFactory.sampleTableForOutgoingRays(lemGT);

    DebugPrintf(("Generating self-absorption matrices for Diffract detector: 2\n"));
    geomFactory.createTableForOutgoingRays(remGT, rightDetAngleRot);
    geomFactory.sampleTableForOutgoingRays(remGT);
}

} // End of FreeART namespace
