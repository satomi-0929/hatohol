/*
 * Copyright (C) 2015 Project Hatohol
 *
 * This file is part of Hatohol.
 *
 * Hatohol is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Lesser General Public License, version 3
 * as published by the Free Software Foundation.
 *
 * Hatohol is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with Hatohol. If not, see
 * <http://www.gnu.org/licenses/>.
 */

#ifndef HatoholArmPluginGateHAPI2_h
#define HatoholArmPluginGateHAPI2_h

#include "DataStore.h"
#include "HatoholArmPluginInterfaceHAPI2.h"
#include "JSONBuilder.h"
#include "DBTablesLastInfo.h"

enum ProcedureImplementType {
	PROCEDURE_SERVER,
	PROCEDURE_HAP,
	PROCEDURE_BOTH
};

enum ProcedureRequirementLevel {
	BOTH_MANDATORY,
	SERVER_MANDATORY,
	SERVER_OPTIONAL,
	SERVER_MANDATORY_HAP_OPTIONAL,
	HAP_MANDATORY,
	HAP_OPTIONAL
};

struct HAPI2ProcedureDef {
	ProcedureImplementType type;
	std::string name;
	ProcedureRequirementLevel level;
};

class HatoholArmPluginGateHAPI2 : public DataStore, public HatoholArmPluginInterfaceHAPI2 {
public:
	HatoholArmPluginGateHAPI2(const MonitoringServerInfo &serverInfo,
				  const bool &autoStart = true);

	virtual const MonitoringServerInfo
	  &getMonitoringServerInfo(void) const override;
	virtual const ArmStatus &getArmStatus(void) const override;
	virtual void start(void) override;

	virtual bool isFetchItemsSupported(void);
	virtual bool startOnDemandFetchItem(Closure0 *closure) override;
	virtual void startOnDemandFetchHistory(
	  const ItemInfo &itemInfo,
	  const time_t &beginTime,
	  const time_t &endTime,
	  Closure1<HistoryInfoVect> *closure) override;
	virtual bool startOnDemandFetchTrigger(Closure0 *closure) override;

protected:
	virtual ~HatoholArmPluginGateHAPI2();
	void upsertLastInfo(std::string lastInfoValue, LastInfoType type);

private:
	std::string procedureHandlerExchangeProfile(JSONParser &parser);
	std::string procedureHandlerMonitoringServerInfo(JSONParser &parser);
	std::string procedureHandlerLastInfo(JSONParser &parser);
	std::string procedureHandlerPutItems(JSONParser &parser);
	std::string procedureHandlerPutHistory(JSONParser &parser);
	std::string procedureHandlerUpdateHosts(JSONParser &parser);
	std::string procedureHandlerUpdateHostGroups(JSONParser &parser);
	std::string procedureHandlerUpdateHostGroupMembership(JSONParser &parser);
	std::string procedureHandlerUpdateTriggers(JSONParser &parser);
	std::string procedureHandlerUpdateEvents(JSONParser &parser);
	std::string procedureHandlerUpdateHostParents(JSONParser &parser);
	std::string procedureHandlerUpdateArmInfo(JSONParser &parser);

public:
	static bool parseTimeStamp(const std::string &timeStampString,
				   timespec &timeStamp);

private:
	struct Impl;
	std::unique_ptr<Impl> m_impl;
};

typedef UsedCountablePtr<HatoholArmPluginGateHAPI2> HatoholArmPluginGateHAPI2Ptr;

#endif // HatoholArmPluginGateHAPI2_h
