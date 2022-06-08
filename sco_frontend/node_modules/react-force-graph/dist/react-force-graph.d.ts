import * as React from 'react';
import { Object3D, Material, Scene, Camera, WebGLRenderer } from 'three';
import { ConfigOptions, ForceGraphVRInstance } from '3d-force-graph-vr';
import { ConfigOptions as ConfigOptions$1, ForceGraphARInstance } from '3d-force-graph-ar';
import { EffectComposer } from 'three/examples/jsm/postprocessing/EffectComposer.js';
import { ConfigOptions as ConfigOptions$2, ForceGraph3DInstance } from '3d-force-graph';
import { ForceGraphInstance } from 'force-graph';

interface GraphData$3 {
  nodes: NodeObject$3[];
  links: LinkObject$3[];
}

type NodeObject$3 = object & {
  id?: string | number;
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  fx?: number;
  fy?: number;
  fz?: number;
};

type LinkObject$3 = object & {
  source?: string | number | NodeObject$3;
  target?: string | number | NodeObject$3;
};

type Accessor$3<In, Out> = Out | string | ((obj: In) => Out);
type NodeAccessor$3<T> = Accessor$3<NodeObject$3, T>;
type LinkAccessor$3<T> = Accessor$3<LinkObject$3, T>;

type DagMode$3 = 'td' | 'bu' | 'lr' | 'rl' | 'zout' | 'zin' | 'radialout' | 'radialin';

type ForceEngine$2 = 'd3' | 'ngraph';

interface ForceFn$3 {
  (alpha: number): void;
  initialize?: (nodes: NodeObject$3[], ...args: any[]) => void;
  [key: string]: any;
}

type Coords$2 = { x: number; y: number; z: number; }

type LinkPositionUpdateFn$2 = (obj: Object3D, coords: { start: Coords$2, end: Coords$2 }, link: LinkObject$3) => null | boolean;

interface ForceGraphProps$3 extends ConfigOptions {
  // Data input
  graphData?: GraphData$3;
  nodeId?: string;
  linkSource?: string;
  linkTarget?: string;

  // Container layout
  width?: number;
  height?: number;
  yOffset?: number;
  glScale?: number;

  // Node styling
  nodeLabel?: NodeAccessor$3<string>;
  nodeDesc?: NodeAccessor$3<string>;
  nodeRelSize?: number;
  nodeVal?: NodeAccessor$3<number>;
  nodeVisibility?: NodeAccessor$3<boolean>;
  nodeColor?: NodeAccessor$3<string>;
  nodeAutoColorBy?: NodeAccessor$3<string | null>;
  nodeOpacity?: number;
  nodeResolution?: number;
  nodeThreeObject?: NodeAccessor$3<Object3D>;
  nodeThreeObjectExtend?: NodeAccessor$3<boolean>;

  // Link styling
  linkLabel?: LinkAccessor$3<string>;
  linkDesc?: LinkAccessor$3<string>;
  linkVisibility?: LinkAccessor$3<boolean>;
  linkColor?: LinkAccessor$3<string>;
  linkAutoColorBy?: LinkAccessor$3<string | null>;
  linkWidth?: LinkAccessor$3<number>;
  linkOpacity?: number;
  linkResolution?: number;
  linkCurvature?: LinkAccessor$3<number>;
  linkCurveRotation?: LinkAccessor$3<number>;
  linkMaterial?: LinkAccessor$3<Material | boolean | null>;
  linkThreeObject?: LinkAccessor$3<Object3D>;
  linkThreeObjectExtend?: LinkAccessor$3<boolean>;
  linkPositionUpdate?: LinkPositionUpdateFn$2 | null;
  linkDirectionalArrowLength?: LinkAccessor$3<number>;
  linkDirectionalArrowColor?: LinkAccessor$3<string>;
  linkDirectionalArrowRelPos?: LinkAccessor$3<number>;
  linkDirectionalArrowResolution?: number;
  linkDirectionalParticles?: LinkAccessor$3<number>;
  linkDirectionalParticleSpeed?: LinkAccessor$3<number>;
  linkDirectionalParticleWidth?: LinkAccessor$3<number>;
  linkDirectionalParticleColor?: LinkAccessor$3<string>;
  linkDirectionalParticleResolution?: number;

