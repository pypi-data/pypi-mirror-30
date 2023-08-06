//+==================================================================================================================
//
// AlgoIO.tpp
//
//
// Copyright (C) :      2015
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
 * AlgoIO.tpp
 *
 *  Created on: Jan, 2015
 *      Author: taurel
 */

#include "AlgoIO.h"
#include <iostream>
#include <math.h>

namespace FREEART_NAMESPACE
{

void DetectorGeometry::reset(const size_t nbElt)
{
    Ci.reset(nbElt);
    di.reset(nbElt);
    Di.reset(nbElt);
    Ui.reset(nbElt);
    Vi.reset(nbElt);
}

void SinogramsGeometry::printIt()
{
    for (size_t loop = 0;loop < bi.size();loop++)
    {
        cout << "bi[" << loop << "] = {" << bi[loop].x << ", " << bi[loop].y << ", " << bi[loop].z << "}" << endl;
        for (size_t ctr = 0;ctr < dets.size();ctr++)
        {
            Position_FC CiPoint = dets[ctr].getCi(loop);
            cout << "\tCi = {" << CiPoint.x << ", " << CiPoint.y << ", " << CiPoint.z << "}" << endl;
            Position_FC diPoint = dets[ctr].getdi(loop);
            cout << "\tdi = {" << diPoint.x << ", " << diPoint.y << ", " << diPoint.z << "}" << endl;
            Position_FC DiPoint = dets[ctr].getDi(loop);
            cout << "\tDi = {" << DiPoint.x << ", " << DiPoint.y << ", " << DiPoint.z << "}" << endl;
            Position_FC UiPoint = dets[ctr].getUi(loop);
            cout << "\tUi = {" << UiPoint.x << ", " << UiPoint.y << ", " << UiPoint.z << "}" << endl;
            Position_FC ViPoint = dets[ctr].getVi(loop);
            cout << "\tVi = {" << ViPoint.x << ", " << ViPoint.y << ", " << ViPoint.z << "}" << endl;
        }
    }
}

template <typename TYPE>
void AlgorithmIO::buildSinogramGeometry(const string &sinoFile,const ExperimentSetUp &esu,Sinograms3D<TYPE> &sinos,SinogramsGeometry &sinosGeo)
{
    size_t fileNb = 1;
    size_t detNb = esu.size();

//
// Resize output parameters
//

    sinos.reset(fileNb);
    sinosGeo.reset(detNb);

//
// Read the sinogram
//

    AnglesArray aa0;
    TextLoader tl(sinoFile.c_str());
    tl.readSinogram(sinos.get(0),aa0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,sinosGeo);

//
// Compute detector geometry
//

    computeDetGeo(sinosGeo,aa0,esu);
}

template <typename TYPE>
void AlgorithmIO::buildSinogramGeometry(const string &sinoFile,Sinograms3D<TYPE> &sinos,SinogramsGeometry &sinosGeo)
{
    size_t fileNb = 1;

//
// Resize output parameters
//

    sinos.reset(fileNb);
    sinosGeo.reset(0);

//
// Read the sinogram
//

    AnglesArray aa0;
    TextLoader tl(sinoFile.c_str());
    tl.readSinogram(sinos.get(0),aa0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,sinosGeo);
}

template <typename TYPE>
void AlgorithmIO::buildSinogramGeometry(const double *_aa,
                                        const TYPE *_dat,
                                        const size_t _sliceNb,
                                        const size_t _anglesNb,
                                        const size_t _pointNb,
                                        const ExperimentSetUp &_esu,
                                        Sinograms3D<TYPE> &_sinos,
                                        SinogramsGeometry &_sinosGeo)
{
    DebugPrintf(("Received %zu slice(s), %zu angles with %zu points\n",_sliceNb,_anglesNb,_pointNb));

    size_t fileNb = 1;
    size_t detNb = _esu.size();

//
// Resize output parameters
//

    _sinos.reset(fileNb);
    _sinosGeo.reset(detNb);

//
// Create angle array
//

    AnglesArray aa0;
    aa0.assign(_aa,_aa + _anglesNb);

//
// Load sinogram data
//

    GenericSinogram3D<TYPE> &sino = _sinos.get(0);
    sino.reset(_sliceNb,_anglesNb,_pointNb);

    for (uint32_t rot = 0;rot < _anglesNb;rot++)
    {
       sino.getRotation(0,rot).angle = aa0[rot];
    }

    for(uint32_t slice = 0; slice < _sliceNb; slice++)
    {
        for (uint32_t rot = 0;rot < _anglesNb;rot++)
        {
            GenericSinogramProj<TYPE> &rotation = sino.getRotation(slice,rot);
            rotation.resize(_pointNb);
            for (uint32_t ray = 0;ray < _pointNb;ray++)
            {
                uint32_t ind = (slice * (_anglesNb * _pointNb)) + (rot * _pointNb) + ray;
                rotation.getPoint(ray) = _dat[ind];
            }
        }
    }

    for (uint32_t slice=1;slice < _sliceNb;slice++)
    {
        for (uint32_t rot = 0;rot < _anglesNb;rot++)
        {
            sino.getRotation(slice,rot).angle = sino.getRotation(0,rot).angle;
        }
    }

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,_sinosGeo);

//
// Compute detector geometry
//

