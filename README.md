# preqin-assignment


## Problem Statement

Use a web framework of your choice (Flask, Django, FastAPI, etc) to develop a single production-quality API endpoint that takes a sentence as input and returns a random 500 dimensional array of floats. For example:

*Input*: “This is an example sentence”

*Output*: [1.32, 0.393, .... 0.9312]

## Solution:

For developing the api endpoint, I have selected the web framework **_FastAPI_**. Mainly because:

- It's fast
- Have builtin support to handle asynchronous requests
- In-built data validation feature and support for automatic documentation

To run the web app:
- I have provided a dockerfile, using which you can create a docker image and run the web app in docker container
- To create the image run `docker build -f Dockerfile -t webapp .`
- To run the web server run `docker run -p 80:8000 -e SECRET_KEY=$SECRET_KEY -e ALGORITHM=$ALGORITHM --name containerName -it webapp`
- To run the server successfully, it requires two environment variable, `SECRET_KEY` and `ALGORITHM`.
- `SECRET_KEY` is your ssl key, which you can generate by running `openssl rand -hex 32`
- `ALGORITHM` you can choose something like `HS256`


In the webserver, I have implemented some basic security, a user needs to be authenticated before he/she can make a successful request. Only those users which are in database (`db.json`) can be authenticated. To authenticate:
- first get your token by running
    ```bash
    curl -X 'POST' \
    'http://127.0.0.1:8000/token' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username=monte&password=secret&scope=&client_id=&client_secret='
    ```
- The above endpoint will return a token, which you can copy and use in subsequent requests, as follows
    ```bash
    token=$(curl -X 'POST' \
    'http://127.0.0.1:8000/token' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'grant_type=&username=monte&password=secret&scope=&client_id=&client_secret=' -s | jq .access_token --raw-output);

    curl -X 'GET' \
    'http://127.0.0.1:8000/array?sentence=some random sentence&n=5' \
    -H 'accept: application/json' \
    -H "Authorization: Bearer ${token}"
    ```
- In the question, it was asked to return an array of length 500. But you can have an array of any length, just need to update the value of `n`. The default value of `n` is `500`. The above endpoint (`/array`), returns a response like following (this is for `n=5`).
    ```bash 
    {
      "user": {
        "username": "monte",
        "display_name": "Mohit Sharma",
        "emailid": "mohitsharma@gmail.com"
      },
      "array": [
        4.88,
        2.14,
        4.31,
        1.1,
        1.72
      ]
    }
    ```
