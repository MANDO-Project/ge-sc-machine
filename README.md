# MANDO-GURU backend services

## This project was created to bring out the APIs of vulnerability detection for smart contracts.

## Deploy MANDO-GURU services in a local machine

### Backend


```
docker pull nguyenminh1807/sco:latest
```

```
docker run -it -d --rm  --name sco_app -p 5555:5555 nguyenminh1807/sco:latest
```

### Frontend

```
cd sco_frontend
```

```
yarn
```

```
yarn build
```
