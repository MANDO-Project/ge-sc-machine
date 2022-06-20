import React,{Component} from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import {coy} from 'react-syntax-highlighter/dist/esm/styles/prism';
import Graph from './Graph';
export default class  Detail_error extends Component{
  constructor(props){
    super(props);
  }
  callbackFunction = (graphData) => {
    this.props.parentCallback(graphData);
  }
    render(){
      const linesToHighlight = this.props.arrayerrorline,startingLineNumber = 1;
      if(this.props.Detail){
        return(
          <div>
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
                      if(this.props.ClickNode.includes(lineNumber)){
                        style.border = "4px solid red";
                      }
                      return { style };
                  }}>
                  {this.props.codeString}
              </SyntaxHighlighter>
              <div className='Graph'>
                <Graph  ClickNode={this.props.ClickNode} 
                        graph={this.props.graph} 
                        parentCallback = {this.callbackFunction}></Graph>
              </div>   
            </div>
            <div className='Lenged'>
              <div className='Code_Lenged'>
                <div className='note'><span id='yellow' ></span> Buggy Code Line</div> 
                <div className='note'><span id='red_border' ></span> Code Line of Selected Node </div> 
              </div>
              <div className='Graph_Lenged'>
                <div className='note'><span id='red' ></span> Bug Node</div> 
                <div className='note'><span id='white' ></span> Clean Node</div> 
              </div>
            </div>
          </div>
        )
      }
        else return null;

    }
}

