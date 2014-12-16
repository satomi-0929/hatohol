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

#ifndef RestResourceAction_h
#define RestResourceAction_h

#include "FaceRestPrivate.h"

struct RestResourceAction : public FaceRest::ResourceHandler
{
	static void registerFactories(FaceRest *faceRest);

	RestResourceAction(FaceRest *faceRest);
	virtual ~RestResourceAction();

	virtual void handle(void) override;

	void handleGet(void);
	void handlePost(void);
	void handleDelete(void);

	static const char *pathForAction;
};

struct RestResourceActionFactory : public FaceRest::ResourceHandlerFactory
{
	RestResourceActionFactory(FaceRest *faceRest);
	virtual FaceRest::ResourceHandler *createHandler(void) override;
};

#endif // RestResourceAction_h
