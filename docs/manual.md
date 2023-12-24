# Distributed Database Systems - Project Manual

## Authors

Armando Fortes [2021403383](mailto:ferreiracardos10@mails.tsinghua.edu.cn), David Pissarra [2021403381](mailto:pissarrad10@mails.tsinghua.edu.cn)


## MongoDB Sharded Cluster Setup

To begin with the setup of our MongoDB Cluster, we should run our two config servers on docker containers, by running the following command on the mongodb directory:

```
cd mongodb
docker-compose -f configsvrs/docker-compose.yml up -d
```

In order to initiate the config server replica set we should log into one of the config servers (will be selected as the primary config server):

```
mongo mongodb://localhost:40001
```

Then, initiate the replica set by running this mongodb command and exit afterwards:

```
rs.initiate(
  {
    _id: "cfgrs",
    configsvr: true,
    members: [
      { _id : 0, host : "<PRIVATE IP>:40001" },
      { _id : 1, host : "<PRIVATE IP>:40002" }
    ]
  }
)

exit
```

Config server are done at this moment. Now, we should start running the shards:

```
docker-compose -f shards/docker-compose.yml up -d
```

After checking if every docker container is running, we should initiate every shard replica set. Since we have three replica sets, we have to do it three times, for every replica set primary shard:

```
mongo mongodb://localhost:50001

rs.initiate(
  {
    _id : "shard0",
    members: [
      { _id : 0, host : "<PRIVATE IP>:50001" }
    ]
  }
)

exit
```

```
mongo mongodb://localhost:50002

rs.initiate(
  {
    _id : "shardrep",
    members: [
      { _id : 0, host : "<PRIVATE IP>:50002" },
      { _id : 1, host : "<PRIVATE IP>:50003" }
    ]
  }
)

exit
```

```
mongo mongodb://localhost:50004

rs.initiate(
  {
    _id : "shard1",
    members: [
      { _id : 1, host : "<PRIVATE IP>:50004" }
    ]
  }
)

exit
```

Finally, we should run our last MongoDB component, the router (mongos):

```
docker-compose -f router/docker-compose.yml up -d
```

Since we want to configure the router, we must enter in mongos:

```
mongo mongodb://localhost:60000
```

Inside mongos, we should run several commands as follows.

Add every shard replica set to the router:

```
sh.addShard("shard0/<PRIVATE IP>:50001")

sh.addShard("shardrep/<PRIVATE IP>:50002, <PRIVATE IP>:50003")

sh.addShard("shard1/<PRIVATE IP>:50004")
```

Name every shard replica set with MongoDB tags, so we can distinguish each other. Note: DBMS12 will be the replica set which will be present in both DBMS1 and DBMS2.

```
sh.addShardTag("shard0", "DBMS1")

sh.addShardTag("shard1", "DBMS2")

sh.addShardTag("shardrep", "DBMS12")
```

Create a new sharded database called demo:

```
use demo
sh.enableSharding("demo")
```

Create the User collection, and then define the ranges so we can allocate partitions of data, according project requirements (Beijing -> DBMS1, Hong Kong -> DBMS2):

```
sh.shardCollection("demo.user_beijing", {"uid": 1})
sh.addTagRange( 
  "demo.user_beijing",
  { "uid" : MinKey },
  { "uid" : MaxKey },
  "DBMS1"
)

sh.shardCollection("demo.user_hong_kong", {"uid": 1})
sh.addTagRange(
  "demo.user_hong_kong",
  { "uid" : MinKey },
  { "uid" : MaxKey },
  "DBMS2"
)
```

Setup the Article collection (Science -> DBMS12, Technology -> DBMS2):

```
sh.shardCollection("demo.article_science", {"aid": 1})
sh.addTagRange( 
  "demo.article_science",
  { "aid" : MinKey },
  { "aid" : MaxKey },
  "DBMS12"
)

sh.shardCollection("demo.article_tech", {"aid": 1})
sh.addTagRange(
  "demo.article_tech",
  { "aid" : MinKey },
  { "aid" : MaxKey },
  "DBMS2"
)
```

Setup the Read collection (Beijing -> DBMS1, Hong Kong -> DBMS2):

```
sh.shardCollection("demo.read_beijing", {"id": 1})
sh.addTagRange( 
  "demo.read_beijing",
  { "id" : MinKey },
  { "id" : MaxKey },
  "DBMS1"
)

sh.shardCollection("demo.read_hong_kong", {"id": 1})
sh.addTagRange(
  "demo.read_hong_kong",
  { "id" : MinKey },
  { "id" : MaxKey },
  "DBMS2"
)
```

Setup the Be-Read collection (Science -> DBMS12, Technology -> DBMS2):

```
sh.shardCollection("demo.be_read_science", {"brid": 1})
sh.addTagRange(
  "demo.be_read_science",
  { "brid" : MinKey },
  { "brid" : MaxKey },
  "DBMS12"
)

sh.shardCollection("demo.be_read_tech", {"brid": 1})
sh.addTagRange(
  "demo.be_read_tech",
  { "brid" : MinKey },
  { "brid" : MaxKey },
  "DBMS2"
)
```

Setup the Popular-Rank collection (Daily -> DBMS1, Weekly -> DBMS2, Monthly -> DBMS2):

```
sh.shardCollection("demo.popular_rank_daily", {"prid": 1})
sh.addTagRange(
  "demo.popular_rank_daily",
  { "prid" : MinKey },
  { "prid" : MaxKey },
  "DBMS1"
)

sh.shardCollection("demo.popular_rank_weekly", {"prid": 1})
sh.addTagRange(
  "demo.popular_rank_weekly",
  { "prid" : MinKey },
  { "prid" : MaxKey },
  "DBMS2"
)

sh.shardCollection("demo.popular_rank_monthly", {"prid": 1})
sh.addTagRange(
  "demo.popular_rank_monthly",
  { "prid" : MinKey },
  { "prid" : MaxKey },
  "DBMS2"
)
```

