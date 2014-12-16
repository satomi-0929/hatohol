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

#ifndef DB_h
#define DB_h

#include <memory>
#include <Mutex.h>
#include <typeinfo>
#include "Params.h"
#include "DBAgent.h"

class DB {
public:
	enum {
		IDX_TABLES_VERSION_TABLES_ID,
		IDX_TABLES_VERSION_VERSION,
		NUM_IDX_TABLES,
	};

	static const DBAgent::TableProfile &
	  getTableProfileTablesVersion(void);
	static const std::string &getAlwaysFalseCondition(void);
	static bool isAlwaysFalseCondition(const std::string &condition);

	virtual ~DB(void);
	DBAgent &getDBAgent(void);

protected:
	struct SetupContext {
		const std::type_info &dbClassType;
		DBConnectInfo connectInfo;
		bool          initialized;
		mlpl::Mutex   lock;

		SetupContext(const std::type_info &dbClassType);
	};

	DB(SetupContext &setupCtx);

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

#endif // DB_h