  // Force engine (d3-force) configuration
  forceEngine?: ForceEngine$2;
  numDimensions?: 1 | 2 | 3;
  dagMode?: DagMode$3;
  dagLevelDistance?: number | null;
  dagNodeFilter?: (node: NodeObject$3) => boolean;
  onDagError?: ((loopNodeIds: (string | number)[]) => void) | undefined;
  d3AlphaMin?: number;
  d3AlphaDecay?: number;
  d3VelocityDecay?: number;
  ngraphPhysics?: object;
  warmupTicks?: number;
  cooldownTicks?: number;
  cooldownTime?: number;
  onEngineTick?: () => void;
  onEngineStop?: () => void;

  // Interaction
  onNodeHover?: (node: NodeObject$3 | null, previousNode: NodeObject$3 | null) => void;
  onNodeClick?: (link: LinkObject$3) => void;
  onLinkHover?: (link: LinkObject$3 | null, previousLink: LinkObject$3 | null) => void;
  onLinkClick?: (link: LinkObject$3) => void;
}

interface ForceGraphMethods$3 {
  // Link styling
  emitParticle(link: LinkObject$3): ForceGraphVRInstance;

  // Force engine (d3-force) configuration
  d3Force(forceName: 'link' | 'charge' | 'center' | string): ForceFn$3 | undefined;
  d3Force(forceName: 'link' | 'charge' | 'center' | string, forceFn: ForceFn$3): ForceGraphVRInstance;
  d3ReheatSimulation(): ForceGraphVRInstance;

  // Render control
  refresh(): ForceGraphVRInstance;

  // Utility
  getGraphBbox(nodeFilter?: (node: NodeObject$3) => boolean): { x: [number, number], y: [number, number], z: [number, number] };
}

type FCwithRef$3<P = {}, R = {}> = React.FunctionComponent<P & { ref?: React.MutableRefObject<R | undefined> }>;

declare const ForceGraph$3: FCwithRef$3<ForceGraphProps$3, ForceGraphMethods$3>;

interface GraphData$2 {
  nodes: NodeObject$2[];
  links: LinkObject$2[];
}

type NodeObject$2 = object & {
  id?: string | number;
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  fx?: number;
  fy?: number;
  fz?: number;
};

type LinkObject$2 = object & {
  source?: string | number | NodeObject$2;
  target?: string | number | NodeObject$2;
};

type Accessor$2<In, Out> = Out | string | ((obj: In) => Out);
type NodeAccessor$2<T> = Accessor$2<NodeObject$2, T>;
type LinkAccessor$2<T> = Accessor$2<LinkObject$2, T>;

type DagMode$2 = 'td' | 'bu' | 'lr' | 'rl' | 'zout' | 'zin' | 'radialout' | 'radialin';

type ForceEngine$1 = 'd3' | 'ngraph';

interface ForceFn$2 {
  (alpha: number): void;
  initialize?: (nodes: NodeObject$2[], ...args: any[]) => void;
  [key: string]: any;
}

type Coords$1 = { x: number; y: number; z: number; }

type LinkPositionUpdateFn$1 = (obj: Object3D, coords: { start: Coords$1, end: Coords$1 }, link: LinkObject$2) => null | boolean;

interface ForceGraphProps$2 extends ConfigOptions$1 {
  // Data input
  graphData?: GraphData$2;
  nodeId?: string;
  linkSource?: string;
  linkTarget?: string;

  // Container layout
  width?: number;
  height?: number;
  backgroundColor?: string;
  showNavInfo?: boolean;

  // Node styling
  nodeRelSize?: number;
  nodeVal?: NodeAccessor$2<number>;
  nodeVisibility?: NodeAccessor$2<boolean>;
  nodeColor?: NodeAccessor$2<string>;
  nodeAutoColorBy?: NodeAccessor$2<string | null>;
  nodeOpacity?: number;
  nodeResolution?: number;
  nodeThreeObject?: NodeAccessor$2<Object3D>;
  nodeThreeObjectExtend?: NodeAccessor$2<boolean>;

