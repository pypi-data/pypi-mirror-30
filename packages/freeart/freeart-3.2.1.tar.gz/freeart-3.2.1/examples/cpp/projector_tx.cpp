//+==================================================================================================================
//
// projector_tx.cpp
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
///    ./projector_tx
///    // And see the result
///    pymcapostbatch out_V2_tx_proj.edf
/// @endcode

#include "FreeART.h"
#include "edfwriter.h"
#include "Sinogram.h"
#include "FileHandling.h"

#include <iostream>

using namespace std;

int main(int argc, char *argv[]){
    cout << "setting the projection " << endl;

    string phantomFileName = string("../../python_utils/phantomSheppLogan256_3D.tmp");

    FreeART::AlgorithmIO algoIO;
    FreeART::BinVec3D<double> phantom;

    FreeART::SinogramsGeometry sinosGeo;

    cout << "setting the algorithm" << endl;
    algoIO.prepareSinogramGeneration(phantomFileName, 0.0, 2.0*M_PI, 210, phantom, sinosGeo);


    FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>* al = new FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>(phantom,sinosGeo);
    assert(al != NULL);
    al->setOverSampling(10);

    cout << "generate the sinogram " << endl;
    al->makeSinogram();
    FREEART_NAMESPACE::GenericSinogram3D<double> sinogram = al->getSinogram();

    cout << "saving data" << endl;
    write_data_to_edf(sinogram, "out_V2_tx_proj.edf");

    FREEART_NAMESPACE::TextWriter tl("out_V2_tx_proj.tmp");
    tl.writeSinogramToFile(sinogram);

    delete al;
    return 0;
}

