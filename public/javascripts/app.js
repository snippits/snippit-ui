google.charts.load('current', {packages: ['corechart', 'line']});
google.charts.setOnLoadCallback(main_fun);

function find_firstline_with_number(content) {
    var lines = content.split("\n");
    for (var i = 0; i < lines.length; i++) {
        if (lines[i][0] >= '0' && lines[i][0] <= '9') {
            return i;
            break;
        }
    }
    return 0;
}

function animate_scroll(aCode, target_top, steps) {
    setTimeout(function(){
        aCode.scrollTop += steps;
        if (aCode.scrollTop + steps < target_top) {
            animate_scroll(aCode, target_top, steps);
        }
    }, 5);
}

function loadCode(id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("code_div").innerHTML = this.responseText;
            var aCode = document.getElementById('code_pre');
            var line_num = find_firstline_with_number(this.responseText);
            hljs.highlightBlock(aCode);

            setTimeout(function(){
                var aCode = document.getElementById('code_pre');
                var text = aCode.getElementsByTagName("span")[0];
                var word_height = parseInt(window.getComputedStyle(text).fontSize) + 3;
                aCode = document.getElementById('code_div');
                animate_scroll(aCode, line_num * word_height, (line_num * word_height) / 50);
                //aCode.scrollTop = line_num * word_height;
            }, 100);
        }
        else {
            document.getElementById("code_div").innerHTML = "Code not found";
        }
    };
    xhttp.open("GET", "output/phase-code-" + id + "?_=" + new Date().getTime(), true);
    xhttp.send();
}

function loadProfResult(id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("prof_div").innerHTML = this.responseText;
        }
        else {
            document.getElementById("prof_div").innerHTML = "Profiling result not found";
        }
    };
    xhttp.open("GET", "output/phase-prof-" + id + "?_=" + new Date().getTime(), true);
    xhttp.send();
}

function loadPhaseHistory() {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            drawBasic(JSON.parse(this.responseText))
        }
    };
    xhttp.open("GET", "output/phase_history.json?_=" + new Date().getTime(), true);
    xhttp.send();
}

function drawBasic(phase_history) {

    var data = new google.visualization.DataTable();
    data.addColumn('number', 'X');
    data.addColumn('number', 'Phase #');

    data.addRows(phase_history);

    var options = {
        hAxis: {
            title: 'Window Count'
        },
        vAxis: {
            title: 'Phase Number'
        }
    };

    function selectHandler() {
        var selectedItem = chart.getSelection()[0];
        if (selectedItem) {
            var topping = data.getValue(selectedItem.row, 1);
            loadProfResult(topping);
            loadCode(topping);
        }
    }

    var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
    google.visualization.events.addListener(chart, 'select', selectHandler);
    chart.draw(data, options);
}

function main_fun()
{
    loadPhaseHistory();
}

