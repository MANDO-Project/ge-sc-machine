import React,{Component} from 'react'; 
import Styles from "./components/Styles";

class App extends Component { 

    state = { 
      // Initially, no file is selected 
      selectedFile: null,
      detectResults: null
    }; 
     
    // On file select (from the pop up) 
    onFileChange = event => { 
      // Update the state 
      this.setState({ selectedFile: event.target.files[0] });
    }; 
     
    // On file upload (click the upload button) 
    onSubmit = () => { 
      // Create an object of formData 
      const formData = new FormData(); 
      const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'key': 'MqQVfJ6Fq1umZnUI7ZuaycciCjxi3gM0'},
        body: JSON.stringify({ filename: this.state.selectedFile.name})
      };
      fetch('http://localhost:5555/v1.0.0/vulnerability/detection/line', requestOptions)
      .then(response => response.json())
      .then(data => this.setState({ detectResults: data}));
     
      // Details of the uploaded file 
      console.log(this.state.selectedFile); 
    }; 

    handleSubmit = (event) => {
      event.preventDefault();
    };
     
    render() { 
      return ( 
        <Styles>
          <form onSubmit={this.handleSubmit}>
            <h1>🏁 Smart Contract Vulnerability Detection - SCO Demo</h1>
            <a href="https://github.com/erichoang/ge-sc">
              More details
            </a>
            <p>
              This is the quick vulnerability detection demo for <em>reentrancy</em> bug in smart contract.
            </p>
            <div> 
                <input type="file" onChange={this.onFileChange} />
                <div className="buttons">
                  <button
                    type="submit"
                    onClick={this.onSubmit}
                  >
                    Submit
                  </button>
                </div>
            </div>
            <p>File Name: {this.state.selectedFileName}</p>
            <pre>{JSON.stringify(this.state.detectResults, null, 4)}</pre>
          </form>
        </Styles> 
      ); 
    } 
  } 
  
  export default App; 
