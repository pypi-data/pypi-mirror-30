//+==================================================================================================================
//
// newreconstr.cpp
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
/// Note : This is a short code to call the fluorescence reconstruction.
///  for this example we are picking the sinogram created by the projector_fluo.cpp example.
/// ./reconstr_fluo 8 out_V2_fluo_proj.tmp ../../python_utils/phantomSheppLogan256_3D.tmp ../../python_utils/phantomSheppLogan256_3D.tmp  reconstructed_phantom_fluo_V2.edf

#include <FreeART.h>
#include <edfwriter.h>

#include <iostream>
#include <units.h>
using namespace std;
using namespace FREEART_NAMESPACE;

int main(int argc, char** argv)
{
    if (argc != 6 )
    {
        cerr << "reconstr usage: reconstr <iter nb> <Sinogram File> <Sample Absorption volume File> <Sample Self absorption volume File > <Output File>" << endl;
        return EXIT_FAILURE;
    }

    uint32_t iterNb = (uint32_t)atoi(argv[1]);
    string outFile, absorpFile, selfAbsorpFile;
    FreeART::BinVec3D<double> absorpMatr;
    FreeART::BinVec3D<double> selfAbsorpMatr;

    string sinoFile(argv[2]);

    absorpFile = argv[3];
    selfAbsorpFile = argv[4];
    outFile = argv[5];

    // define the detector ( cf : compton reconstruction )
    FreeART::ExperimentSetUp esu(1, FreeART::DetectorSetUp(FreeART::Position_FC(1000.0*UNITS::cm, 0.0,0.0), 10*UNITS::cm));
    // The fluorescence detector ?

    FreeART::SinogramsGeometry sinosGeo;
    FreeART::Sinograms3D<double> sinos;
    FreeART::AlgorithmIO algoIO;

    // first way without changing the absoption matrices
    {
        try
        {
            algoIO.buildSinogramGeometry(sinoFile,esu,sinos,sinosGeo);

            //load abs ans selfAbs matrices
            algoIO.loadAbsorptionMatrix(absorpFile, absorpMatr);
            algoIO.loadAbsorptionMatrix(selfAbsorpFile, selfAbsorpMatr);
            
            // create the fluorescence reconstruction
            FreeART::SARTAlgorithm<double,FreeART::FluoReconstruction> *al;
            al = new FreeART::SARTAlgorithm<double,FreeART::FluoReconstruction>(sinos, absorpMatr, selfAbsorpMatr, sinosGeo);
            al->setDampingFactor(0.05);
            al->setOverSampling(8);            
            // Launch the reconstruction on itterNb iterations
            al->doWork(iterNb);

            const FreeART::BinVec3D<double>* v = &(al->getPhantom());
            write_data_to_edf(static_cast<const std::vector<double>*> (v), v->getLength(), v->getWidth(), outFile.c_str());

            delete al;
        }
        catch (FreeART::BasicException &e)
        {
            cerr << "Received FreeART exception" << endl;
            cerr << e.getMessage() << endl;
            return EXIT_FAILURE;
        }
        catch (...)
        {
            cerr << "Received unforeseen exception.... " << endl;
            return EXIT_FAILURE;
        }
    }
    return EXIT_SUCCESS;
}


