/*
 * Copyright (C) 2014 Project Hatohol
 *
 * This file is part of Hatohol.
 *
 * Hatohol is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License, version 3
 * as published by the Free Software Foundation.
 *
 * Hatohol is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Hatohol. If not, see <http://www.gnu.org/licenses/>.
 *
 * Additional permission under GNU GPL version 3 section 7
 *
 * If you modify this program, or any covered work, by linking or
 * combining it with the OpenSSL project's OpenSSL library (or a
 * modified version of that library), containing parts covered by the
 * terms of the OpenSSL or SSLeay licenses, Project Hatohol
 * grants you additional permission to convey the resulting work.
 * Corresponding Source for a non-source form of such a combination
 * shall include the source code for the parts of OpenSSL used as well
 * as that of the covered work.
 */

#include <string>
#include <vector>
using namespace std;

#include <cutter.h>
#include <cppcutter.h>
#include <gcutter.h>

#include "SeparatorInjector.h"
using namespace mlpl;

namespace testSeparatorInejector {

void test_basicFeature(void)
{
	string str = "ABC";
	SeparatorInjector sepInj(",");
	sepInj(str);
	cppcut_assert_equal(string("ABC"), str);

	sepInj(str);
	cppcut_assert_equal(string("ABC,"), str);

	str += "DOG!";
	sepInj(str);
	cppcut_assert_equal(string("ABC,DOG!,"), str);
}

void test_clear(void)
{
	string str = "ABC";
	SeparatorInjector sepInj(",");
	sepInj(str);
	cppcut_assert_equal(string("ABC"), str);

	sepInj.clear();
	sepInj(str);
	cppcut_assert_equal(string("ABC"), str);
}

} // namespace testSeparatorInejector
