import React, { Component } from "react";
import  ReactApexChart from "react-apexcharts";

class StackedChart extends Component {
  constructor(props) {
    super(props);

    this.state = {
      series: [
    
        {
          name: 'BUG',
          type: 'column',
          data: [40, 70, 30, 0, 22, 80, 35]
        },
        {
          name: "CLEAN",
          type: 'column',
          data: [60, 30, 70, 100, 78, 20,65]
        },
        {
          name: "TIME",
          type: 'line',
          data: [4, 3.2, 2.8, 1.5,3, 2.8, 3.8]
        },
      ],
      options : {
        chart: {
          height: 450,
          type: "line",
          stacked: true,

        },
        dataLabels: {
          enabled: true,
          style: {
            fontSize: '14px',
            fontFamily: 'Helvetica, Arial, sans-serif',
            fontWeight: 'bold',
            colors: (['#333'])
        }
        },
        colors: ['#c42400', '#309529', '#d6d62f'],
        stroke: {
          width: [2, 2, 2]
        },
        plotOptions: {
          bar: {
            columnWidth: "20%"
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
          }, {
            opposite: true,
            seriesName: 'TIME',
            axisTicks: {
              show: true
            },
            axisBorder: {
              show: true,
            },
            title: {
              text: "Miliseconds"
            }
          }
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
      }  
    
    };
  }

  render() {
    if(this.props.showBarChart&&this.props.showGraphCheck){
      return (
        <div id="chart">
        <ReactApexChart options={this.state.options} series={this.props.series} type="bar" height={450} />
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

export default StackedChart ;