    computeDetGeo(_sinosGeo,aa0,_esu);
}


template <typename TYPE>
void AlgorithmIO::buildSinogramGeometryTx(const double *_aa,
                                        const TYPE *_dat,
                                        const size_t _sliceNb,
                                        const size_t _anglesNb,
                                        const size_t _pointNb,
                                        Sinograms3D<TYPE> &_sinos,
                                        SinogramsGeometry &_sinosGeo)
{
    DebugPrintf(("Received %zu slice(s), %zu angles with %zu points\n",_sliceNb,_anglesNb,_pointNb));
    size_t fileNb = 1;

//
// Resize output parameters
//

    _sinos.reset(fileNb);
    _sinosGeo.reset(0);

//
// Create angle array
//

    AnglesArray aa0;
    aa0.assign(_aa,_aa + _anglesNb);

//
// Load sinogram data
//

    GenericSinogram3D<TYPE> &sino = _sinos.get(0);
    sino.reset(_sliceNb,_anglesNb,_pointNb);

    for (uint32_t rot = 0;rot < _anglesNb;rot++)
    {
       sino.getRotation(0,rot).angle = aa0[rot];
    }

    for(uint32_t slice = 0; slice < _sliceNb; slice++)
    {
        for (uint32_t rot = 0;rot < _anglesNb;rot++)
        {
            GenericSinogramProj<TYPE> &rotation = sino.getRotation(slice,rot);
            rotation.resize(_pointNb);
            for (uint32_t ray = 0;ray < _pointNb;ray++)
            {
                uint32_t ind = (slice * (_anglesNb * _pointNb)) + (rot * _pointNb) + ray;
                rotation.getPoint(ray) = _dat[ind];
            }
        }
    }

    for (uint32_t slice=1;slice < _sliceNb;slice++)
    {
        for (uint32_t rot = 0;rot < _anglesNb;rot++)
        {
            sino.getRotation(slice,rot).angle = sino.getRotation(0,rot).angle;
        }
    }

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,_sinosGeo);
}


void AlgorithmIO::sinoAnglesTobVersor(AnglesArray &aa0,SinogramsGeometry &sinosGeo)
{
    size_t angleNb = aa0.size();
    sinosGeo.getbi().reset(angleNb);

    for (size_t i = 0;i < angleNb;i++)
    {
        FreeART::radians teta = aa0.get(i);
        // henri
        // sinosGeo.getbi(i) = Position_FC(cos(tetaRadian),sin(tetaRadian),0.0);
        sinosGeo.getbi(i) = Position_FC(sin(teta),cos(teta),0.0);
    }
}

