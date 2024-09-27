# Steps:

1. git fetch and git pull -- ensure code is up-to-date

2. Run:

```bash
./build.sh
```

```bash
curl --json '{"name": "hello"}' http://localhost:8080/api/v1/breeders/
{"name":"hello","id":1}
```

```bash
curl http://localhost:8080/api/v1/breeders/
```

3. go to frontend repository

Run:

```bash
./build.sh
```

Go to `http://localhost:3000/`