  // Link styling
  linkVisibility?: LinkAccessor$2<boolean>;
  linkColor?: LinkAccessor$2<string>;
  linkAutoColorBy?: LinkAccessor$2<string | null>;
  linkWidth?: LinkAccessor$2<number>;
  linkOpacity?: number;
  linkResolution?: number;
  linkCurvature?: LinkAccessor$2<number>;
  linkCurveRotation?: LinkAccessor$2<number>;
  linkMaterial?: LinkAccessor$2<Material | boolean | null>;
  linkThreeObject?: LinkAccessor$2<Object3D>;
  linkThreeObjectExtend?: LinkAccessor$2<boolean>;
  linkPositionUpdate?: LinkPositionUpdateFn$1 | null;
  linkDirectionalArrowLength?: LinkAccessor$2<number>;
  linkDirectionalArrowColor?: LinkAccessor$2<string>;
  linkDirectionalArrowRelPos?: LinkAccessor$2<number>;
  linkDirectionalArrowResolution?: number;
  linkDirectionalParticles?: LinkAccessor$2<number>;
  linkDirectionalParticleSpeed?: LinkAccessor$2<number>;
  linkDirectionalParticleWidth?: LinkAccessor$2<number>;
  linkDirectionalParticleColor?: LinkAccessor$2<string>;
  linkDirectionalParticleResolution?: number;

  // Force engine (d3-force) configuration
  forceEngine?: ForceEngine$1;
  numDimensions?: 1 | 2 | 3;
  dagMode?: DagMode$2;
  dagLevelDistance?: number | null;
  dagNodeFilter?: (node: NodeObject$2) => boolean;
  onDagError?: ((loopNodeIds: (string | number)[]) => void) | undefined;
  d3AlphaMin?: number;
  d3AlphaDecay?: number;
  d3VelocityDecay?: number;
  ngraphPhysics?: object;
  warmupTicks?: number;
  cooldownTicks?: number;
  cooldownTime?: number;
  onEngineTick?: () => void;
  onEngineStop?: () => void;

  // Interaction
  onNodeHover?: (node: NodeObject$2 | null, previousNode: NodeObject$2 | null) => void;
  onNodeClick?: (link: LinkObject$2) => void;
  onLinkHover?: (link: LinkObject$2 | null, previousLink: LinkObject$2 | null) => void;
  onLinkClick?: (link: LinkObject$2) => void;
}

interface ForceGraphMethods$2 {
  // Link styling
  emitParticle(link: LinkObject$2): ForceGraphARInstance;

  // Force engine (d3-force) configuration
  d3Force(forceName: 'link' | 'charge' | 'center' | string): ForceFn$2 | undefined;
  d3Force(forceName: 'link' | 'charge' | 'center' | string, forceFn: ForceFn$2): ForceGraphARInstance;
  d3ReheatSimulation(): ForceGraphARInstance;

  // Render control
  refresh(): ForceGraphARInstance;

  // Utility
  getGraphBbox(nodeFilter?: (node: NodeObject$2) => boolean): { x: [number, number], y: [number, number], z: [number, number] };
}

type FCwithRef$2<P = {}, R = {}> = React.FunctionComponent<P & { ref?: React.MutableRefObject<R | undefined> }>;

declare const ForceGraph$2: FCwithRef$2<ForceGraphProps$2, ForceGraphMethods$2>;

interface GraphData$1 {
  nodes: NodeObject$1[];
  links: LinkObject$1[];
}

type NodeObject$1 = object & {
  id?: string | number;
  x?: number;
  y?: number;
  z?: number;
  vx?: number;
  vy?: number;
  vz?: number;
  fx?: number;
  fy?: number;
  fz?: number;
};

type LinkObject$1 = object & {
  source?: string | number | NodeObject$1;
  target?: string | number | NodeObject$1;
};

type Accessor$1<In, Out> = Out | string | ((obj: In) => Out);
type NodeAccessor$1<T> = Accessor$1<NodeObject$1, T>;
type LinkAccessor$1<T> = Accessor$1<LinkObject$1, T>;

type DagMode$1 = 'td' | 'bu' | 'lr' | 'rl' | 'zout' | 'zin' | 'radialout' | 'radialin';

type ForceEngine = 'd3' | 'ngraph';

interface ForceFn$1 {
  (alpha: number): void;
  initialize?: (nodes: NodeObject$1[], ...args: any[]) => void;
  [key: string]: any;
}

type Coords = { x: number; y: number; z: number; }