Lastly, in order to populate all collections, we run the following python script:

```
python3 config.py
```

The setup process for the MongoDB Sharded Cluster is now finished and one may return to the main directory:

```
cd ..
```


## Redis Setup

For this setup, we should firstly navigate to the *redis/* directory:

```
cd redis/
```

We should then run our redis server on a docker container, by executing the following command:

```
docker-compose -f docker-compose.yml up -d
```

We may set some configurations for our cache, so the following command allows accessing to the redis interface:

```
redis-cli -h <PRIVATE IP> -p 6379
```

To optimize the cache usage we can set a 100 megabyte limit, as follows:

```
CONFIG SET maxmemory 100mb
```

To set the LRU (Least Recently Used) replacement policy, we run:

```
CONFIG SET maxmemory-policy allkeys-lru
```

The setup process for the Redis cache is now finished and one may return to the main directory:

```
exit
cd ..
```


## Hadoop Distributed File System Setup

For this setup, we should firstly navigate to the *hadoop/* directory:

```
cd hadoop/
```

We have to make sure the article contents are inside the build context. Therefore, if the articles are not inside the *hadoop/* directory, the following commands should be ran in order to copy them from the corresponding directory they are in:

```
mkdir articles
cp -r <ARTICLES DIR>* ./articles/
```

Then, we are ready to build our docker image regarding the hadoop, which will rely on the *Dockerfile* present in the current directory. This *Dockerfile* has instructions to install hadoop and java 8, configurate the corresponding environment variables, and copy the necessary hadoop configuration files, scripts and the articles from our local machine to the respective container:

```
docker build -t hadoop:3.2.1
```

After the docker image has been built, we may create a docker network for the hadoop containers:

```
docker network create --driver=bridge hadoop
```

Start the hadoop-master container:

```
sudo docker run -itd \
           --net=hadoop \
           -p 9870:9870 \
           -p 8088:8088 \
           --name hadoop-master \
           --hostname hadoop-master \
           hadoop:3.2.1 > /dev/null
```

Start the hadoop-slave containers:

```
N=${1:-3}
i=1
while [ $i -lt $N ]
do
    sudo docker rm -f hadoop-slave$i > /dev/null
    echo "start hadoop-slave$i container..."
    sudo docker run -itd \
               --net=hadoop \
               --name hadoop-slave$i \
               --hostname hadoop-slave$i \
               hadoop:3.2.1 > /dev/null
    i=$(( $i + 1 ))
done
```

All 3 hadoop related containers are now running. We may go inside the hadoop-master container for the following setup instructions. For this, run the following command:

```
docker exec -it hadoop-master bash
```

Now that we are inside the hadoop-master, we may run the following script for starting the all the HDFS servers:

```
start-all.sh
```

Furthermore, we may now upload the articles to the DFS. We start by creating a new directory as follows:

```
hdfs dfs -mkdir -p articles
```

Finally, we may copy the locally stored articles to the newly created directory in HDFS:

```
hdfs dfs -put ./articles/* articles
```

The setup process for the Hadoop Distributed File System is now finished and one may exit the hadoop-master container and return to the main directory:

```
exit
cd ..
```

## Current Docker Status

Now that every component is up, we can check which containers are currently running:

<img src=figs/docker.png width="1000">

## Run the python application

For this step, we should firstly navigate to the *app/* directory:

```
cd app/
```

In order to run the python application we may run the following command:

```
python3 app_tk.py
```

Now that the application is up and running, we should be presented with the next menu:

<img src=figs/apphome.png width="550">

Here, we are able to read, insert, edit and delete users at will. Moreover, similar functionalities are also possible for the rest of the structured tables. Finally, one may also access the contents of a given article directly from the application interface. Follows some examples of the implemented features:

- Analyzing the articles read by user 1:

  <img src=figs/appreads.png width="550">

- Querying the top-5 articles in a day (01/01/2018):

  <img src=figs/appdailyrank.png width="550">

- Reading the contents of article 6965:

  <img src=figs/apparticle.png width="550">

And many more features may be explored...

## Monitoring MongoDB

We can monitor each DBMS (including the router) by using MongoDB Compass:

<img src=figs/compass.png width="200">

By checking the router, we can see every sharded collection in our cluster:

<img src=figs/collections.png width="625">

For each collection, we can check the existent documents:

<img src=figs/documents.png width="625">

Also, we can check which collection there will be in a specific DBMS, for instance DBMS2:

<img src=figs/distribution.png width="1000">


## Monitoring HDFS

In order to monitor the HDFS nodes, we may access the next *url* through a web browser:

```
http://<PRIVATE IP>:9870/
```

Which should redirect us to the following monitoring page:

<img src=figs/hdfshome.png width="600">

From here we are able to analyze the live datanodes, as well as the distribution of the blocks between them:

<img src=figs/hdfsdata.png width="1000">

Moreover, we may also browse the articles present in the distributed file system:

<img src=figs/hdfsarticles.png width="1000">
<br />
<br />
<br />
<br />
And read their contents:
<br />
<img src=figs/hdfsexample.png width="1000">

## Shut down

We can shut every container down and delete its volumes, by running the following commands:

```
docker stop $(docker container ls -q)
docker rm -f $(docker ps -a -q)
docker volume rm $(docker volume ls -q)
```
