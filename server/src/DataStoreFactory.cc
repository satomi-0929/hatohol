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

#ifdef HAVE_CONFIG_H
#include <config.h>
#endif // HAVE_CONFIG_H

#include "DataStoreFactory.h"
#include "DataStoreFake.h"
#include "DataStoreZabbix.h"
#include "DataStoreNagios.h"
#include "HatoholArmPluginGate.h"
#ifdef HAVE_LIBRABBITMQ
#include "HatoholArmPluginGateJSON.h"
#endif

DataStore *DataStoreFactory::create(const MonitoringServerInfo &svInfo,
                                    const bool &autoStart)
{
	switch (svInfo.type) {
	case MONITORING_SYSTEM_FAKE:
		return new DataStoreFake(svInfo, autoStart);
	case MONITORING_SYSTEM_ZABBIX:
		return new DataStoreZabbix(svInfo, autoStart);
	case MONITORING_SYSTEM_NAGIOS:
		return new DataStoreNagios(svInfo, autoStart);
	case MONITORING_SYSTEM_HAPI_ZABBIX:
	case MONITORING_SYSTEM_HAPI_CEILOMETER:
	{
		HatoholArmPluginGate *gate = new HatoholArmPluginGate(svInfo);
		if (autoStart)
			gate->start();
                return gate;
	}
#ifdef HAVE_LIBRABBITMQ
	case MONITORING_SYSTEM_HAPI_JSON:
	{
		return new HatoholArmPluginGateJSON(svInfo, autoStart);
	}
#endif
	default:
		MLPL_BUG("Invalid monitoring system: %d\n", svInfo.type);
	}
	return NULL;
}




