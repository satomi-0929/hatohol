/*
 * Copyright (C) 2013 Project Hatohol
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

var HatoholSessionManager = function() {
  var HATOHOL_SID_COOKIE_NAME = "hatoholSessionId";
  var HATOHOL_SID_COOKIE_MAX_AGE = 7 * 24 * 3600;

  return {
    get: function() {
      var cookies = document.cookie.split(";");
      for(var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].replace(/^\s*(.*?)\s*$/, "$1");
        var hands = cookie.split("=");
        if (hands.length != 2)
          continue;
        if (hands[0] == HATOHOL_SID_COOKIE_NAME)
          return hands[1];
      }
      return null;
    },

    set: function(sessionId) {
      document.cookie = HATOHOL_SID_COOKIE_NAME + "=" + sessionId +
                        "; max-age=" + HATOHOL_SID_COOKIE_MAX_AGE;
    },

    deleteCookie: function(path) {
      var date = new Date();
      date.setTime(0);
      var cookie = HATOHOL_SID_COOKIE_NAME + "=; expires=" +
                   date.toGMTString();
      if (path)
        cookie += "; path=" + path;
      document.cookie = cookie;
    }
  };
}();
