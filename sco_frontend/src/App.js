import React,{Component, Suspense} from 'react' 
import "./App.css"
import Detail_error from './components/SH_code'
import StackedChart from './components/Chart'
import Graph_check from './components/graphcheck'
import GithubCorner from 'react-github-corner'
import LoadingOverlay from 'react-loading-overlay';
import Alert from 'react-popup-alert'
import styled, { css } from "styled-components";
// import { useAlert } from "react-alert";


import { BrowserRouter, Route, Routes } from 'react-router-dom';

import {encode as base64_encode} from 'base-64';
import sample0 from './smart_contracts/0x23a91059fdc9579a9fbd0edc5f2ea0bfdb70deb4.sol';


import Select from 'react-select'; 
import x from './smart_contracts/0x23a91059fdc9579a9fbd0edc5f2ea0bfdb70deb4.sol'
import y from "./smart_contracts/simple_dao.sol"
import z from "./smart_contracts/buggy_1.sol"

const BugIds = {
  access_control: 0,
  arithmetic: 1,
  denial_of_service: 2,
  front_running: 3,
  reentrancy: 4,
  time_manipulation: 5,
  unchecked_low_level_calls: 6
}
const optionsSelect = [
  { value: x, label: '0x23a91059fdc9579a9fbd0edc5f2ea0bfdb70deb4.sol' },
  { value: y, label: 'simple_dao.sol' },
  { value: z, label: 'buggy_1.sol' },
]; 

const DarkBackground = styled.div`
  display: none; /* Hidden by default */
  position: fixed; /* Stay in place */
  z-index: 999; /* Sit on top */
  left: 0;
  top: 0;
  width: 100%; /* Full width */
  height: 100%; /* Full height */
  overflow: auto; /* Enable scroll if needed */
  background-color: rgb(0, 0, 0); /* Fallback color */
  background-color: rgba(0, 0, 0, 0.4); /* Black w/ opacity */

  ${(props) =>
    props.disappear &&
    css`
      display: block; /* show */
    `}
`;


class App extends Component {
    constructor(props){
      super(props)
      this.state = {
        // Initially, no file is selected
        isLoading: false,
        newSubmit: false,
        detectReports:null,
        base64String:null,
        detectResults: null,
        detectGraphs:null,
        selectedFile:null,
        DataChart:null,
        codeString :"",
        graph:{nodes: [],links: [],},
        arrayerrorline:[],
        ClickNode:[],
        Access_control:'Access_control_green',
        Arithmetic:'Arithmetic_red',
        Denial_of_service:'Denial_of_service_green',
        Front_running:'Front_running_green',
        Reentrancy:'Reentrancy_green',
        Time_manipulation:'Time_manipulation_red',
        Unchecked_low_level_calls:'Unchecked_low_level_calls_red',
        changeBugType: false,
        showGraphCheck: false,
        showDetailCode:false,
        showBarChart:false,
        showHeatMap: false,
        Error_type:{ Access_control:1,
        Arithmetic:0,
        Denial_of_service:1,
        Front_running:0,
        Reentrancy:1,
        Time_manipulation:0,
        Unchecked_low_level_calls:1},
        seriesBarChart: [],
        seriesHeatMap: [],
        seriesArea: [],
        seriesArea: [],
        selectOptions:null,
        alert: {
          type: 'error',
          text: 'This is a alert message',
          show: false
        },
      };
      // const alert = useAlert();
    }
    onClickChooseFile = (event) =>{
      const realFileBtn = document.getElementById("input")
      realFileBtn.click()
    }

