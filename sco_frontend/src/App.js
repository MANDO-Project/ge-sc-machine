import React,{Component} from 'react'; 
import "./App.css";
import Detail_error from './components/SH_code';
import StackedChart from './components/Chart';
import Graph_check from './components/graphcheck';



class App extends Component { 

    constructor(props){
      super(props);
      this.state = { 
        // Initially, no file is selected 
        base64String:null,
        detectResults: null,
        selectedFile:null,
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
        showGraphCheck: true,
        showDetailCode:true,
        showBarChart:false,
        Error_type:{ Access_control:1,
        Arithmetic:0,
        Denial_of_service:1,
        Front_running:0,
        Reentrancy:1,
        Time_manipulation:0,
        Unchecked_low_level_calls:1},
        series: [{
          name: 'BUG',
          color: "#C80A0A",
          data: []
        }, {
          name: 'CLEAN',
          data: []
        }],
        
      }; 

    }

    onClickChooseFile = (event) =>{
      const realFileBtn = document.getElementById("input");
      realFileBtn.click();
    };

    // On file select (from the pop up) 
    onFileChange = event => { 
      // Update the state 
      this.setState({ selectedFile: event.target.files[0] });
      this.setState({ClickNode:[]});
      this.setState({showBarChart:false,showDetailCode:false,showGraphCheck:false});

      // Customize choose file button 
      const customTxt = document.getElementById("custom-text");
      if (event.target.files[0]) {
        customTxt.innerHTML = event.target.files[0].name;
      } else {
        customTxt.innerHTML = "No file chosen";
      }
      //Convert a file to base64 string 
      var fileInput = document.getElementById('input').files;
      console.log(fileInput);
      const reader = new FileReader();
      let self=this;
      
      
      reader.readAsDataURL(fileInput[0]);
      reader.onload = function () {
        const data = reader.result
                .replace('data:', '')
                .replace(/^.+,/, ''); 
        self.setState({base64String:data})
      };
      reader.onerror = function (error) {
        console.log('Error: ', error);
      }; 
    }

    //Check to see what kind of errors the code encounters
    onSubmit = () => {
      //connect graph backend
      console.log(JSON.stringify({smart_contract:this.state.base64String}));
      let link='http://localhost:5555/v1.0.0/vulnerability/detection/graph/test'
      console.log(link)
      const requestOptions = {
        method: 'POST',
        headers: { 'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'}
      };
      fetch(link, requestOptions)
      .then(response => response.json())
      .then(data =>console.log(data));
      // Return vulnerability detection of 7 types of bug in smartcontract
      let typeBugs=this.state.Error_type;
      if(typeBugs.Access_control===1){
        this.setState({Access_control:'Access_control_green'});
      }
      else  this.setState({Access_control:'Access_control_red'});
      if(typeBugs.Arithmetic===1){
        this.setState({Arithmetic:'Arithmetic_green'});
      }
      else  this.setState({Arithmetic:'Arithmetic_red'});
      if(typeBugs.Denial_of_service===1){
        this.setState({Denial_of_service:'Denial_of_service_green'});
      }
      else  this.setState({Denial_of_service:'Denial_of_service_red'});
      if(typeBugs.Front_running===1){
        this.setState({Front_running:'Front_running_green'});
      }
      else  this.setState({Front_running:'Front_running_red'});
      if(typeBugs.Reentrancy===1){
        this.setState({Reentrancy:'Reentrancy_green'});
      }
      else  this.setState({Reentrancy:'Reentrancy_red'});
      if(typeBugs.Time_manipulation===1){
        this.setState({Time_manipulation:'Time_manipulation_green'});
      }
      else  this.setState({Time_manipulation:'Time_manipulation_red'});
      if(typeBugs. Unchecked_low_level_calls===1){
        this.setState({Unchecked_low_level_calls:'Unchecked_low_level_calls_green'});
      }
      else  this.setState({Unchecked_low_level_calls:'Unchecked_low_level_calls_red'});

      this.setState({showGraphCheck:true});
    }; 

    onClickDetail = event =>{
      this.setState({showDetailCode:true})
      let link='http://localhost:5555/v1.0.0/vulnerability/detection/line/reentrancy'
      console.log(link)
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({ filename: this.state.selectedFile.name})
      };
      fetch(link, requestOptions)
      .then(response => response.json())
      .then(data => this.setState({ detectResults: data}));
    }
    componentDidUpdate(prevProps,prevState){
      if(prevState.detectResults!==this.state.detectResults){
        var input = document.querySelector('input[type=file]').files[0];
          
        var reader = new FileReader();
        
        let array = []
        let ArrayUniq = []
        let self=this
      
        var data=this.state.detectResults;
        self.setState({graph:data["graph"]})
        console.log(data);
        reader.onload = function (event) {
          self.setState({codeString: event.target.result})        
          data["results"].forEach((node, index) => {
            if (node["vulnerability"] == 1) {
              array = [...array, ...node["code_lines"]]
              ArrayUniq = [...new Set(array)];
            }
          })
          self.setState({arrayerrorline:ArrayUniq});
          
        };
        reader.readAsBinaryString(input);
        
      }
    };

    handleSubmit = (event) => {
      event.preventDefault();
    };

    callbackFunction = (graphData) => {
      this.setState({ClickNode: graphData})
    }
 
    ShowChart=(event)=>{
      this.setState({showBarChart:true});
      let bug= [44, 55, 0, 67, 22, 0, 21];
      let clean = [56, 45, 100, 33, 78, 100, 79];
      var i=0;
      var tmp=0;
      let series=[{
        name: 'BUG',
        color: "#C80A0A",
        data: []
      }, {
        name: 'CLEAN',
        data: []
      }];
      for(i=0;i<7;i++){
        tmp=bug[i];
        series[0].data.push(tmp);
        tmp=clean[i];
        series[1].data.push(tmp);
      }
      this.setState({series:series});
    };

    //Show syntax highlight code and graph
    
    
     
    render() {
      return ( 
        <div className='App'>
          <div className='top'>
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
                <button className="Button" type="submit" onClick={this.onSubmit}> Submit </button>  
          </div>
          </form>
          <Graph_check
          Submit={this.state.showGraphCheck}
          updateDetail={this.onClickDetail}
          Access_control={this.state.Access_control}
          Arithmetic={this.state.Arithmetic}
          Denial_of_service={this.state.Denial_of_service}
          Front_running={this.state.Front_running}
          Reentrancy={this.state.Reentrancy}
          Time_manipulation={this.state.Time_manipulation}
          Unchecked_low_level_calls={this.state.Unchecked_low_level_calls}
          ></Graph_check>

          <StackedChart series={this.state.series} 
          Click={this.ShowChart} 
          showBarChart={this.state.showBarChart}
          showGraphCheck={this.state.showGraphCheck}
          ></StackedChart>

          <Detail_error
          Detail={this.state.showDetailCode}
          arrayerrorline={this.state.arrayerrorline}
          graph={this.state.graph}
          codeString={this.state.codeString}
          parentCallback={this.callbackFunction}
          ClickNode={this.state.ClickNode}
          ></Detail_error>
          
        </div> 
      ); 
    } 
  } 
  
  export default App; 
  


