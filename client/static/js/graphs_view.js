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

var GraphsView = function(userProfile) {
  //
  // Variables
  //
  var self = this;

  // call the constructor of the super class
  HatoholMonitoringView.apply(this, [userProfile]);

  //
  // main code
  //
  $("#delete-graph-button").show();
  load();

  //
  // Main view
  //
  $("#table").stupidtable();
  $("#table").bind('aftertablesort', function(event, data) {
    var th = $(this).find("th");
    th.find("i.sort").remove();
    var icon = data.direction === "asc" ? "up" : "down";
    th.eq(data.column).append("<i class='sort glyphicon glyphicon-arrow-" + icon +"'></i>");
  });

  $("#delete-graph-button").click(function() {
    var msg = gettext("Do you delete the selected items ?");
    hatoholNoYesMsgBox(msg, deleteGraphs);
  });

  //
  // Commonly used functions from a dialog.
  //
  function HatoholGraphReplyParser(data) {
    this.data = data;
  }

  HatoholGraphReplyParser.prototype.getStatus = function() {
    return REPLY_STATUS.OK;
  };

  function deleteGraphs() {
    $(this).dialog("close");
    var checkboxes = $(".selectcheckbox");
    var deleteList = [];
    var i;
    for (i = 0; i < checkboxes.length; i++) {
      if (checkboxes[i].checked)
        deleteList.push(checkboxes[i].getAttribute("graphID"));
    }
    new HatoholItemRemover({
      id: deleteList,
      type: "graphs",
      completionCallback: function() {
        load();
      }
    }, {
      pathPrefix: '',
      replyParser: HatoholGraphReplyParser
    });
    hatoholInfoMsgBox(gettext("Deleting..."));
  }

  //
  // callback function from the base template
  //
  function drawTableBody(graphs) {
    var table = "";
    graphs.forEach(function(graph) {
      var title = graph.title ? escapeHTML(graph.title) : gettext("No title");
      var graphID = escapeHTML(graph.id);
      var graphURL = "ajax_history?id=" + graphID;
      table += "<tr>";
      table += "<td class='delete-selector' style='display:none'>";
      table += "<input type='checkbox' class='selectcheckbox' " +
        "graphID='" + graphID + "'></td>";
      table += "<td>" + graphID + "</td>";
      table += "<td><a href=\"" + graphURL +  "\">" + title + "</a></td>";
      table += "</tr>";
    });
    return table;
  }

  function onGotGraphs(graphs) {
    self.graphs = graphs;
    $("#table tbody").empty();
    $("#table tbody").append(drawTableBody(self.graphs));
    self.setupCheckboxForDelete($("#delete-graph-button"));
    $(".delete-selector").show();
    $(".edit-graph-column").show();
  }

  function load() {
    self.displayUpdateTime();
    self.startConnection('graphs/',
                         onGotGraphs,
                         null,
                         {pathPrefix: ''});
  }
};

GraphsView.prototype = Object.create(HatoholMonitoringView.prototype);
GraphsView.prototype.constructor = GraphsView;