void AlgorithmIO::computeDetGeo(SinogramsGeometry &sinosGeo,const AnglesArray &aa0,const ExperimentSetUp &esu)
{
    size_t angleNb = aa0.size();
    size_t detNb = sinosGeo.detNb();

    for (size_t loop = 0;loop < detNb;loop++)
    {

//
// Create entries for all geometry element
//

        DetectorGeometry &detGeo = sinosGeo.getDetectorsGeometry().get(loop);
        detGeo.reset(angleNb);

//
// Compute alpha angle (in radian)
//

        FreeART::radians teta = aa0.get(0);
        const Position_FC &detCenter = esu[loop].getDetectorCenter();
        const double Xc0 = detCenter.x;
        const double Yc0 = detCenter.y;
        double norm_s = detCenter.norm();
        double alpha = acos((sin(teta) * (Xc0 / norm_s)) + (cos(teta) * (Yc0 / norm_s)));
        // double alpha = acos((cos(teta) * (Xc0 / norm_s)) + (sin(teta) * (Yc0 / norm_s)));
        if (Yc0 < 0)
            alpha = -alpha;

        double detLength = esu[loop].getDetLength();
        double x,y;

        for (size_t i = 0;i < angleNb;i++)
        {

//
// Compute all the Ci (si)
// Today (Jan 2015), the di are the same than the Ci
//

            if (i == 0)
            {
                 detGeo.getCi(0) = Position_FC(detCenter.x,detCenter.y,detCenter.z);
                 x = detCenter.x;
                 y = detCenter.y;
            }
            else
            {
                // double x1 = cos(alpha) * sinosGeo.getbi().get(i).x;
                // double x2 = -sin(alpha) * sinosGeo.getbi().get(i).y;
                double x1 = sin(alpha) * sinosGeo.getbi().get(i).x;
                double x2 = -cos(alpha) * sinosGeo.getbi().get(i).y;


                x = (x1 + x2) * norm_s;

                // double y1 = sin(alpha) * sinosGeo.getbi().get(i).x;
                // double y2 = cos(alpha) * sinosGeo.getbi().get(i).y;
                double y1 = cos(alpha) * sinosGeo.getbi().get(i).x;
                double y2 = sin(alpha) * sinosGeo.getbi().get(i).y;

                y = (y1 + y2) * norm_s;

                detGeo.getCi(i) = Position_FC(x,y,0.0);
                detGeo.getdi(i) = Position_FC(x,y,0.0);
            }

//
// Compute the Di and Ui
//

            double tmp_You = (detLength * x) / detGeo.getCi(i).norm();
            double tmp_Xou;
            if (x == 0.0)
                tmp_Xou = detLength;
            else
                tmp_Xou = (-tmp_You * y) / x;

            double halfX = tmp_Xou / 2;
            double halfY = tmp_You / 2;

            detGeo.getDi(i) = Position_FC(x - halfX,y - halfY,0.0);
            detGeo.getUi(i) = Position_FC(x + halfX,y + halfY,0.0);

//
// The Vi are all 0 until real 3D is implemented
//

            detGeo.getVi(i) = Position_FC(0.0,0.0,0.0);
        }
    }
}

template <typename TYPE>
void AlgorithmIO::savePhantomToFile(const string &outFileName,const BinVec3D<TYPE> &ph)
{
    TextWriter writer(outFileName);
    writer.writePhantomToFile(ph);
}

template <typename TYPE>
void AlgorithmIO::savePhantomToFile(const string &outFileName,const Algorithm<TYPE> &al)
{
    savePhantomToFile(outFileName,al.getPhantom());
}

template <typename TYPE>
void AlgorithmIO::saveSinogramToFile(const string &outFileName,const GenericSinogram3D<TYPE> &sino)
{
    TextWriter writer(outFileName);
    writer.writeSinogramToFile(sino);
}

template <typename TYPE>
void AlgorithmIO::saveSinogramToFile(const string &outFileName,const Algorithm<TYPE> &al)
{
    saveSinogramToFile(outFileName,al.getSinogram());
}

template <typename TYPE>
void AlgorithmIO::loadAbsorptionMatrix(const string &absorpFileName,BinVec3D<TYPE> &matr)
{
    TextLoader absorpReader(absorpFileName);
    absorpReader.readAbsorp(matr);
}

template <typename TYPE>
void AlgorithmIO::prepareSinogramGeneration(const string &absorpFileName,AnglesArray &aa0,
                                            BinVec3D<TYPE> &matr,SinogramsGeometry &sinosGeo)
{
    TextLoader absorpReader(absorpFileName);
    absorpReader.readAbsorp(matr);

    sinosGeo.reset(0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,sinosGeo);
}

