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

var lastPos = null, lastQuery = null, marked = [];


// function unmark() {
//   for (var i = 0; i < marked.length; ++i) marked[i]();
//   marked.length = 0;
// }

// function search() {
//   unmark();                     
//   var text = "t";
//   if (!text) return;
//   for (var cursor = editor.getSearchCursor(text); cursor.findNext();)
//     marked.push(editor.markText(cursor.from(), cursor.to(), "searched"));

//   if (lastQuery != text) lastPos = null;
//   var cursor = editor.getSearchCursor(text, lastPos || editor.getCursor());
//   if (!cursor.findNext()) {
//     cursor = editor.getSearchCursor(text);
//     if (!cursor.findNext()) return;
//   }
//   editor.setSelection(cursor.from(), cursor.to());
//   lastQuery = text; lastPos = cursor.to();
// }


function replace_Codemirror(name, value) {
//------------- ToDo --------//

//   var text = name;
//       replace =name+ " "+value;
//   if (!text) return;
  
//   var cursor = sparql_input.getSearchCursor(text); 
//   cursor.findNext();

// console.log(cursor.from()["line"]);
// console.log(sparql_input.getLine(cursor.from()["line"]));
// var pos1 = { // create a new object to avoid mutation of the original selection
//   line: cursor.from()["line"],
//   ch: 0 // set the character position to the end of the line
// }

// sparql_input.replaceRange(replace, pos1);

}



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
    data: JSON.stringify({ ttl: ttlstring, method: "oneBBox" }),

    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {
      console.log(data)
      editor.replaceRange(data, { line: Infinity });

      update_with_ttlString_JsonNameList_and_render(data,true);

    },

    contentType: "application/json",
    dataType: 'json'
  });

}


function update_graph_with_uri(uristring, simplifylist) {
  var ttlstring = editor.getValue();
  $.ajax({
    type: 'POST',
    url: '/api/graph/',
    data: JSON.stringify({ ttl: ttlstring, uri: uristring, simplifylist: simplifylist }),
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

function update_graph_with_uri_TS(uristring, simplifylist) {
  var ttlstring = editor.getValue();

  set_info_element(uristring);
  $.ajax({
    type: 'POST',
    url: '/api/graph/TS',
    data: JSON.stringify({ ttl: ttlstring, uri: uristring, simplifylist: simplifylist }),
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


function update_JsonNameList_and_render(filename) {
  // call this function if dropdown changes
  clickedItem = "";
  delete_all();
  // call API - Endpoint to create json shapes and return the list, or direkt all json as a list
  $.ajax({
    type: 'POST',
    url: '/api/',
    data: '{"file" :"' + filename + '"}', // or JSON.stringify ({file: 'filename'}),
    beforeSend: function () {
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      jsonNameList = data['jsonIDs'];
      ttlstring = data['ttlstring']
      subPredObjList = data['subPredObjs'];

      document.getElementById("loader").style.display = "none";
      // add the json shapes to scence
      loadJsons();
      update_graph_visualizer(subPredObjList)


    },

    contentType: "application/json",
    dataType: 'json'
  });
}

function update_JsonNameList_and_render_FromTS(nGraph) {
  // call this function if dropdown changes
  clickedItem = "";
  set_info_graph(nGraph);
  replace_Codemirror("#Graph",nGraph);
  delete_all();
  // call API - Endpoint to create json shapes and return the list, or direkt all json as a list
  $.ajax({
    type: 'POST',
    url: '/api/TS',
    data: '{"nGraph" :"' + nGraph + '"}', 
    beforeSend: function () {
      console.log(nGraph);
      document.getElementById("loader").style.display = "block";
    },
    success: function (data) {

      jsonNameList = data['jsonIDs'];
      ttlstring = data['ttlstring']

      subPredObjList = data['subPredObjs'];

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
  //console.log(ttlstring);

  update_with_ttlString_JsonNameList_and_render(ttlstring);
}

function update_with_ttlString_JsonNameList_and_render(ttlstring, bbox=false) {
  clickedItem = "";
  $.ajax({
    type: 'POST',
    url: '/api/',
    data: JSON.stringify({ ttl: ttlstring }),
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
  //console.log(ttlstring);

  update_with_TS(TSurl, namespace);
}

function update_with_TS(TSurl, namespace) {

  $.ajax({
    type: 'POST',
    url: '/api/TS/',
    data: JSON.stringify({ TS: TSurl, Namespace: namespace }),
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
console.log(ts);
  if (ts){


  triples.forEach(function (triple) {
    var subjId = triple.subject;
    var predId = triple.predicate;
    var objId = triple.object;

    if(predId == "omg:hasOccString" || predId =="omg:haspickle"){
      s += ""
    }
    else{
      s  += subjId  + "  "
      s  += predId  + "  "
      s  += objId + "\n"
    }
  });

  editor.setValue(s);
}
  var graph = triplesToGraph(triples);
  update(graph);
}

function set_info_graph(url) {
  $("#graph_panel").html("Graph: "+ url);
}


function set_info_element(uristring) {
  $("#element_panel").html("Element: "+ uristring);
   
  // search(uristring);
}
