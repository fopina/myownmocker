For some tests  (such as XCode UI Testing) we cannot use dependency injection nor mock classes. The easiest solution is to run the application using a mock server.

There are a few solutions already (such as http://mocky.io and http://mockable.io) but I wanted to make my own, MyOwnMocker.

This code is running live in https://mom.skmobi.com/ so whenever you need, just call MOM.

## Overview
[![Build Status](https://travis-ci.org/fopina/myownmocker.svg)](https://travis-ci.org/fopina/myownmocker)

1. [API](#api)
    1.  [Register](#register)
    2.  [Setup](#setup)
    3.  [Mock](#mock)
2. [Setting up your own copy of MOM](#setting-up-your-own-copy-of-mom)

## API

#### Register
Register for a mock token.

This is the first call you need to make to generate a mock API token to create mock API paths later

    GET /register/

###### Example Response

    < HTTP/1.1 200 OK
    < Content-Type: application/json

    {
      "token": "MeB3aNo4yDXrtNH6",
      "setup_url": "https://mom.skmobi.com/setup/MeB3aNo4yDXrtNH6/",
      "mock_base_url": "https://mom.skmobi.com/mock/MeB3aNo4yDXrtNH6/"
    }

### Setup
Setup a mock path.

This is the call to setup (create or replace) mock API paths

    POST /setup/:token/
    Content-Type: application/json

###### Parameters

| Name              | Type       | Description   |
| :---------------: |:----------:| :------------:|
| path              | string     | **Required**. The API method path (such as *login/* or *user/fopina/details/*) |
| status_code       | int        | **Required**. The HTTP response status code              |
| content_type      | string     | **Required**. The HTTP response content type             |
| custom_headers    | dictionary | Optional. Extra HTTP headers to include in the response  |
| body              | string     | Optional. The body of the response                       |

###### Example Input

    {
        "path": "login/",
        "status_code": 400,
        "content_type": "application/json",
        "custom_headers": { "X-My-API-Version": "1" },
        "body": "{\"code\": \"invalid_login\"}"
    }

###### Example Response

    < HTTP/1.1 200 OK
    < Content-Type: application/json

    {
        "message": "ok",
        "path_url": "https://mom.skmobi.com/mock/MeB3aNo4yDXrtNH6/login/"
    }

### Mock
Your mock API base URL.

This is your mock API "new" base URL. All the mock API paths you setup are available under `/mock/:token/` for both `GET`and `POST`methods.
Example (using token and path created in `register`and `setup`section examples):

    $ curl -v https://mom.skmobi.com/mock/MeB3aNo4yDXrtNH6/login/
    < HTTP/1.1 400 BAD REQUEST
    < Content-Type: application/json
    < Content-Length: 25
    <
    {"code": "invalid_login"}

## Setting up your own copy of MOM

Using [Heroku CLI](https://devcenter.heroku.com/articles/heroku-command), setting up your own copy is as easy as:

    $ git clone https://github.com/fopina/myownmocker
    Cloning into 'myownmocker'...
    remote: Counting objects: 35, done.
    remote: Compressing objects: 100% (28/28), done.
    remote: Total 35 (delta 5), reused 11 (delta 2), pack-reused 0
    Unpacking objects: 100% (35/35), done.
    Checking connectivity... done.

    $ cd myownmocker/
    $ heroku create
    Creating evening-scrubland-9609... done, stack is cedar-14
    https://evening-scrubland-9609.herokuapp.com/ | https://git.heroku.com/evening-scrubland-9609.git
    Git remote heroku added

    $ git push heroku
    Counting objects: 14, done.
    Delta compression using up to 4 threads.
    Compressing objects: 100% (11/11), done.
    Writing objects: 100% (14/14), 4.81 KiB | 0 bytes/s, done.
    Total 14 (delta 2), reused 0 (delta 0)
    remote: Compressing source files... done.
    remote: Building source:
    remote:
    (...)
    remote: -----> Launching... done, v4
    remote:        https://evening-scrubland-9609.herokuapp.com/ deployed to Heroku
    remote:
    remote: Verifying deploy... done.
    To https://git.heroku.com/evening-scrubland-9609.git
     * [new branch]      master -> master

    $ heroku run ./manage.py initdb
    Running ./manage.py initdb on evening-scrubland-9609... up, run.7551
    Using database postgres://frsnvzfkdflxFc:ZfT4aMeprPYiQC@ec2-107-21-219-235.compute-1.amazonaws.com:5432/dk3m44gfjo30g
    Created tables

And it's live!