type LinkPositionUpdateFn = (obj: Object3D, coords: { start: Coords, end: Coords }, link: LinkObject$1) => null | boolean;

interface ForceGraphProps$1 extends ConfigOptions$2 {
  // Data input
  graphData?: GraphData$1;
  nodeId?: string;
  linkSource?: string;
  linkTarget?: string;

  // Container layout
  width?: number;
  height?: number;
  backgroundColor?: string;
  showNavInfo?: boolean;

  // Node styling
  nodeRelSize?: number;
  nodeVal?: NodeAccessor$1<number>;
  nodeLabel?: NodeAccessor$1<string>;
  nodeVisibility?: NodeAccessor$1<boolean>;
  nodeColor?: NodeAccessor$1<string>;
  nodeAutoColorBy?: NodeAccessor$1<string | null>;
  nodeOpacity?: number;
  nodeResolution?: number;
  nodeThreeObject?: NodeAccessor$1<Object3D>;
  nodeThreeObjectExtend?: NodeAccessor$1<boolean>;

  // Link styling
  linkLabel?: LinkAccessor$1<string>;
  linkVisibility?: LinkAccessor$1<boolean>;
  linkColor?: LinkAccessor$1<string>;
  linkAutoColorBy?: LinkAccessor$1<string | null>;
  linkWidth?: LinkAccessor$1<number>;
  linkOpacity?: number;
  linkResolution?: number;
  linkCurvature?: LinkAccessor$1<number>;
  linkCurveRotation?: LinkAccessor$1<number>;
  linkMaterial?: LinkAccessor$1<Material | boolean | null>;
  linkThreeObject?: LinkAccessor$1<Object3D>;
  linkThreeObjectExtend?: LinkAccessor$1<boolean>;
  linkPositionUpdate?: LinkPositionUpdateFn | null;
  linkDirectionalArrowLength?: LinkAccessor$1<number>;
  linkDirectionalArrowColor?: LinkAccessor$1<string>;
  linkDirectionalArrowRelPos?: LinkAccessor$1<number>;
  linkDirectionalArrowResolution?: number;
  linkDirectionalParticles?: LinkAccessor$1<number>;
  linkDirectionalParticleSpeed?: LinkAccessor$1<number>;
  linkDirectionalParticleWidth?: LinkAccessor$1<number>;
  linkDirectionalParticleColor?: LinkAccessor$1<string>;
  linkDirectionalParticleResolution?: number;

  // Force engine (d3-force) configuration
  forceEngine?: ForceEngine;
  numDimensions?: 1 | 2 | 3;
  dagMode?: DagMode$1;
  dagLevelDistance?: number | null;
  dagNodeFilter?: (node: NodeObject$1) => boolean;
  onDagError?: ((loopNodeIds: (string | number)[]) => void) | undefined;
  d3AlphaMin?: number;
  d3AlphaDecay?: number;
  d3VelocityDecay?: number;
  ngraphPhysics?: object;
  warmupTicks?: number;
  cooldownTicks?: number;
  cooldownTime?: number;
  onEngineTick?: () => void;
  onEngineStop?: () => void;

  // Interaction
  onNodeClick?: (node: NodeObject$1, event: MouseEvent) => void;
  onNodeRightClick?: (node: NodeObject$1, event: MouseEvent) => void;
  onNodeHover?: (node: NodeObject$1 | null, previousNode: NodeObject$1 | null) => void;
  onNodeDrag?: (node: NodeObject$1, translate: { x: number, y: number }) => void;
  onNodeDragEnd?: (node: NodeObject$1, translate: { x: number, y: number }) => void;
  onLinkClick?: (link: LinkObject$1, event: MouseEvent) => void;
  onLinkRightClick?: (link: LinkObject$1, event: MouseEvent) => void;
  onLinkHover?: (link: LinkObject$1 | null, previousLink: LinkObject$1 | null) => void;
  linkHoverPrecision?: number;
  onBackgroundClick?: (event: MouseEvent) => void;
  onBackgroundRightClick?: (event: MouseEvent) => void;
  enableNodeDrag?: boolean;
  enableNavigationControls?: boolean;
  enablePointerInteraction?: boolean;
}

