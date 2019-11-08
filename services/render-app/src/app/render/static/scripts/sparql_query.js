function run_sparql() {

    var sparql = sparql_input.getValue();
    var select = document.getElementById("select");
    var graph = select.options[select.selectedIndex].value;

    console.log(graph);

    $.ajax({
        type: 'POST',
        url: '/api/sparql/TS',
        data: JSON.stringify({
            sparql: sparql
        }),

        success: function (data) {

            heading = data["header"]

            document.getElementById("table").innerHTML = "";

            var myTableDiv = document.getElementById("table");
            var thead = document.createElement('thead');
            thead.class = " thead-dark";
            var tr = document.createElement('tr');

            for (i = 0; i < heading.length; i++) {
                var th = document.createElement('th')
                th.scope += ' col';
                th.width = 'auto';
                th.appendChild(document.createTextNode(heading[i]));
                tr.appendChild(th);
            }

            thead.appendChild(tr);
            myTableDiv.appendChild(thead);

            var tbody = document.createElement('tbody');
            var lis = data["rows"]

            for (i = 0; i < lis.length; i++) {
                var tr = document.createElement('tr');
                for (a = 0; a < lis[i].length; a++) {
                    var td = document.createElement('td');
                    td.appendChild(document.createTextNode(lis[i][a]));
                    tr.appendChild(td);
                }
                tbody.appendChild(tr);
            }
            myTableDiv.appendChild(tbody);
        },

        contentType: "application/json",
        dataType: 'json'
    });

}

function insert_sparql() {

    var graph = document.getElementById("graph").value;
    var elem = document.getElementById("element").value;
    var attr = document.getElementById("new_attribute").value;
    var valu = document.getElementById("value").value;

    $.ajax({
        type: 'POST',
        url: '/api/insert/TS',
        data: JSON.stringify({
            attr: attr,
            value: valu,
            graph: graph,
            elem: elem
        }),

        success: function (data) {
            heading = data["header"]
        },
        contentType: "application/json",
        dataType: 'json'
    });

}