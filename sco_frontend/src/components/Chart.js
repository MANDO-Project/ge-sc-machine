import { show } from "canvasjs/src/helpers/utils";
import React, { Component } from "react";
import  ReactApexChart from "react-apexcharts";


class StackedChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      series: [
      ],
      options : {
        chart: {
          height: 800,
          type: "line",
          stacked: true,
          // stackType: '100%'
        },
        dataLabels: {
          enabled: true,
            enabledOnSeries: [0, 1],
          style: {
            fontSize: '14px',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 'bold',
            colors: (['#000000'])
        }
        },
        colors: ['#c42400', '#309529'],
        stroke: {
          width: [2, 2, 2, 2]
        },
        plotOptions: {
          bar: {
            columnWidth: "60%"
          }
        },
        xaxis: {
          categories: ['Access_control',
                        'Arithmetic',
                        'Denial_of_service',
                        'Front_running',
                        'Reentrancy',
                        'Time_manipulation',
                        'Unchecked_low_level_calls'
          ]
        },
        yaxis: [
          {
            seriesName: 'BUG',
            axisTicks: {
              show: true
            },
            axisBorder: {
              show: true,
            },
            title: {
              text: "Nodes"
            },
            label:{
              maxWidth: 100
            }
          },
          {
            seriesName: 'BUG',
            show: false
          },
        ],
        tooltip: {
          shared: false,
          intersect: true,
          x: {
            show: true
          }
        },
        legend: {
          horizontalAlign: "left",
          offsetX: 40
        }
      },
      areaOpt:{
          chart: {
          height: 350,
          type: 'area'
        },
        dataLabels: {
          enabled: true
        },
        stroke: {
          curve: 'smooth'
        },
        legend: {
          horizontalAlign: 'left',
          offsetX: 40
        },
        xaxis: {
          categories: ['Access_control',
                        'Arithmetic',
                        'Denial_of_service',
                        'Front_running',
                        'Reentrancy',
                        'Time_manipulation',
                        'Unchecked_low_level_calls'
          ]
        },
        yaxis: [
          {
            opposite: false,
            seriesName: 'GRAPH RUNTIME',
            axisTicks: {
              show: true
            },
            axisBorder: {
              show: true,
            },
            title: {
              text: "Miliseconds",
              show: true,
            }
          },
          {
            opposite: false,
            seriesName: 'NODE RUNTIME',
            show: false,
            axisTicks: {
              show: false
            },
            axisBorder: {
              show: false,
            },
          }
        ],
        plotOptions: {
          area: {
            colors: '#0000ff',
            opacity: 0.9,
            type: 'gradient',
            fillTo: 'end',
          }
        }
      },
      heatMapOpt: {
        chart: {
          height: 450,
          type: 'heatmap',
        },
        dataLabels: {
          enabled: true,
        },
        colors: ["#008FFB"],
        title: {
          text: 'Bug Density'
        },
        yaxis: {
          categories: ['Access_control',
                        'Arithmetic',
                        'Denial_of_service',
                        'Front_running',
                        'Reentrancy',
                        'Time_manipulation',
                        'Unchecked_low_level_calls'
          ]
        },
        legend: {
          horizontalAlign: 'left',
          offsetX: 40
        },
      }
      
    };
  }

  render() {
    if(this.props.showBarChart&&this.props.showGraphCheck){
      return (
        <div id="chart">
        <ReactApexChart options={this.state.options} series={this.props.series} type="bar" height={500} />
        <ReactApexChart options={this.state.areaOpt} series={this.props.areaSeries} type="area" height={500} />
        <ReactApexChart options={this.state.heatMapOpt} series={this.props.heatMapSeries} type="heatmap" height={500} />
        </div>
      );
    }
    else if(this.props.showGraphCheck&&!this.props.showBarChart){
      return (
        <button className="showChart" onClick={this.props.Click}>
                        Show Bar Chart
        </button>
      );
    }
    else return null
  }
}

export default StackedChart