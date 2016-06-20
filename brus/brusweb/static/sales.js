function accumulate(d) {
    var i=1;
    for (;i<d.length;i++) {
        d[i][1] += d[i-1][1];
    }
}

d3.json('/brus/sales.json', function(data) {
    for (v in data){
      accumulate(data[v].values);
    }
    nv.addGraph(function() {
        var chart = nv.models.stackedAreaChart()
            .x(function(d) { return d[0] })
            .y(function(d) { return d[1] })
            .color(d3.scale.category10().range())
            .useInteractiveGuideline(true)
        ;

        chart.xAxis
            //.tickValues([1078030800000,1122782400000,1167541200000,1251691200000])
            .tickFormat(function(d) {
                return d3.time.format('%x')(new Date(d))
            });

        chart.yAxis
            .tickFormat(d3.format(',.0f'));

        d3.select('#chart svg')
            .datum(data)
            .call(chart);

        nv.utils.windowResize(chart.update);

        return chart;
    });
});


