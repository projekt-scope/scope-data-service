// Code mirror field for ttl results


var editor = CodeMirror.fromTextArea(document.getElementById("code"), {
  mode: "text/turtle",
  autoRefresh: true,
  lineNumbers: true,
  matchBrackets: true,

});


// Code mirror field for sparql
var sparql_input = CodeMirror.fromTextArea(document.getElementById("sparql_input"), {
  mode: "text/turtle",
  autoRefresh: true,
  lineNumbers: true,
  matchBrackets: true,

});




$(function () {
  $('#toggle-event').change(function () {
    $('#console-event').html('Toggle: ' + $(this).prop('checked'));
    var simplifylist = $('#toggle-event').prop('checked');
    update_graph_with_uri(uri, simplifylist);

  })
})

function tool_service_api() {
  var ttlstring = editor.getValue();
  $.ajax({
    type: 'POST',
    url: 'http://localhost:5004/api/boundingBox/render',
    data: JSON.stringify({
      ttl: ttlstring,
      method: "oneBBox"
    }),

    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {
      // console.log(data)
      editor.replaceRange(data, {
        line: Infinity
      });

      update_with_ttlString_JsonNameList_and_render(data, true);

    },

    contentType: "application/json",
    dataType: 'json'
  });

}


function update_graph_with_uri_TS(uristring, simplifylist) {
  var ttlstring = editor.getValue();

  set_info_element(uristring);
  var trimnumber = document.getElementById("trimnumber").value
  $.ajax({
    type: 'POST',
    url: '/api/graph/TS',
    data: JSON.stringify({
      ttl: ttlstring,
      uri: uristring,
      simplifylist: simplifylist,
      trimnumber: trimnumber
    }),
    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      subPredObjList = data['subPredObjs'];
      // add the json shapes to scence
      document.getElementById("loader").style.display = "none";

      update_graph_visualizer(subPredObjList);

    },

    contentType: "application/json",
    dataType: 'json'
  });

}



function update_JsonNameList_and_render_FromTS(nGraph) {
  // call this function if dropdown changes
  clickedItem = "";
  set_info_graph(nGraph);
  delete_all();
  // call API - Endpoint to create json shapes and return the list, or direkt all json as a list
  $.ajax({
    type: 'POST',
    url: '/api/TS',
    data: '{"nGraph" :"' + nGraph + '"}',
    beforeSend: function () {
      // console.log(nGraph);
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      jsonNameList = data['jsonIDs'];
      ttlstring = data['ttlstring']

      subPredObjList = data['subPredObjs'];
      fill_dropdown_elemente(subPredObjList);
      document.getElementById("loader").style.display = "none";
      // add the json shapes to scence
      loadJsons();
      update_graph_visualizer(subPredObjList)


    },

    contentType: "application/json",
    dataType: 'json'
  });
}

function getTTL() {
  delete_all();
  var ttlstring = editor.getValue();

  update_with_ttlString_JsonNameList_and_render(ttlstring);
}

function update_with_ttlString_JsonNameList_and_render(ttlstring, bbox = false) {
  clickedItem = "";
  $.ajax({
    type: 'POST',
    url: '/api/',
    data: JSON.stringify({
      ttl: ttlstring
    }),
    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      jsonNameList = data['jsonIDs'];
      subPredObjList = data['subPredObjs'];
     
      // add the json shapes to scence
      loadJsons(bbox);
      document.getElementById("loader").style.display = "none";

      update_graph_visualizer(subPredObjList);

    },

    contentType: "application/json",
    dataType: 'json'
  });
}

function getTSdata() {
  clickedItem = "";
  delete_all();
  var TSurl = document.getElementById("TS").value;
  var namespace = document.getElementById("namespace").value;

  update_with_TS(TSurl, namespace);
}

function update_with_TS(TSurl, namespace) {

  $.ajax({
    type: 'POST',
    url: '/api/TS/',
    data: JSON.stringify({
      TS: TSurl,
      Namespace: namespace
    }),
    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      jsonNameList = data['jsonIDs'];
      subPredObjList = data['subPredObjs'];
      // add the json shapes to scence
      loadJsons();
      document.getElementById("loader").style.display = "none";

      update_graph_visualizer(subPredObjList);
      ttlstring = data['ttlstring']


    },

    contentType: "application/json",
    dataType: 'json'
  });
}


function update_graph_visualizer(subPredObjList) {
  var triples = subPredObjList;
  s = ""
  if (ts) {
    triples.forEach(function (triple) {
      var subjId = triple.subject;
      var predId = triple.predicate;
      var objId = triple.object;

      if (predId == "omg:hasOccString" || predId == "omg:hasOCCPickle") {
        s += ""
      } else {
        s += subjId + "  "
        s += predId + "  "
        s += objId + "\n"
      }
    });
    editor.setValue(s);
  }
  var graph = triplesToGraph(triples);
  update(graph);
}

function set_info_graph(url) {
  $("#graph_panel").html("Graph: " + url);
}


function set_info_element(uristring) {
  $("#element_panel").html("Element: " + uristring);

  // search(uristring);
}

function scrollToElement(pos) {

  var elem = document.getElementById(pos);
  if (elem.clientHeight <= 70) {
    var notes = null;
    for (var i = 0; i < elem.childNodes.length; i++) {
      if (elem.childNodes[i].className == "collapse") {
        notes = elem.childNodes[i];
        notes.classList.add("show");
        break;
      }
    }
  }

  var elem = document.getElementById(pos);
  var topPos = elem.offsetTop;
  document.getElementById('scrollside').scrollTop = topPos - 50;

}

function set_info_graph(url) {
  $("#graph_panel").html("Graph: " + url);
  try {
    $("#graph_panel").html("Graph: " + url);
    document.getElementById("graph").value = url;
    document.getElementById("element").value = "";
    document.getElementById("new_attribute").value = "";
    document.getElementById("value").value = "";
  } catch (e) {}
}


function set_info_element(uristring) {
  $("#element_panel").html("Element: " + uristring);

  // search(uristring);
  try {
    $("#element_panel").html("Element: " + uristring);
    document.getElementById("element").value = uristring;
  } catch (e) {}
}

function fill_dropdown_elemente(list_eleme) {
    var dp = document.getElementById("dropdown-menu_element");
    document.getElementById("dropdown-menu_element").innerHTML = "";
    var dd = document.createElement('div');
    dd.id = "openCallsList";
    for (var key in list_eleme) {
      var li = document.createElement('li');

      var aa = document.createElement('a');

      aa.classList.add("dropdown-item");
      aa.classList.add("sel_link");

      aa.appendChild(document.createTextNode(list_eleme[key]["object"]));
      li.appendChild(aa);
      dd.appendChild(li);
    }
    dp.appendChild(dd);

}