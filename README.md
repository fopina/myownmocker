# MyOwnMocker
Online mock server

## API

#### /register/

This is the first call you need to make to generate a mock API token to create mock API paths later

    $ curl https://mom.skmobi.com/register/
    
**Example Response**

    < HTTP/1.1 200 OK
    < Content-Type: application/json
    
    {
      "token": "MeB3aNo4yDXrtNH6"
    }

### /setup/

This is the 

## Setting up your own copy of MOM

Using heroku cli, settings your own copy is as easy as:

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
    skmac:myownmocker fopina$ git push heroku
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
    Using database postgres://frsnvzfkdflfdf:azT4aMeprPYiQjyA_KA2whCreQ@ec2-107-21-219-235.compute-1.amazonaws.com:5432/dk3m44gfjo50g
    Created tables

And it's live!
