# kosakkun/Endless-Marathon

## How to Execute

``` console
$ git submodule update -i
$ docker build . -f Dockerfile.judge -t ubuntu-judge
$ docker-compose up
```

Above commands start the servers with URL <http://localhost:8000>.
