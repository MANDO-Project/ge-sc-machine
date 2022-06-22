# MANDO-GURU services
<p>
    <a href="https://www.python.org/" target="blank_"><img alt="python" src="https://img.shields.io/badge/python-3.8.9-green" /></a>
    <a href="https://fastapi.tiangolo.com/" target="blank_"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.78.0-yellowgreen" /></a>
    <a href="https://reactjs.org/" target="blank_"><img alt="bigquery" src="https://img.shields.io/badge/ReactJs-18.2.0-red" /></a>
    <a href="https://opensource.org/licenses/MIT" target="blank_"><img alt="mit" src="https://img.shields.io/badge/License-MIT-blue.svg" /></a>
</p>
<br/>

# Overview
![GE-SC overview](./assets/Overview.png)

This project was created to bring out the APIs of vulnerability detection for smart contracts.

## The MANDO-GURU tool with three main components: Backend, RESTful APIs, and Frontend.
- Backend plays a vital role with several core sub-components such as heterogeneous presentation for the generated graphs from input smart contract files, heterogeneous graph fusion, custom multi-metapaths extraction, heterogeneous graph neural network, and vulnerability detections in coarse-grained and fine-grained levels.
- Frontend component services are used to visualize the prediction results and the statistics of the analyzed smart contracts.
- RESTful APIs are implemented as a bridge to communicate between the Backend and the Frontend.

# Table of contents
- [MANDO-GURU services](#mando-guru-services)
- [Overview](#overview)
  - [The MANDO-GURU tool with three main components: Backend, RESTful APIs, and Frontend.](#the-mando-guru-tool-with-three-main-components-backend-restful-apis-and-frontend)
- [Table of contents](#table-of-contents)
- [How to use the tool?](#how-to-use-the-tool)
  - [Coaser-Grained Detection](#coaser-grained-detection)
  - [Fine-Grained Detection](#fine-grained-detection)
  - [Statistics](#statistics)
  - [Demo Video](#demo-video)
- [Deployment](#deployment)
  - [Prerequisites](#prerequisites)
  - [Backend](#backend)
  - [Frontend](#frontend)

# How to use the tool?
## Coaser-Grained Detection
![GE-SC overview](./assets/onClickDetail.png)
- You can upload a solidity smart contract from local or select an available one in the drop-down box.
- We supported 7 kind of bugs. Due to limits of computation resources, the scanning process might take 1-2 minutes to get the results, depending on the complexity of the input source file. We recommend users use the Chrome browser for the best experience.
- When the process finished:
    - Red Button: Smart contract contains this type of bug.
    - Green Button: Smart contract does not contain this type of bug.

## Fine-Grained Detection
![GE-SC overview](./assets/mando-detection-screenshot.png)
- When you click a button which was result of Coaser-Grained phase, the tool would show the source code and graph of the smart contract
- Source Code
    - Buggy Code Line : The line of code has the background color of yellow.
- Graph 
    - Red Node: Bug Node.
    - White Node : Clean Node.
    - Border of Node : Node Type.
- If you click a node in the graph, the lines of code equivalent to that node will be bounded by a red border.

## Statistics
- Bar Chart
![GE-SC overview](./assets/BarChart.png)
  - Number of bug nodes and Number of clean nodes for each type of bug.
- Detection Time
![GE-SC overview](./assets/DetectionTime.png)
  - DetectionTime for each type of bug.
- Bug Density
![GE-SC overview](./assets/BugDensity.png)
  - We divided the line number which had bugs into 15 categories in order.
  - The portion with darker color shows that the areas of source code have more bug lines.
## Demo Video
Please visit this link to see the [demo video](http://mandoguru.com/demo-video).

# Deployment
- If you want to launch our tool yourselves, please meet the prerequisites prior to follow the steps bellow:

## Prerequisites
- [docker](https://docs.docker.com/engine/install/)
- [node](https://nodejs.org/en/download/) 16.15.1 or higher
- [npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) 8.11.0 or higher


## Backend
- We published docker image for launching backend service.

- Pull docker image from docker hub.
```
docker pull nguyenminh1807/sco:latest
```

- Run container and map port 5555:xxxx to any port you want to public (we used the same port over here).
```
docker run -it -d --rm  --name sco_app -p 5555:5555 nguyenminh1807/sco:latest
```

## Frontend
- You need to navigate to frontend directory first.
```
cd sco_frontend
```

- Install required package.
```
npm install
```

- Launch app from local.
```
npm start
```
