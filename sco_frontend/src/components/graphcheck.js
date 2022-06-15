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
                      <button className={this.props.Access_control} onClick={this.props.updateDetail}>
                        Access_control
                      </button>
                      <button className={this.props.Arithmetic} onClick={this.props.updateDetail}>
                        Arithmetic
                      </button>
                      <button className={this.props.Denial_of_service}onClick={this.props.updateDetail}>
                        Denial_of_service
                      </button>
                      <button className={this.props.Front_running} onClick={this.props.updateDetail}>
                        Front_running
                      </button>
                      <button className={this.props.Reentrancy} onClick={this.props.updateDetail}>
                        Reentrancy
                      </button>
                      <button className={this.props.Time_manipulation}onClick={this.props.updateDetail}>
                        Time_manipulation
                      </button>
                      <button className={this.props.Unchecked_low_level_calls}onClick={this.props.updateDetail}>
                        Unchecked_low_level_calls
                      </button>
                </div>
                </div>
              );
      }
        else return null;

    }
}