template <typename TYPE>
void AlgorithmIO::prepareSinogramGeneration(const string &absorpFileName,const double minAngle,const double maxAngle,
                                            size_t angleNb,BinVec3D<TYPE> &matr,SinogramsGeometry &sinosGeo)
{
    TextLoader absorpReader(absorpFileName);
    absorpReader.readAbsorp(matr);

    sinosGeo.reset(0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    AnglesArray geoAngles;
    geoAngles.setFixedSpaceAngles(angleNb,minAngle,maxAngle);
    sinoAnglesTobVersor(geoAngles,sinosGeo);
}

template <typename TYPE>
void AlgorithmIO::prepareSinogramGeneration(const string &absorpFileName,const ExperimentSetUp &esu,AnglesArray &aa0,
                                   BinVec3D<TYPE> &matr,SinogramsGeometry &sinosGeo)
{
    TextLoader absorpReader(absorpFileName);
    absorpReader.readAbsorp(matr);

    sinosGeo.reset(esu.size());

    sinoAnglesTobVersor(aa0,sinosGeo);
    computeDetGeo(sinosGeo,aa0,esu);
}

template <typename TYPE>
void AlgorithmIO::prepareSinogramGeneration(const string &absorpFileName,const ExperimentSetUp &esu,const double minAngle,
                                   const double maxAngle,const size_t angleNb,BinVec3D<TYPE> &matr,
                                   SinogramsGeometry &sinosGeo)
{
    TextLoader absorpReader(absorpFileName);
    absorpReader.readAbsorp(matr);

    AnglesArray geoAngles;
    geoAngles.setFixedSpaceAngles(angleNb,minAngle,maxAngle);

    sinosGeo.reset(esu.size());

    sinoAnglesTobVersor(geoAngles,sinosGeo);
    computeDetGeo(sinosGeo,geoAngles,esu);
}

template <typename TYPE>
void AlgorithmIO::createMatr(const TYPE *_dat,const size_t _length,const size_t _width,
                            const size_t _height,BinVec3D<TYPE> &_matr)
{
    _matr.reset(_length,_width,_height);
    _matr.assign(_dat,_dat + (_length * _width * _height));
}

template <typename TYPE>
void AlgorithmIO::createAnglesArray(const TYPE *_dat,const size_t _anglesNb,AnglesArray _aa)
{
    _aa.reset(_anglesNb);
    _aa.assign(_dat,_dat + _anglesNb);
}

void AlgorithmIO::prepareSinogramGeneration(AnglesArray &aa0,SinogramsGeometry &sinosGeo)
{
    sinosGeo.reset(0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    sinoAnglesTobVersor(aa0,sinosGeo);
}

void AlgorithmIO::prepareSinogramGeneration(const double minAngle,const double maxAngle,
                                            size_t angleNb,SinogramsGeometry &sinosGeo)
{
    sinosGeo.reset(0);

//
// Convert sinogram angles to b versor (only for first detector)
//

    AnglesArray geoAngles;
    geoAngles.setFixedSpaceAngles(angleNb,minAngle,maxAngle);
    sinoAnglesTobVersor(geoAngles,sinosGeo);
}

void AlgorithmIO::prepareSinogramGeneration(const ExperimentSetUp &esu,AnglesArray &aa0,SinogramsGeometry &sinosGeo)
{
    sinosGeo.reset(esu.size());

    sinoAnglesTobVersor(aa0,sinosGeo);
    computeDetGeo(sinosGeo,aa0,esu);
}



void AlgorithmIO::prepareSinogramGeneration(const ExperimentSetUp &esu,const double minAngle,
                                   const double maxAngle,const size_t angleNb,SinogramsGeometry &sinosGeo)
{
    AnglesArray geoAngles;
    geoAngles.setFixedSpaceAngles(angleNb,minAngle,maxAngle);

    sinosGeo.reset(esu.size());

    sinoAnglesTobVersor(geoAngles,sinosGeo);
    computeDetGeo(sinosGeo,geoAngles,esu);
}

} // End of FreeART namespace