    // On file select (from the pop up)
    onFileChange = event => {
      // Update the state
      console.log(event.target.files[0])
      this.setState({ selectedFile: event.target.files[0] })
      this.setState({ClickNode:[]})
      this.setState({showBarChart:false,showHeatMap:false,showDetailCode:false,showGraphCheck:false})
      //readfile
      let self=this
      var input = document.querySelector('input[type=file]').files[0]
      var reader = new FileReader()
      reader.onload = function (event) {
        self.setState({codeString: event.target.result})
      }
      reader.readAsBinaryString(input)

      // Customize choose file button
      const customTxt = document.getElementById("custom-text")
      if (event.target.files[0]) {
        customTxt.innerHTML = event.target.files[0].name
      } else {
        customTxt.innerHTML = "No file chosen"
      }
      //Convert a file to base64 string
      var fileInput = document.getElementById('input').files
      // console.log(fileInput)
      reader = new FileReader()
      
      reader.readAsDataURL(fileInput[0])
      reader.onload = function () {
        const data = reader.result
                .replace('data:', '')
                .replace(/^.+,/, '')
        self.setState({base64String:data})
      }
      reader.onerror = function (error) {
        console.log('Error: ', error)
      }
    }
    onSelectChange = selectedOption => {
      fetch(selectedOption.value)
      .then(r => r.text())
      .then(text => {
        this.setState({codeString: text})
        console.log(btoa(text));
        this.setState({base64String:btoa(text)});
      });
    };

