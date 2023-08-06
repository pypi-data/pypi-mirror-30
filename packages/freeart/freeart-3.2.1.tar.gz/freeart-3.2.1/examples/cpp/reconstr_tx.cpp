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
/// Note : This is a short code to call the forward projection of the transmission.
///  for this example we are picking the sinogram created by the projector_tx.cpp example.
/// ./reconstr_tx 8 out_V2_tx_proj.tmp reconstructed_phantom_tx_V2.edf


#include <FreeART.h>
#include <edfwriter.h>

#include <iostream>
#include <unistd.h>

using namespace std;

int main(int argc, char** argv)
{
    if (argc !=4 )
    {
        cerr << "reconstr usage: reconstr <iter nb> <Sinogram File> <Output File>" << endl;
        return EXIT_FAILURE;
    }

    // the number of iteration we want to make for the reconstruction
    uint32_t iterNb = (uint32_t)atoi(argv[1]);
    string outFile;

    // the file containing the sinogram file
    string sinoFile(argv[2]);

    outFile = argv[3];

    FreeART::SinogramsGeometry sinosGeo;
    FreeART::Sinograms3D<double> sinos;
    FreeART::AlgorithmIO algoIO;

    // no need to define a detector for the transmission reconstruction
    FreeART::ExperimentSetUp esu;
    try
    {
        // set up the geometry (sinosgeo) and the stack of sinogram (sinos)
        // from a sinoFile and an experiemt setup.
        // Here because we are in the transmission case, the experiment setup can be empty of detector
        algoIO.buildSinogramGeometry(sinoFile, esu, sinos, sinosGeo);

        // create the transmission reconstruction
        FreeART::SARTAlgorithm<double,FreeART::TxReconstruction> *al;
        al = new FreeART::SARTAlgorithm<double,FreeART::TxReconstruction>(sinos,sinosGeo);
        al->setDampingFactor(0.1);
        al->setOverSampling(6);
        // launch the reconstruction over iterNb iterations
        al->doWork(iterNb);

        // get the reconstructed phantom
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

    return EXIT_SUCCESS;
}


