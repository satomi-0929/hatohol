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

#ifndef IncidentSenderManager_h
#define IncidentSenderManager_h

#include "Params.h"
#include "DBTablesMonitoring.h"
#include "IncidentSender.h"

class IncidentSenderManager
{
public:
	static IncidentSenderManager &getInstance(void);

	void queue(const IncidentTrackerIdType &trackerId,
		   const EventInfo &info,
		   IncidentSender::CreateIncidentCallback callback = NULL,
		   void *userData = NULL);
	void queue(const IncidentInfo &incidentInfo,
		   const std::string &comment,
		   IncidentSender::UpdateIncidentCallback callback = NULL,
		   void *userData = NULL);
	bool isIdling(void);

protected:
	IncidentSenderManager(void);
	virtual ~IncidentSenderManager();

	IncidentSender *getSender(const IncidentTrackerIdType &id,
				  bool autoCreate = false);

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

#endif // IncidentSenderManager_h