    //Check to see what kind of errors the code encounters
    onSubmit = () => {
      //connect graph backend
      this.setState({isLoading: true})
      let report_api='http://localhost:5555/v1.0.0/vulnerability/detection/nodetype'
      const reportRequestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                    'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({smart_contract:this.state.base64String})
      }
      fetch(report_api, reportRequestOptions)
      .then(response => response.json())
      .then(data => {
        if (data['messages'] !== 'OK') {
          this.setState({
            alert: {
              type: 'error',
              text: data['messages'],
              show: true
            }
          })
        }
        this.setState({detectReports:data})
        this.setState({newSubmit: true})
        // console.log('request: ', this.newSubmit)
        this.setState({isLoading: false})
      })
    }

    onClickSample = (event) => {
      // this.setState({ selectedFile: event.target.files[0] })
      this.setState({ClickNode:[]})
      this.setState({showBarChart:false,showHeatMap:false,showDetailCode:false,showGraphCheck:false})
      let encoded = null
      fetch(sample0)
      .then(r => r.text())
      .then(text => {
        encoded = base64_encode(text);
        this.setState({base64String:encoded})
      });

      this.setState({isLoading: true})
      let report_api='http://localhost:5555/v1.0.0/vulnerability/detection/nodetype'
      const reportRequestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                    'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({smart_contract:encoded})
      }
      fetch(report_api, reportRequestOptions)
      .then(response => response.json())
      .then(data => {
        this.setState({detectReports:data})
        this.setState({newSubmit: true})
        // console.log('request: ', this.newSubmit)
        this.setState({isLoading: false})
      })
    }

    onSample1 = () => {
      //connect graph backend
      this.setState({isLoading: true})
      let report_api='http://localhost:5555/v1.0.0/vulnerability/detection/nodetype'
      const reportRequestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                    'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({smart_contract:this.state.base64String})
      }
      fetch(report_api, reportRequestOptions)
      .then(response => response.json())
      .then(data => {
        this.setState({newSubmit: true})
        this.setState({detectReports:data})
        // console.log('request: ', this.newSubmit)
        this.setState({isLoading: false})
      })
    }

    //Detail Button
    onClickDetail_Access_control = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.access_control]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Arithmetic = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.arithmetic]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Denial_of_service = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.denial_of_service]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Front_running = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.front_running]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Reentrancy = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.reentrancy]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Time_manipulation = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.time_manipulation]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }
    onClickDetail_Unchecked_low_level_calls = event =>{
      this.setState({detectResults:this.state.detectReports['summaries'][BugIds.unchecked_low_level_calls]})
      this.setState({changeBugType:true})
      this.setState({showDetailCode:true})
    }

    onCloseAlert = () => {
      this.setState({alert: {
        type: '',
        text: '',
        show: false
      }})
    }

    //componentDidUpdate
    componentDidUpdate(prevProps,prevState){
      if(prevState.changeBugType!==this.state.changeBugType){
        let array = []
        let ArrayUniq = []
        let self=this
        var data=this.state.detectResults
        self.setState({graph:data["graph"]})
        if(data["results"]!=null){
          data["results"].forEach((node, index) => {
            if (node["vulnerability"] == 1) {
              array = [...array, ...node["code_lines"]]
              ArrayUniq = [...new Set(array)]
            }
          })
        self.setState({arrayerrorline:ArrayUniq})
        }
      }

      if(this.state.newSubmit && this.state.detectReports['messages'] === 'OK'){
        let typeBugs=this.state.detectReports['summaries']
        if(typeBugs[0]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Access_control:'Access_control_green'})
        }
        else  this.setState({Access_control:'Access_control_red'})
        if(typeBugs[1]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Arithmetic:'Arithmetic_green'})
        }
        else  this.setState({Arithmetic:'Arithmetic_red'})
        if(typeBugs[2]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Denial_of_service:'Denial_of_service_green'})
        }
        else  this.setState({Denial_of_service:'Denial_of_service_red'})
        if(typeBugs[3]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Front_running:'Front_running_green'})
        }
        else  this.setState({Front_running:'Front_running_red'})
        if(typeBugs[4]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Reentrancy:'Reentrancy_green'})
        }
        else  this.setState({Reentrancy:'Reentrancy_red'})
        if(typeBugs[5]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Time_manipulation:'Time_manipulation_green'})
        }
        else  this.setState({Time_manipulation:'Time_manipulation_red'})
        if(typeBugs[6]['vulnerability']===0){
          this.setState({newSubmit: false})
          this.setState({Unchecked_low_level_calls:'Unchecked_low_level_calls_green'})
        }
        else  this.setState({Unchecked_low_level_calls:'Unchecked_low_level_calls_red'})
          this.setState({newSubmit: false})
          this.setState({showGraphCheck:true})
      }
      if(prevState.changeBugType!==this.state.changeBugType){
        let dataChart=this.state.detectReports['summaries']
        var i=0
        // BarChart series
        let seriesBarChart= [
          {
            name: 'BUG',
            type: 'column',
            data: []
          },
          {
            name: "CLEAN",
            type: 'column',
            data: []
          },
        ]
        let seriesArea = [
          {name: 'Graph Runtime',
           type: 'line',
           data: []
          },
          {name: 'Node Runtime',
           type: 'line',
           data: []
          }
        ]
        for(i=0;i<7;i++){
          seriesBarChart[0].data.push(dataChart[i]['number_of_bug_node'])
          seriesBarChart[1].data.push(dataChart[i]['number_of_normal_node'])
          seriesArea[0].data.push(dataChart[i]['graph_runtime'])
          seriesArea[1].data.push(dataChart[i]['node_runtime'])
        }
        // HeatMap serires
        let seriesHeatMap = [
          {name: 'Access_control',
           data: dataChart[0]['bug_density']},
          {name: 'Arithmetic',
          data: dataChart[1]['bug_density']},
          {name: 'Denial_of_service',
          data: dataChart[2]['bug_density']},
          {name: 'Front_running',
          data: dataChart[3]['bug_density']},
          {name: 'Reentrancy',
          data: dataChart[4]['bug_density']},
          {name: 'Time_manipulation',
          data: dataChart[5]['bug_density']},
          {name: 'Unchecked_low_level_calls_red',
          data: dataChart[6]['bug_density']},
        ]
        
        this.setState({changeBugType: false})
        this.setState({seriesBarChart:seriesBarChart})
        this.setState({seriesArea:seriesArea})
        this.setState({seriesHeatMap:seriesHeatMap})
      }
    }

    handleSubmit = (event) => {
      event.preventDefault()
    }

    callbackFunction = (graphData) => {
      this.setState({ClickNode: graphData})
    }

    ShowChart=(event)=>{
      this.setState({DataChart:this.detectReports})
      this.setState({showBarChart:true})
      this.setState({showHeatMap: true})
    }

    //Show syntax highlight code and graph
    
    render() {
      const selectOptions=this.state.selectOptions;
      return (
        
        <div className='App'>
          <div className='top'>
          <div id='github'>
            <GithubCorner href='https://github.com/CIKM-2021/hive-db' direction='left'/>
          </div>
            <h1>🏁 Smart Contract Vulnerability Detection - SCO Demo</h1>
            <a href="https://github.com/erichoang/ge-sc">
              More details
            </a>
            <p>
              This is the quick vulnerability detection demo for <em>7 types of bug</em> in smart contract.
            </p>
          </div>
          <form onSubmit={this.handleSubmit} id="form">
          <div className='ControlsBox'>
                <input type="file" className='inputfile' id="input" onChange={this.onFileChange} hidden="hidden" />
                <div>
                    <button type="button" id = "custom-button" onClick={this.onClickChooseFile}>CHOOSE A FILE</button>
                    <span id="custom-text"> No file chosen</span>
                </div>
                <Select options={optionsSelect}
                onChange={this.onSelectChange}
                />
                <button className="Button" type="submit" onClick={this.onSubmit}> Submit </button>
                <DarkBackground disappear={this.state.isLoading}>
                  <LoadingOverlay
                    active={true}
                    // spinner={<BounceLoader />}
                    spinner={true}
                    text="Scanning smart contract ... "
                  >
                  </LoadingOverlay>
                </DarkBackground>
          </div>
          <hr/>
          {/* <div>
            <button className="Button" type="submit" onClick={this.onClickSample}> 0x23a91059fdc9579a9fbd0edc5f2ea0bfdb70deb4.sol</button>
            <button className="Button" type="submit" onClick={this.onClickSample}> simple_dao.sol</button>
            <button className="Button" type="submit" onClick={this.onClickSample}> multiowned_vulnerable.sol</button>
            <button className="Button" type="submit" onClick={this.onClickSample}> buggy_1.sol</button>
          </div> */}
          </form>
          <div>
          <Alert
            header={'Failed!'}
            btnText={'Close'}
            text={this.state.alert.text}
            type={this.state.alert.type}
            show={this.state.alert.show}
            onClosePress={this.onCloseAlert}
            pressCloseOnOutsideClick={true}
            showBorderBottom={true}
            alertStyles={{}}
            headerStyles={{}}
            textStyles={{}}
            buttonStyles={{}}
            />
          </div>
            <Graph_check
            Submit={this.state.showGraphCheck}
            Access_control={this.state.Access_control}
            Arithmetic={this.state.Arithmetic}
            Denial_of_service={this.state.Denial_of_service}
            Front_running={this.state.Front_running}
            Reentrancy={this.state.Reentrancy}
            Time_manipulation={this.state.Time_manipulation}
            Unchecked_low_level_calls={this.state.Unchecked_low_level_calls}
            Access_control_button={this.onClickDetail_Access_control}
            Arithmetic_button={this.onClickDetail_Arithmetic}
            Denial_of_service_button={this.onClickDetail_Denial_of_service}
            Front_running_button={this.onClickDetail_Front_running}
            Reentrancy_button={this.onClickDetail_Reentrancy}
            Time_manipulation_button={this.onClickDetail_Time_manipulation}
            Unchecked_low_level_calls_button={this.onClickDetail_Unchecked_low_level_calls}
            ></Graph_check>

            <Detail_error
            Detail={this.state.showDetailCode}
            arrayerrorline={this.state.arrayerrorline}
            graph={this.state.graph}
            codeString={this.state.codeString}
            parentCallback={this.callbackFunction}
            ClickNode={this.state.ClickNode}
            ></Detail_error>

            <StackedChart 
            series={this.state.seriesBarChart}
            heatMapSeries={this.state.seriesHeatMap}
            areaSeries={this.state.seriesArea}
            Click={this.ShowChart} 
            showBarChart={this.state.showBarChart}
            showGraphCheck={this.state.showGraphCheck}
            ></StackedChart>
        </div>
      )
    }
  }

  export default App 



