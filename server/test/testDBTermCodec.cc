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
#include <gcutter.h>
#include "DBTermCodec.h"
#include "DBAgentSQLite3.h"
#include "DataSamples.h"

using namespace std;

namespace testDBTermCodec {

void data_getInt(void)
{
	addDataSamplesForGCutInt();
}

void test_getInt(gconstpointer data)
{
	DBTermCodec dbTermCodec;
	string actual = dbTermCodec.enc(gcut_data_get_int(data, "val"));
	string expect = gcut_data_get_string(data, "expect");
	cppcut_assert_equal(expect, actual);
}

void data_getUint64(void)
{
	gcut_add_datum("Zero",
		       "val", G_TYPE_UINT64, (guint64)0,
		       "expect", G_TYPE_STRING, "0",
		       NULL);
	gcut_add_datum("Positive within 32bit",
		       "val", G_TYPE_UINT64, (guint64)3456,
		       "expect", G_TYPE_STRING, "3456",
		       NULL);
	gcut_add_datum("Positive 32bit Max",
		       "val", G_TYPE_UINT64, (guint64)2147483647,
		       "expect", G_TYPE_STRING, "2147483647",
		       NULL);
	gcut_add_datum("Positive 32bit Max + 1",
		       "val", G_TYPE_UINT64, (guint64)G_MAXINT32 + 1,
		       "expect", G_TYPE_STRING, "2147483648",
		       NULL);
	gcut_add_datum("Positive 64bit Poistive Max",
		       "val", G_TYPE_UINT64, 9223372036854775807UL,
		       "expect", G_TYPE_STRING, "9223372036854775807",
		       NULL);
	gcut_add_datum("Positive 64bit Poistive Max+1",
		       "val", G_TYPE_UINT64, 9223372036854775808UL,
		       "expect", G_TYPE_STRING, "9223372036854775808",
		       NULL);
	gcut_add_datum("Positive 64bit Max",
		       "val", G_TYPE_UINT64, 18446744073709551615UL,
		       "expect", G_TYPE_STRING, "18446744073709551615",
		       NULL);
}

void test_getUint64(gconstpointer data)
{
	DBTermCodec dbTermCodec;
	string actual = dbTermCodec.enc(gcut_data_get_uint64(data, "val"));
	string expect = gcut_data_get_string(data, "expect");
	cppcut_assert_equal(expect, actual);
}

} // testDBTermCodec

namespace testDBTermCodecSQLite3 {

void data_getUint64(void)
{
	addDataSamplesForGCutUint64();
}

void test_getUint64(gconstpointer data)
{
	DBAgentSQLite3 dbAgent;
	const DBTermCodec *dbTermCodec = dbAgent.getDBTermCodec();
	string actual = dbTermCodec->enc(gcut_data_get_uint64(data, "val"));
	string expect = gcut_data_get_string(data, "expect");
	cppcut_assert_equal(expect, actual);
}

} // testDBTermCodecSQLite3