interface ForceGraphMethods$1 {
  // Link styling
  emitParticle(link: LinkObject$1): ForceGraph3DInstance;

  // Force engine (d3-force) configuration
  d3Force(forceName: 'link' | 'charge' | 'center' | string): ForceFn$1 | undefined;
  d3Force(forceName: 'link' | 'charge' | 'center' | string, forceFn: ForceFn$1): ForceGraph3DInstance;
  d3ReheatSimulation(): ForceGraph3DInstance;

  // Render control
  pauseAnimation(): ForceGraph3DInstance;
  resumeAnimation(): ForceGraph3DInstance;
  cameraPosition(position: Partial<Coords>, lookAt?: Coords, transitionMs?: number): ForceGraph3DInstance;
  zoomToFit(durationMs?: number, padding?: number, nodeFilter?: (node: NodeObject$1) => boolean): ForceGraph3DInstance;
  postProcessingComposer(): EffectComposer;
  scene(): Scene;
  camera(): Camera;
  renderer(): WebGLRenderer;
  controls(): object;
  refresh(): ForceGraph3DInstance;

  // Utility
  getGraphBbox(nodeFilter?: (node: NodeObject$1) => boolean): { x: [number, number], y: [number, number], z: [number, number] };
  screen2GraphCoords(x: number, y: number, distance: number): Coords;
  graph2ScreenCoords(x: number, y: number, z: number): Coords;
}

type FCwithRef$1<P = {}, R = {}> = React.FunctionComponent<P & { ref?: React.MutableRefObject<R | undefined> }>;

declare const ForceGraph$1: FCwithRef$1<ForceGraphProps$1, ForceGraphMethods$1>;

interface GraphData {
  nodes: NodeObject[];
  links: LinkObject[];
}

type NodeObject = object & {
  id?: string | number;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number;
  fy?: number;
};

type LinkObject = object & {
  source?: string | number | NodeObject;
  target?: string | number | NodeObject;
};

type Accessor<In, Out> = Out | string | ((obj: In) => Out);
type NodeAccessor<T> = Accessor<NodeObject, T>;
type LinkAccessor<T> = Accessor<LinkObject, T>;

type CanvasCustomRenderMode = 'replace' | 'before' | 'after';
type CanvasCustomRenderFn<T> = (obj: T, canvasContext: CanvasRenderingContext2D, globalScale: number) => void;
type CanvasPointerAreaPaintFn<T> = (obj: T, paintColor: string, canvasContext: CanvasRenderingContext2D, globalScale: number) => void;

type DagMode = 'td' | 'bu' | 'lr' | 'rl' | 'radialout' | 'radialin';

interface ForceFn {
  (alpha: number): void;
  initialize?: (nodes: NodeObject[], ...args: any[]) => void;
  [key: string]: any;
}

interface ForceGraphProps {
  // Data input
  graphData?: GraphData;
  nodeId?: string;
  linkSource?: string;
  linkTarget?: string;

  // Container layout
  width?: number;
  height?: number;
  backgroundColor?: string;

  // Node styling
  nodeRelSize?: number;
  nodeVal?: NodeAccessor<number>;
  nodeLabel?: NodeAccessor<string>;
  nodeVisibility?: NodeAccessor<boolean>;
  nodeColor?: NodeAccessor<string>;
  nodeAutoColorBy?: NodeAccessor<string | null>;
  nodeCanvasObjectMode?: string | ((obj: NodeObject) => CanvasCustomRenderMode);
  nodeCanvasObject?: CanvasCustomRenderFn<NodeObject>;
  nodePointerAreaPaint?: CanvasPointerAreaPaintFn<NodeObject>;

  // Link styling
  linkLabel?: LinkAccessor<string>;
  linkVisibility?: LinkAccessor<boolean>;
  linkColor?: LinkAccessor<string>;
  linkAutoColorBy?: LinkAccessor<string | null>;
  linkLineDash?: LinkAccessor<number[] | null>;
  linkWidth?: LinkAccessor<number>;
  linkCurvature?: LinkAccessor<number>;
  linkCanvasObject?: CanvasCustomRenderFn<LinkObject>;
  linkCanvasObjectMode?: string | ((obj: LinkObject) => CanvasCustomRenderMode);
  linkDirectionalArrowLength?: LinkAccessor<number>;
  linkDirectionalArrowColor?: LinkAccessor<string>;
  linkDirectionalArrowRelPos?: LinkAccessor<number>;
  linkDirectionalParticles?: LinkAccessor<number>;
  linkDirectionalParticleSpeed?: LinkAccessor<number>;
  linkDirectionalParticleWidth?: LinkAccessor<number>;
  linkDirectionalParticleColor?: LinkAccessor<string>;
  linkPointerAreaPaint?: CanvasPointerAreaPaintFn<LinkObject>;

