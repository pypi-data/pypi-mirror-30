//+==================================================================================================================
//
// GeometryFactory.cpp
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
 * GeometryFactory.cpp
 *
 *  Created on: Dec 20, 2010
 *      Author: vigano
 */

#include "GeometryFactory.h"

#include "RayHelpers.h"
#include "ScannerPhantom2D.h"

#include <sstream>
#ifdef HAVE_OMP
# include <omp.h>
#endif

#include <iostream>

namespace FREEART_NAMESPACE
{

//INLINE const Position_UI32
//GeometryFactory::guessPhantomDims(const uint32_t & sinoWidth,
//    const float_C & voxLength, const float_C & voxWidth)
//  const
const Dimensions_UI32
GeometryFactory::guessPhantomDims(const uint32_t & sinoWidth,
    const float_C & voxLength, const float_C & voxWidth)
  const
{
    double rayWidth = RAY_WIDTH;

    const uint32_t matrLength = _FT_UI32(ceil(sinoWidth*rayWidth/voxLength));
    const uint32_t matrWidth = _FT_UI32(ceil(sinoWidth*rayWidth/voxWidth));
    const uint32_t matrHeight = 1;

    return Dimensions_UI32(matrLength, matrWidth, matrHeight);
}

} // End of FreeART namespace
