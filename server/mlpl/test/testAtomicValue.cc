/*
 * Copyright (C) 2013 Project Hatohol
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

#include <cppcutter.h>
#include "AtomicValue.h"
using namespace mlpl;

namespace testAtomicValue {

// ---------------------------------------------------------------------------
// Test cases
// ---------------------------------------------------------------------------
void test_Define(void)
{
	AtomicValue<int> val;
}

void test_DefineWithInit(void)
{
	AtomicValue<int> val(5);
}

void test_get(void)
{
	int initValue = -3;
	AtomicValue<int> val(initValue);
	cppcut_assert_equal(initValue, val.get());
}

void test_setAndGet(void)
{
	int initValue = -3;
	AtomicValue<int> val;
	val.set(initValue);
	cppcut_assert_equal(initValue, val.get());
}

void test_add(void)
{
	const int initValue = 5;
	const int addedValue = 3;
	AtomicValue<int> val(initValue);
	cppcut_assert_equal(initValue + addedValue, val.add(addedValue));
}

void test_sub(void)
{
	const int initValue = 5;
	const int subValue = 3;
	AtomicValue<int> val(initValue);
	cppcut_assert_equal(initValue - subValue, val.sub(subValue));
}

void test_operatorEq(void)
{
	AtomicValue<int> val0(0);
	AtomicValue<int> val1(0);
	val0 = val1 = 3;
	cppcut_assert_equal(3, val0.get());
	cppcut_assert_equal(3, val1.get());
}

void test_operatorCast(void)
{
	AtomicValue<int> val(7);
	int i = val;
	cppcut_assert_equal(7, i);
}

} // namespace testAtomicValue
