## How to deploy your solution

Create a MySQL RDS instance in your AWS account then connect to that RDS instance and then create the database with these commands:

```
CREATE DATABASE Error_Logs

USE Error_Logs

CREATE TABLE `Logs` (
`error_log_id` INT NOT NULL AUTO_INCREMENT,
`device_id` varchar(255) NOT NULL,
`error_number` INT NOT NULL,
`time_stamp` INT NOT NULL,
PRIMARY KEY (`error_log_id`)
);
```

There are 2 GitHub repositories: 1 for the GET API and 1 for the POST API. Clone both into your machine.

https://github.com/JoshuaManto/Canoo-TakeHome-GetAPI

https://github.com/JoshuaManto/Canoo-TakeHome-PostAPI

Node, Python, Serverless, Virtualenv, and Docker are needed for both APIs so you’d need to install them if you don’t already have them in your machine.

```
npm install -g serverless

pip3 install virtualenv
```

Then create a virtual environment to handle Python packages

```
virtualenv venv --python=python3

source venv/bin/activate
```

Install MySQL for Python

```
pip3 install pymysql
```

requirements.txt already contains pymysql so there’s no need to run pip freeze

Setup a new npm package and go through creating the package.json file and install serverless-python-requirements plugin to be able to save node dependencies

```
npm init

npm install --save serverless-python-requirements
```

There will be a secrets.json file attached with the email. It holds the data to be used as environment variables for the APIs. Copy this file into the root directory of each API then change the data depending on the database you created.

Make sure to run Docker before the next step to package Python packages along with Serverless

Deploy the api by running

```
serverless deploy or sls deploy
```

It should start packaging and uploading it to your aws account. The API key will be one of the output artifacts of the build process. Use this key to test the API Gateway route.

## How you would scale your solution to hundreds of error codes per second. Thousands? Millions?

#### Lambda concurrent soft limit can be increase

AWS Lambda concurrency limit by default is 1000 if I got it right and it can be increased by making a request directly to AWS. The max limit is different depending on the region.

#### Lambda Throttling

#### SQS

This is a possible side effect of burst calls for Lambda functions and one way to go about avoiding or fixing this problem is to use a service like SQS to hold possible retries on invoking the Lambda function with the same data. A dead letter queue is also a good mechanism to use alongside SQS to possibly accommodate for failure so the data won’t be completely lost. Setting alarms on throttling exceptions is also good practice to be aware that it is happening.

#### Lambda cold start issue

Amazon CloudWatch Events can be used to keep lambdas warm by triggering them periodically. There are already solutions out there like in Serverless, there’s plugins like serverless-plugin-warmup or the Lambda Warmer npm package that keep your lambdas.

#### Multi AZ database

For the database, having duplicate or backup copies is always good practice for redundancy if the main database goes down for some reason and the good thing about this is RDS already has an automatic mechanism to switch to the backup when this happens.

#### NoSQL Database

Refactor to using DynamoDB NoSQL database because RDS SQL Databases have builtin overhead that maintains relationships and since the data doesn’t have any relationships so this feature makes it redundant for SQL databases.
How the tables are designed is important in how the data is stored so choosing the right Hash and Sort keys will affect how they’re saved in the partitions.

DynamoDB Accelerator (DAX) is great for read-heavy workloads while maintaining an ElasiCache datastore is good for write-heavy workloads.

## Any other considerations we should be aware of

I’d like to thank Clark for being so awesome throughout the weekend with scheduling calls and answering my questions!

#### Why SQL?

#### Nosql and dynamodb

#### Filter expression problem

#### Local and global index

#### Caching / separate database for top 10

Initially, when I saw the data to be stored and used, I thought a NoSQL database like DynamoDB should be the right choice since the there’s only a single table so there’s no relationships, but when I was trying to formulate the table’s primary key (both the hash key and sort key if needed) and how to get the 10 most recent logs, that’s when I started having problems. I know filter expression is kind of like the WHERE clause in SQL so I delved deeper into that, but a problem with using filter is how it works because it gets the data (with a 1mb limit) before it applies the filter expression. Then I thought and researched about the sort key, but in order to use it properly, the hash key needs to be used unless an index (local or global) is applied on the table, but I wasn’t sure if that would completely solve the problem and I knew there’s a limited amount of time so I switched my approach to SQL since I knew how to query it.

There’s also an approach that I could’ve implemented, but realized it pretty late on how to completely integrate it with the system. I could’ve used a separate database or a cache that holds the 10 most recent logs and whenever something is added then the 10 most recent would be updated.

#### API keys and Authorizers

The solution I implemented for the API keys is to separate the GET and POST into their own APIs so they would have their own API Gateways in order to leverage the builtin API key creation and authentication mechanism in API Gateway and Serverless.

Another way that I thought of was to create custom authorizers and to enforce those for each route in a single API, but possible problems are its harder to maintain, it adds a whole new mechanism where there’s already services builtin that handles the problem, and I think it’ll be a lambda function so there would be additional cost.

#### API keys and environment variable storage

I ended up using the simplest way which is to store the data in a json file and then imported that information into Serverless’s yaml file configuration file to store the environmental variables and push it up with the Lambda functions.

There are a couple of different ways I could’ve stored the environmental variables. One is to use Serverless website dashboard parameters feature to store them. Another is to store it in AWS using Parameter Store. One other approach is to use AWS Secrets manager to store API keys and secrets/environment variables.

#### IAM roles and policies and security

I didn’t get to implement this, but Clark still suggested I put it down here.

I wanted to use IAM roles and policies that coincides with the principle of least privilege to limit the lambda functions from accessing any other resource or service that it shouldn’t be allowed to interact with.

A policy I was thinking is to limit the lambda function to only be able to interact with that specific RDS MySQL instance using its ARN if that’s possible.

I also found this policy “AWSLambdaVPCAccessExecutionRole” that could be fairly useful since RDS policies are limited unlike DynamoDB policies where you could create custom ones with specific actions.

"Effect": "Allow",

"Action": [

"logs:CreateLogGroup",

"logs:CreateLogStream",

"logs:PutLogEvents",

"ec2:CreateNetworkInterface",

"ec2:DescribeNetworkInterfaces",

"ec2:DeleteNetworkInterface"

],

"Resource": "\*"

#### Model and Mapping templates

This actually isn’t all that necessary since the data being used is so small in terms of the number of attributes, but I think it would still be a good thing to have, moreso for bigger applications.
