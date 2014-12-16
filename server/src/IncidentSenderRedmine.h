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

#ifndef IncidentSenderRedmine_h
#define IncidentSenderRedmine_h

#include "IncidentSender.h"

class IncidentSenderRedmine : public IncidentSender
{
public:
	IncidentSenderRedmine(const IncidentTrackerInfo &tracker);
	virtual ~IncidentSenderRedmine();

	virtual HatoholError send(const EventInfo &event) override;

	virtual HatoholError send(const IncidentInfo &incident,
				  const std::string &comment) override;

protected:
	std::string buildJSON(const EventInfo &event);
	std::string buildJSON(const IncidentInfo &incident,
			      const std::string &comment);
	std::string getProjectURL(void);
	std::string buildDescription(const EventInfo &event,
				     const MonitoringServerInfo *server);
	std::string getIssuesJSONURL(void);
	std::string getIssueURL(const std::string &id);
	HatoholError parseResponse(IncidentInfo &incidentInfo,
				   const std::string &response);
	HatoholError buildIncidentInfo(IncidentInfo &incidentInfo,
				       const std::string &response,
				       const EventInfo &event);

	// TODO: Move to MonitoringServer?
	static std::string buildURLMonitoringServerEvent(
	  const EventInfo &event,
	  const MonitoringServerInfo *server);

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

#endif // IncidentSenderRedmine_h
