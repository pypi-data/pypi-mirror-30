//+==================================================================================================================
//
// Exceptions.h
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
 * Exceptions.h
 *
 *  Created on: 7 oct. 2010
 *      Author: vigano
 */

#ifndef EXCEPTIONS_H_
#define EXCEPTIONS_H_

#include <stdexcept>
#include <string>

using namespace std;

namespace FREEART_NAMESPACE
{

class BasicException : public ::exception {
  string message;

  exception nestedEx;

public:
  BasicException() { }
  BasicException(const char * _mess) : message(_mess) { }
  BasicException(const string& _mess) : message(_mess) { }
  BasicException(const BasicException& _ex)
        : exception(_ex), message(_ex.message), nestedEx(_ex.nestedEx) { }
  BasicException(const string & _mess, const BasicException& _ex)
        : message(_mess), nestedEx(_ex) { }

  virtual ~BasicException() throw() { }

  virtual const char * what() const throw() { return message.c_str(); }
  const string& getMessage() const throw() { return message; }
  const exception & getNestedException() const throw() { return nestedEx; }

  virtual void setMessage(const string& _mess) { message = _mess; }
  virtual void appendMessage(const string& _mess) { message += _mess; }
  virtual void prefixMessage(const string& _mess) { message = _mess + message; }
};

class WrongFileException : public BasicException {
public:
  WrongFileException() { }
  WrongFileException(const WrongFileException &_ex)
        : BasicException(_ex) { }
  WrongFileException(const char * _mess) : BasicException(_mess) { }
  WrongFileException(const string& _mess) : BasicException(_mess) { }
  WrongFileException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class WrongArgException : public BasicException {
public:
  WrongArgException() { }
  WrongArgException(const WrongArgException &_ex)
        : BasicException(_ex) { }
  WrongArgException(const char * _mess) : BasicException(_mess) { }
  WrongArgException(const string& _mess) : BasicException(_mess) { }
  WrongArgException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class NotInitializedObjException : public BasicException {
public:
  NotInitializedObjException() { }
  NotInitializedObjException(const NotInitializedObjException &_ex)
        : BasicException(_ex) { }
  NotInitializedObjException(const char * _mess) : BasicException(_mess) { }
  NotInitializedObjException(const string& _mess) : BasicException(_mess) { }
  NotInitializedObjException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class BadSolidAngleException : public BasicException {
public:
  BadSolidAngleException() { }
  BadSolidAngleException(const BadSolidAngleException &_ex)
        : BasicException(_ex) { }
  BadSolidAngleException(const char * _mess) : BasicException(_mess) { }
  BadSolidAngleException(const string& _mess) : BasicException(_mess) { }
  BadSolidAngleException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class NotImplementedException : public BasicException {
public:
  NotImplementedException() { }
  NotImplementedException(const NotImplementedException &_ex)
        : BasicException(_ex) { }
  NotImplementedException(const char * _mess) : BasicException(_mess) { }
  NotImplementedException(const string& _mess) : BasicException(_mess) { }
  NotImplementedException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class InitializationException : public BasicException {
public:
  InitializationException() { }
  InitializationException(const InitializationException &_ex)
        : BasicException(_ex) { }
  InitializationException(const char * _mess) : BasicException(_mess) { }
  InitializationException(const string& _mess) : BasicException(_mess) { }
  InitializationException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

class OutOfBoundException : public BasicException {
public:
  OutOfBoundException() { }
  OutOfBoundException(const OutOfBoundException &_ex)
        : BasicException(_ex) { }
  OutOfBoundException(const char * _mess) : BasicException(_mess) { }
  OutOfBoundException(const string& _mess) : BasicException(_mess) { }
  OutOfBoundException(const string& _mess, const BasicException& _ex)
        : BasicException(_mess, _ex) { }
};

} // End of FreeART namespace

#endif /* EXCEPTIONS_H_ */
