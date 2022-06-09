import React,{Component} from 'react'; 
import Graph from "./components/Graph";
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import {coy} from 'react-syntax-highlighter/dist/esm/styles/prism';
import "./App.css";
import { ForceGraph2D} from 'react-force-graph';


class App extends Component { 

    constructor(props){
      super(props);
      this.state = { 
        // Initially, no file is selected 
        selectedFile: null,
        detectResults: null,
        codeString :"",
        graph:{nodes: [],links: [],},
        arrayerrorline:[],
        ClickNode:[]
      }; 

    }

    callbackFunction = (graphData) => {
      this.setState({ClickNode: graphData})
    }

    // On file select (from the pop up) 
    onFileChange = event => { 
      // Update the state 
      this.setState({ selectedFile: event.target.files[0] });
      this.setState({ClickNode:[]})
    }
    // On file upload (click the upload button) 
    onSubmit = () => {
      
      // Create an object of formData 
      let error_type=document.getElementById('selectError').value;
      console.log(error_type)
      console.log(this.state.selectedFile.name)
      let link='http://localhost:5555/v1.0.0/vulnerability/detection/line/'+error_type
      console.log(link)
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({ filename: this.state.selectedFile.name})
      };
      fetch(link, requestOptions)
      .then(response => response.json())
      .then(data => this.setState({ detectResults: data}));
      
      console.log(this.state.detectResults);
        
    }; 
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
    
     
    render() {
      const linesToHighlight = this.state.arrayerrorline,startingLineNumber = 1;
      const data=this.state.graph
      const nodes=data["nodes"].flat().map(app=>({id:app.id,name:app.name,nodeColor: app.color,code_lines:app.code_lines,error:app.error}))
      const links=data["links"].flat().map(app=>({"source":app.source,"target":app.target}))
      const myGraph={nodes,links};
      const error=data["nodes"].flat().map(app=>({id:app.id,error:app.error}))
      
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
                <input type="file" className='inputfile' id="input" onChange={this.onFileChange}/>

                <select className='selectError' id='selectError'  defaultValue={"reentrancy"} onChange={this.onSelectChange}>
                  <option value="access_control">access_control</option>
                  <option value="arithmetic">arithmetic</option>
                  <option value="denial_of_service">denial_of_service</option>
                  <option value="front_running">front_running</option>
                  <option value="reentrancy">reentrancy</option>
                  <option value="time_manipulation">time_manipulation</option>
                  <option value="unchecked_low_level_calls">unchecked_low_level_calls</option>
                </select>
                
                <button className="Button" type="submit" onClick={this.onSubmit}> Submit </button>  
          </div>
          </form> 
          <div className='PanelsBox'> 
              <SyntaxHighlighter
                  startingLineNumber={startingLineNumber}
                  language='solidity'
                  style={coy}
                  className='highlight'
                  showLineNumbers
                  wrapLines
                  lineProps={(lineNumber) => {
                      const style = { display: "block", width: "fit-content" };
                      if (linesToHighlight.includes(lineNumber)) {
                          style.backgroundColor = "#ffe7a4";
                      }
                      if(this.state.ClickNode.includes(lineNumber)){
                        style.border = "1px solid red";
                      }
                      return { style };
                  }}>
                  {this.state.codeString}
              </SyntaxHighlighter>
            <div className='Graph'>
              <Graph ClickNode={this.state.ClickNode} graph={this.state.graph} parentCallback = {this.callbackFunction}></Graph>
            </div>     
          </div>  
        </div> 
      ); 
    } 
  } 
  
  export default App; 
  