  // Render control
  autoPauseRedraw?: boolean;
  minZoom?: number;
  maxZoom?: number;
  onRenderFramePre?: (canvasContext: CanvasRenderingContext2D, globalScale: number) => void;
  onRenderFramePost?: (canvasContext: CanvasRenderingContext2D, globalScale: number) => void;

  // Force engine (d3-force) configuration
  dagMode?: DagMode;
  dagLevelDistance?: number | null;
  dagNodeFilter?: (node: NodeObject) => boolean;
  onDagError?: ((loopNodeIds: (string | number)[]) => void) | undefined;
  d3AlphaMin?: number;
  d3AlphaDecay?: number;
  d3VelocityDecay?: number;
  ngraphPhysics?: object;
  warmupTicks?: number;
  cooldownTicks?: number;
  cooldownTime?: number;
  onEngineTick?: () => void;
  onEngineStop?: () => void;

  // Interaction
  onNodeClick?: (node: NodeObject, event: MouseEvent) => void;
  onNodeRightClick?: (node: NodeObject, event: MouseEvent) => void;
  onNodeHover?: (node: NodeObject | null, previousNode: NodeObject | null) => void;
  onNodeDrag?: (node: NodeObject, translate: { x: number, y: number }) => void;
  onNodeDragEnd?: (node: NodeObject, translate: { x: number, y: number }) => void;
  onLinkClick?: (link: LinkObject, event: MouseEvent) => void;
  onLinkRightClick?: (link: LinkObject, event: MouseEvent) => void;
  onLinkHover?: (link: LinkObject | null, previousLink: LinkObject | null) => void;
  linkHoverPrecision?: number;
  onBackgroundClick?: (event: MouseEvent) => void;
  onBackgroundRightClick?: (event: MouseEvent) => void;
  onZoom?: (transform: {k: number, x: number, y: number}) => void;
  onZoomEnd?: (transform: {k: number, x: number, y: number}) => void;
  enableNodeDrag?: boolean;
  enableZoomInteraction?: boolean;
  enablePanInteraction?: boolean;
  enablePointerInteraction?: boolean;
}

interface ForceGraphMethods {
  // Link styling
  emitParticle(link: LinkObject): ForceGraphInstance;

  // Force engine (d3-force) configuration
  d3Force(forceName: 'link' | 'charge' | 'center' | string): ForceFn | undefined;
  d3Force(forceName: 'link' | 'charge' | 'center' | string, forceFn: ForceFn): ForceGraphInstance;
  d3ReheatSimulation(): ForceGraphInstance;

  // Render control
  pauseAnimation(): ForceGraphInstance;
  resumeAnimation(): ForceGraphInstance;
  centerAt(): {x: number, y: number};
  centerAt(x?: number, y?: number, durationMs?: number): ForceGraphInstance;
  zoom(): number;
  zoom(scale: number, durationMs?: number): ForceGraphInstance;
  zoomToFit(durationMs?: number, padding?: number, nodeFilter?: (node: NodeObject) => boolean): ForceGraphInstance;

  // Utility
  getGraphBbox(nodeFilter?: (node: NodeObject) => boolean): { x: [number, number], y: [number, number] };
  screen2GraphCoords(x: number, y: number): { x: number, y: number };
  graph2ScreenCoords(x: number, y: number): { x: number, y: number };
}

type FCwithRef<P = {}, R = {}> = React.FunctionComponent<P & { ref?: React.MutableRefObject<R | undefined> }>;

declare const ForceGraph: FCwithRef<ForceGraphProps, ForceGraphMethods>;

export { ForceGraph as ForceGraph2D, ForceGraph$1 as ForceGraph3D, ForceGraph$2 as ForceGraphAR, ForceGraph$3 as ForceGraphVR };
