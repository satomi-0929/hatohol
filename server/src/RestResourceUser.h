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

#ifndef RestResourceUser_h
#define RestResourceUser_h

#include "FaceRestPrivate.h"

struct RestResourceUser : public FaceRest::ResourceHandler
{
	typedef void (RestResourceUser::*HandlerFunc)(void);

	static void registerFactories(FaceRest *faceRest);
	static const std::string &getPathForUserMe(void);

	RestResourceUser(FaceRest *faceRest, HandlerFunc handler);
	virtual ~RestResourceUser();

	virtual void handle(void) override;

	bool pathIsUserMe(void);

	void handlerUser(void);
	void handlerGetUser(void);
	void handlerPostUser(void);
	void handlerPutUser(void);
	void handlerDeleteUser(void);

	void handlerAccessInfo(void);
	void handlerGetAccessInfo(void);
	void handlerPostAccessInfo(void);
	void handlerDeleteAccessInfo(void);

	void handlerUserRole(void);
	void handlerGetUserRole(void);
	void handlerPostUserRole(void);
	void handlerPutUserRole(void);
	void handlerDeleteUserRole(void);

	/**
	 * Update the user informformation if 'name' specifined in 'query'
	 * exits in the DB. Otherwise, the user is newly added.
	 * NOTE: This method is currently used for test purpose.
	 *
	 * @param query
	 * A hash table that has query parameters in the URL.
	 *
	 * @param option
	 * A UserQueryOption used for the query.
	 *
	 * @return A HatoholError is returned.
	 */
	static HatoholError updateOrAddUser(GHashTable *query,
	                                    UserQueryOption &option);

	static const char *pathForUser;
	static const char *pathForUserRole;
	static const std::string pathForUserMe;

	HandlerFunc m_handlerFunc;
};

struct RestResourceUserFactory : public FaceRest::ResourceHandlerFactory
{
	RestResourceUserFactory(FaceRest *faceRest,
				RestResourceUser::HandlerFunc handler);
	virtual FaceRest::ResourceHandler *createHandler(void) override;

	RestResourceUser::HandlerFunc m_handlerFunc;
};

#endif // RestResourceUser_h
