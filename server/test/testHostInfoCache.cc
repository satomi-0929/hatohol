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

#include <cppcutter.h>
#include "HostInfoCache.h"
using namespace std;

namespace testHostInfoCache {

// ---------------------------------------------------------------------------
// Test cases
// ---------------------------------------------------------------------------

void test_updateAndGetName(void)
{
	HostInfo hostInfo;
	hostInfo.serverId = 100;
	hostInfo.id = 2;
	hostInfo.hostName = "foo";

	HostInfoCache hiCache;
	hiCache.update(hostInfo);
	string name;
	cppcut_assert_equal(true, hiCache.getName(hostInfo.id, name));
	cppcut_assert_equal(hostInfo.hostName, name);
}

void test_getNameExpectFalse(void)
{
	HostInfo hostInfo;
	hostInfo.serverId = 100;
	hostInfo.id = 2;
	hostInfo.hostName = "foo";

	HostInfoCache hiCache;
	hiCache.update(hostInfo);
	string name;
	cppcut_assert_equal(false, hiCache.getName(500, name));
}

void test_updateTwice(void)
{
	HostInfo hostInfo;
	hostInfo.serverId = 100;
	hostInfo.id = 2;
	hostInfo.hostName = "foo";

	HostInfoCache hiCache;
	hiCache.update(hostInfo);
	string name;
	cppcut_assert_equal(true, hiCache.getName(hostInfo.id, name));
	cppcut_assert_equal(hostInfo.hostName, name);

	// update again
	hostInfo.hostName = "Dog Dog Dog Cat";
	hiCache.update(hostInfo);
	cppcut_assert_equal(true, hiCache.getName(hostInfo.id, name));
	cppcut_assert_equal(hostInfo.hostName, name);
}

void test_getNameFromMany(void)
{
	struct DataArray {
		HostIdType id;
		const char *name;
	} dataArray [] = {
		{105,   "You"},
		{211,   "Hydrogen"},
		{5,     "foo"},
		{10555, "3K background radition is not 4K display"},
		{4,     "I like strawberry."},
	};
	const size_t numData = ARRAY_SIZE(dataArray);

	HostInfoCache hiCache;
	for (size_t i = 0; i < numData; i++) {
		HostInfo hostInfo;
		hostInfo.serverId = 100;
		hostInfo.id = dataArray[i].id;
		hostInfo.hostName = dataArray[i].name;
		hiCache.update(hostInfo);
	}

	// check
	for (size_t i = 0; i < numData; i++) {
		string name;
		const HostIdType id = dataArray[i].id;
		cppcut_assert_equal(true, hiCache.getName(id, name));
		cppcut_assert_equal(string(dataArray[i].name), name);
	}
}

} // namespace testHostInfoCache
