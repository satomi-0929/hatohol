/*
 * Copyright (C) 2013 Project Hatohol
 *
 * This file is part of Hatohol.
 *
 * Hatohol is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * Hatohol is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Hatohol. If not, see <http://www.gnu.org/licenses/>.
 */

#include <cstdio>
#include "DBClientUser.h"
#include "DataQueryOption.h"
#include "CacheServiceDBClient.h"

struct DataQueryOption::PrivateContext {
	UserIdType userId;
	size_t maxNumber;
	SortOrder sortOrder;
	uint64_t startId;

	// constuctor
	PrivateContext(void)
	: userId(INVALID_USER_ID),
	  maxNumber(NO_LIMIT),
	  sortOrder(SORT_DONT_CARE),
	  startId(0)
	{
	}
};

const size_t DataQueryOption::NO_LIMIT = 0;

// ---------------------------------------------------------------------------
// Public static methods
// ---------------------------------------------------------------------------
DataQueryOption::DataQueryOption(void)
: m_ctx(NULL)
{
	m_ctx = new PrivateContext();
}

DataQueryOption::~DataQueryOption()
{
	if (m_ctx)
		delete m_ctx;
}

bool DataQueryOption::operator==(const DataQueryOption &rhs)
{
	if (m_ctx->userId != rhs.m_ctx->userId)
		return false;
	if (m_ctx->maxNumber != rhs.m_ctx->maxNumber)
		return false;
	if (m_ctx->sortOrder != rhs.m_ctx->sortOrder)
		return false;
	if (m_ctx->startId != rhs.m_ctx->startId)
		return false;
	return true;
}

string DataQueryOption::getCondition(void) const
{
	return "";
}

void DataQueryOption::setMaximumNumber(size_t maximum)
{
	m_ctx->maxNumber = maximum;
}

size_t DataQueryOption::getMaximumNumber(void) const
{
	return m_ctx->maxNumber;
}

void DataQueryOption::setSortOrder(SortOrder order)
{
	m_ctx->sortOrder = order;
}

DataQueryOption::SortOrder DataQueryOption::getSortOrder(void) const
{
	return m_ctx->sortOrder;
}

void DataQueryOption::setStartId(uint64_t id)
{
	m_ctx->startId = id;
}

uint64_t DataQueryOption::getStartId(void) const
{
	return m_ctx->startId;
}

void DataQueryOption::setUserId(UserIdType userId)
{
	m_ctx->userId = userId;
	if (m_ctx->userId == USER_ID_ADMIN) {
		setFlags(ALL_PRIVILEGES);
		return;
	}

	UserInfo userInfo;
	CacheServiceDBClient cache;
	if (!cache.getUser()->getUserInfo(userInfo, userId)) {
		MLPL_ERR("Failed to getUserInfo(): userId: "
		         "%"FMT_USER_ID"\n", userId);
		m_ctx->userId = INVALID_USER_ID;
		return;
	}
	setFlags(userInfo.flags);
}

UserIdType DataQueryOption::getUserId(void) const
{
	return m_ctx->userId;
}
