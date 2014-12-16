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

#ifndef DataQueryContext_h
#define DataQueryContext_h

#include "Params.h"
#include "UsedCountable.h"
#include "UsedCountablePtr.h"
#include "OperationPrivilege.h"

/**
 * This class provides a function to share information for data query
 * among DataQueryOption and its subclasses.
 */
class DataQueryContext : public UsedCountable {
public:
	DataQueryContext(const UserIdType &UserId);

	void setUserId(const UserIdType &userId);
	void setFlags(const OperationPrivilegeFlag &flags);
	const OperationPrivilege &getOperationPrivilege(void) const;
	const ServerHostGrpSetMap &getServerHostGrpSetMap(void);
	bool isValidServer(const ServerIdType &serverId);
	const ServerIdSet &getValidServerIdSet(void);

protected:
	// To avoid an instance from being crated on a stack.
	virtual ~DataQueryContext();

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

typedef UsedCountablePtr<DataQueryContext> DataQueryContextPtr;

#endif // DataQueryContext_h
