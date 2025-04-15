$.get("get_bar_chart_data/", function (data) {
    var chartDom = document.getElementById('bar_chart');
    var myChart = echarts.init(chartDom, null, { height: 300 });
    var option;

    option = {
        dataset: {
            dimensions: data.columns,
            source: data.data
        },
        xAxis: {
            type: 'category',
            name: 'Search requests',
            nameLocation: 'center',
            nameTextStyle: {
                align: 'right',
                verticalAlign: 'top',
                fontWeight: 'bold',
                fontSize: 16
            },
            nameGap: 30,
        },
        yAxis: {
            type: 'value',
            name: 'Count of vacancies',
            nameLocation: 'middle',
            nameGap: 50,
            nameTextStyle: {
                fontWeight: 'bold',
                fontSize: 16
            }
        },
        series: [
            {
                type: 'bar',
                encode: {
                    x: 'search_request',
                    y: 'total'
                },
                label: {
                    show: true,
                    position: 'outside'
                },
            }
        ],
        title: {
            text: 'Count of vacancies by search requests',
        },
    };

    option && myChart.setOption(option);
    window.addEventListener('resize', function () {
        myChart.resize();
    });
})



