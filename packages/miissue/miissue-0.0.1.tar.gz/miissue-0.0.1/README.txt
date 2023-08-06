miissue

migrating git issues between repositories of github and gitbucket

 - Provide the source and destination git url.
 - Provide the source and destination git token.
 - Provide the repository name.
 - Provide the desired issues closed or open issues. by default it grabs the closed issues.


Command line examples:

### Migrating the open issues
```
miissue -p "surl http://source-host/api/v3" -p "durl http://dest-host/api/v3" -p "stoken xxxx" -p "dtoken xxxx" -p "srepo name1/repo1" -p "drepo name2/repo1" -p "stat open”
```

### Migrating the closed issues
```
miissue -p "surl http://source-host/api/v3" -p "durl http://dest-host/api/v3" -p "stoken xxxx" -p "dtoken xxxx" -p "srepo name1/repo1" -p "drepo name2/repo1"
```
