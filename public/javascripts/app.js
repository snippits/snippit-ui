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


function loadTreemap(id) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            draw_high_tree(JSON.parse(this.responseText));
        }
        else {
            draw_high_tree([{name: "Profiling result not found", id: "id_0", value: 1}]);
        }
    };
    xhttp.open("GET", "output/phase-treemap-" + id + "?_=" + new Date().getTime(), true);
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

function loadPhaseHistory(similarity_threshold) {
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            draw_highchart(JSON.parse(this.responseText));
        }
    };
    similarity_threshold = parseInt(similarity_threshold / 10)
    xhttp.open("GET", "output/phase-history-" + similarity_threshold + ".json?_=" + new Date().getTime(), true);
    xhttp.send();
}

function draw_highchart(data) {
    // Create the chart
    Highcharts.stockChart('container', {
        plotOptions: {
            series: {
                animation: {
                    duration: 2000,
                },
                allowPointSelect: true,
            }
        },
        rangeSelector: {
            allButtonsEnabled: true,
            selected: 4,
            buttons: [{
                type: 'millisecond',
                count: 2000,
                text: 'ms'
            }, {
                type: 'second',
                count: 10,
                text: '1s'
            }, {
                type: 'minute',
                count: 1,
                text: '1M'
            }, {
                type: 'hour',
                count: 1,
                text: '1H'
            }, {
                type: 'all',
                text: 'All'
            }],
            inputDateFormat: '%H:%M:%S.%L',
            inputEditDateFormat: '%H:%M:%S.%L',
        },

        title: {
            text: 'Phase ID Timeline',
        },

        yAxis: {
            allowDecimals: false,
            title: {
                text: 'Phase ID',
                style: {fontSize: "25px"},
            },
        },

        chart: {
            height: '400px',
        },

        scrollbar: {
            liveRedraw: false
        },

        series: [{
            name: 'Phase ID',
            data: data,
            marker: {
                enabled: null, // auto
                radius: 3,
                lineWidth: 1,
            },
            tooltip: {
                valueDecimals: 0
            },
            linecap:"round",
            point:{
                events: {
                    select: function (event) {
                        console.log(event.target["y"])
                        var selectedItem = event.target["y"];
                        if (selectedItem) {
                            loadProfResult(selectedItem);
                            loadCode(selectedItem);
                            loadTreemap(selectedItem);
                            return true;
                        }
                        return false;
                    }
                }
            },
            allowPointSelect: true,
            showCheckbox: false,
            selected: false,
            dataGrouping: { enabled: false },
        }]
    });
}

function draw_high_tree(data) {
    Highcharts.chart('container_tree', {
        series: [{
            type: 'treemap',
            layoutAlgorithm: 'squarified',
            allowDrillToNode: true,
            animationLimit: 500,
            dataLabels: {
                enabled: false
            },
            levelIsConstant: false,
            levels: [{
                level: 1,
                dataLabels: {
                    enabled: true,
                    style: {fontSize: "15px"}
                },
                borderWidth: 3
            }],
            data: data
        }],
        subtitle: {
            text: ''
        },
        title: {
            text: 'Phase Tree Map of Execution Times'
        },
        colorAxis: {
            minColor: '#FFFFFF',
            maxColor: Highcharts.getOptions().colors[0]
        },
    });
}

function main_fun()
{
    draw_high_tree([{name: "No phase is selected", id: "id_0", value: 1}]);
    loadPhaseHistory(90);
}

