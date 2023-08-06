//+==================================================================================================================
//
// units.h
//
//
// Copyright (C) :      2014,2015, 2016
//                      European Synchrotron Radiation Facility
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
 * units.h
 *
 *  Created on: July, 2016
 *      Author: payno
 */

#ifndef UNITS_HH
#define UNITS_HH

namespace FREEART_NAMESPACE
{

namespace UNITS
{

/// metric
static const double centimeter = 1.0;
static const double cm = centimeter;
static const double millimeter = 0.1*centimeter;
static const double mm = millimeter;
static const double meter = 100.0*centimeter;
static const double m = meter;

static const double mm2 = millimeter*millimeter;
static const double cm2 = centimeter*centimeter;
static const double m2 = meter*meter;
static const double nanometer = 1e-9*meter;
static const double nm = nanometer;

}// end namespace UNITS

}// end namespace FREEART_NAMESPACE

#endif // UNITS_HH