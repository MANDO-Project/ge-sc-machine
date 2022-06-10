import React,{Component} from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import {coy} from 'react-syntax-highlighter/dist/esm/styles/prism';
export default class SyntaxHighlighter_code extends Component{
  constructor(props){
    super(props);
    this.state = { 
      // Initially, no file is selected 
      
      arrayerrorline:[],
    }; 

  }

  componentDidUpdate(prevProps,prevState){
    if((prevProps.detectResults!==this.props.detectResults)||prevProps.ClickNode!==this.props.ClickNode){
      
      let array = []
      let ArrayUniq = []
      let self=this

      var data=this.props.detectResults;
      data["results"].forEach((node, index) => {
        if (node["vulnerability"] == 1) {
          array = [...array, ...node["code_lines"]]
          ArrayUniq = [...new Set(array)];
        }
      })
      self.setState({arrayerrorline:ArrayUniq});
    }
  };



    render(){
      const linesToHighlight = this.state.arrayerrorline,startingLineNumber = 1;
        
        return(
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
                        style.backgroundColor = "#DC143C";
                      }
                      return { style };
                  }}>
                  {this.props.codeString}
              </SyntaxHighlighter>
            
        )
    }
}

