import React,{PureComponent,useCallback} from 'react';
import { ForceGraph2D} from 'react-force-graph';
import "./graph.css";
export default class Graph extends PureComponent{
    shouldComponentUpdate(nextProps) {
        if (this.props.ClickNode === nextProps.ClickNode) {
            console.log("graph-reload")
            return true;
        }
        return false;
    }
    
    render(){

      const data=this.props.graph
      const nodes=data["nodes"].flat().map(app=>({id:app.id,name:app.name,nodeColor: app.color,code_lines:app.code_lines,error:app.error}))
      const links=data["links"].flat().map(app=>({"source":app.source,"target":app.target}))
      const myGraph={nodes,links};
        
        const paintRing = (node, ctx) => {
            // add ring just for highlighted nodes
            let gData=myGraph;
            ctx.beginPath();
            ctx.arc(node.x, node.y, 5 * 1.8, 0, 2 * Math.PI, false);
            ctx.fillStyle = gData.nodes[node.id].nodeColor;
            ctx.fill();
            ctx.stroke();
          };

          
        const handleClick=(node)=>{
            let result=myGraph.nodes[node.id].code_lines;
            this.props.parentCallback(result);
        };
        const draw_red_circle=()=>{
        var canvas = document.getElementById('circle');
        if (canvas.getContext)
            {
            var ctx = canvas.getContext('2d'); 
            var X = canvas.width / 2;
            var Y = canvas.height / 2;
            var R = 45;
            ctx.beginPath();
            ctx.arc(X, Y, R, 0, 2 * Math.PI, false);
            ctx.lineWidth = 3;
            ctx.strokeStyle = '#FF0000';
            ctx.stroke();
            ctx.fill();
            }
        }
        return(
            <div onLoad={draw_red_circle}>
                <div className='comment'>
                <div className='line'>
                    <div className='col' ><span id='entrypoint' ></span>  Entry_point</div> 
                    <div className='col' ><span id='new_var' ></span>New_var</div>  
                    <div className='col' ><span id='expression' ></span>  Expression</div>   
                    <div className='col' ><span id='if' ></span>  If</div>  
                    <div className='col' ><span id='endif' ></span> EndIf</div>  
                </div>
                <div className='line'>
                    <div className='col' ><span id='bg_loop' ></span>  BG Loop  </div>  
                    <div className='col' ><span id='other' ></span>  Other</div>  
                    <div className='col' ><span id='throw' ></span>  Throw</div>   
                    <div className='col' ><span id='continue' ></span>  Continue</div>  
                    <div className='col' ><span id='return' ></span>  Return</div>  
                </div>
                <div className='line'>
                    <div className='col' ><span id='inline' ></span>  Inline ASM</div> 
                    <div className='col' ><span id='func' ></span>  Func</div> 
                    <div className='col' ><span id='end_loop' ></span>  End Loop</div>   
                    <div className='col' ><span id='ifloop' ></span>  If Loop</div> 
                    <div className='col' ><span id='_' ></span>  _</div>  
                </div>
                </div>
                <ForceGraph2D graphData={myGraph} 
                nodeRelSize={5} width={580} height={520}
                nodeCanvasObject={paintRing}
                nodeCanvasObjectMode={node => 'before'}
                nodeColor={node=>myGraph.nodes[node.id].error==1? "red":"white"}
                linkDirectionalParticles={4}
                nodeLabel={node=>myGraph.nodes[node.id].name}
                onNodeClick={handleClick}
                />
            </div>
           
        )
    }
}

