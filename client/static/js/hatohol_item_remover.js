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

// ---------------------------------------------------------------------------
// HatoholItemRemover
// ---------------------------------------------------------------------------
var HatoholItemRemover = function(deleteParameters, connParam) {
  //
  // deleteParameters has following parameters.
  //
  // * id: Please enumerate an array of ID to delete.
  // * type
  // TODO: Add the description.
  //
  var count = 0;
  var total = 0;
  var errors = 0;
  var msg = "";
  for (var i = 0; i < deleteParameters.id.length; i++) {
    count++;
    total++;
    new HatoholConnector($.extend({
      url: '/' + deleteParameters.type + '/' + deleteParameters.id[i],
        request: "DELETE",
        context: deleteParameters.id[i],
        replyCallback: function(reply, parser, context) {
        },
        parseErrorCallback: function(reply, parser) {
          // TODO: Add line break.
          msg += "errorCode: " + reply.errorCode + ". ";
          hatoholErrorMsgBox(msg);
          errors++;
        },
        connectErrorCallback: function(XMLHttpRequest,
                                textStatus, errorThrown) {
          // TODO: Add line break.
          msg += "Error: " + XMLHttpRequest.status + ": " +
          XMLHttpRequest.statusText + ". ";
          hatoholErrorMsgBox(msg);
          errors++;
        },
        completionCallback: function(context) {
          compleOneDel();
        }
    }, connParam || {}));
  }

  function compleOneDel() {
    count--;
    var completed = total - count;
    hatoholErrorMsgBox(msg + gettext("Deleting...") + " " + completed +
                       " / " + total);
    if (count > 0)
      return;

    // close dialogs
    hatoholInfoMsgBox(msg + gettext("Completed. (Number of errors: ") +
                      errors + "/" + total + ")");

    if (deleteParameters.completionCallback)
      deleteParameters.completionCallback();
  }
}
