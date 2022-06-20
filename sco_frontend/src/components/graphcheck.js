import React,{Component} from 'react'
import "./graphcheck.css";
export default class  Graph_check extends Component{
  constructor(props){
    super(props);
  }
    render(){
      if(this.props.Submit){
        return(
                <div className='graphcheck'>
                  <div className='legend_button'>
                    <div className='note' ><span id='red_legend' ></span> Bug</div> 
                    <div className='note' ><span id='green_legend' ></span> Clean</div> 
                    <hr color='#ccc'></hr>
                  </div>
  
                <div className='results'>
                      <button className={this.props.Access_control} onClick={this.props.Access_control_button}>
                        Access_control
                      </button>
                      <button className={this.props.Arithmetic} onClick={this.props.Arithmetic_button}>
                        Arithmetic
                      </button>
                      <button className={this.props.Denial_of_service}onClick={this.props.Denial_of_service_button}>
                        Denial_of_service
                      </button>
                      <button className={this.props.Front_running} onClick={this.props.Front_running_button}>
                        Front_running
                      </button>
                      <button className={this.props.Reentrancy} onClick={this.props.Reentrancy_button}>
                        Reentrancy
                      </button>
                      <button className={this.props.Time_manipulation}onClick={this.props.Time_manipulation_button}>
                        Time_manipulation
                      </button>
                      <button className={this.props.Unchecked_low_level_calls}onClick={this.props.Unchecked_low_level_calls_button}>
                        Unchecked_low_level_calls
                      </button>
                </div>
                </div>
              );
      }
        else return null;

    }
}