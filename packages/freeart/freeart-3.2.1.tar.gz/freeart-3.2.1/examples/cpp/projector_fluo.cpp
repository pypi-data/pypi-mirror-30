//+==================================================================================================================
//
// projector_fluo.cpp
//
//
// Copyright (C) :      2014,2015
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
/// Note : in order to run this test you should already have generate the phantomSheppLogan256_3D file
/// That you can generate by calling the genph.py script : 
/// @code :
///  python genph.py phantomSheppLogan256_3D.tmp
/// @endcode
///
/// Then you can call this script :
/// @code
///    ./projector_fluo
///    // And see the result
///    pymcapostbatch out_V2_tx_proj.edf
/// @endcode

#include <FreeART.h>
#include <iostream>
#include <edfwriter.h>
#include <Sinogram.h>
#include <FileHandling.h>
#include <units.h>

#include <string>

static unsigned int i_out = 0;

using namespace std;
using namespace FREEART_NAMESPACE;

enum PROJECTION_MODE{PHANTOM_ONLY, PHANTOM_AND_SELF_ABS, PHANTOM_AND_ABS_MATRIX, PHANTOM_AND_ABS_AND_SELF_ABS};

string getOutFileName(PROJECTION_MODE opt){
  switch(opt){
    case PHANTOM_ONLY:{
      i_out++;
      return string("compton");
    }
    case PHANTOM_AND_SELF_ABS:{
      return "phantom_and_self_abs";
    }
    case PHANTOM_AND_ABS_MATRIX:{
      return "phantom_and_abs_matrix";
    }
    case PHANTOM_AND_ABS_AND_SELF_ABS:{
      return "all_in";
    }
  }
}

// projectionMode
int main(int argc, char *argv[]){

    string phantomFileName = string("phantomSheppLogan256_3D.tmp");
    string absorpMatrixFileName = string("phantomSheppLogan256_3D.tmp");
    string selfAbsorpMatrixFileName = string("phantomSheppLogan256_3D.tmp");

    FreeART::AlgorithmIO algoIO;
    FreeART::BinVec3D<float> phantom;
    FreeART::BinVec3D<float> absorpMatrix;
    FreeART::BinVec3D<float> selfAbsorpMatrix;

    cout << "setting the projection " << endl;
    FreeART::ExperimentSetUp esu(1,FreeART::DetectorSetUp(FreeART::Position_FC(-1000.0*UNITS::cm, 0.0, 0.0), 10*UNITS::cm));
    
    FreeART::SinogramsGeometry sinosGeo;

    algoIO.prepareSinogramGeneration(phantomFileName, esu, 0.0, 2.0*M_PI, 200, phantom, sinosGeo);
    algoIO.loadAbsorptionMatrix(absorpMatrixFileName, absorpMatrix);
    algoIO.loadAbsorptionMatrix(selfAbsorpMatrixFileName, selfAbsorpMatrix);
    
    FreeART::SARTAlgorithm<float,FreeART::FluoReconstruction> *al = NULL;
    al = new FreeART::SARTAlgorithm<float,FreeART::FluoReconstruction>(phantom, absorpMatrix, selfAbsorpMatrix, sinosGeo);

    assert(al != NULL);
    // set the non negative effect
    al->setLowerLimit(0.0);
    al->setOverSampling(10);

    // generate the sinogram
    cout << "generate the sinogram " << endl;
    al->makeSinogram();
    GenericSinogram3D<float> sinogram = al->getSinogram();

    string outSinoFileName = string("out_V2_fluo.edf");

    cout << "saving data" << endl;
    write_data_to_edf(sinogram, outSinoFileName.c_str());
    FREEART_NAMESPACE::TextWriter tl("out_V2_fluo_proj.tmp");
    tl.writeSinogramToFile(sinogram);

    delete al;
    return 0;
}

