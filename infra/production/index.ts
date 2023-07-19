import * as pulumi from "@pulumi/pulumi";
import * as aws from "@pulumi/aws";
import * as awsx from "@pulumi/awsx";

// The following vars ar not alloed to be undefined, hence the `${...}` magic
let dbUsername = `${process.env["DB_USER"]}`;
let dbPassword = pulumi.secret(`${process.env["DB_PASSWORD"]}`);
let dbName = `${process.env["DB_NAME"]}`;

let githubApiUser = `${process.env["GITHUB_API_USER"]}`;
let githubApiToken = pulumi.secret(`${process.env["GITHUB_API_TOKEN"]}`);
let githubClientId = `${process.env["GITHUB_CLIENT_ID"]}`;
let githubClientSecret = pulumi.secret(`${process.env["GITHUB_CLIENT_SECRET"]}`);
let githubAppName = `${process.env["GITHUB_APP_NAME"]}`;
let tempDatabase = `${process.env["TEMP_DATABASE"]}`

let route53Zone = `${process.env["ROUTE_53_ZONE"]}`;
let domain = `${process.env["DOMAIN"]}`;
let baseUrl = `http://${domain}/`;

let sentryDSN = `${process.env["SENTRY_DSN"]}`;

let databaseURL = `${process.env["DATABASE_URL"]}`
let readReplica1 = `${process.env["READ_REPLICA_1_DATABASE_URL"]}`
let readReplica2 = `${process.env["READ_REPLICA_2_DATABASE_URL"]}`
let readReplica3 = `${process.env["READ_REPLICA_3_DATABASE_URL"]}`
let readReplica4 = `${process.env["READ_REPLICA_4_DATABASE_URL"]}`
let oldProdRedisURL = `${process.env["OLD_REDIS_URL"]}`
let starGitcoinCertificate = `${process.env["AWS_STAR_GITCOIN_CERT"]}`

let secretKey = `${process.env["SECRET_KEY"]}`
let sendgridApiKey = `${process.env["SENDGRID_API_KEY"]}`
let etherscanApiKey = `${process.env["ETHERSCAN_API_KEY"]}`
let gtcDistApiUrl = `${process.env["GTC_DIST_API_URL"]}`
let gtcDistKey = `${process.env["GTC_DIST_KEY"]}`
let brightIdPrivateKey = `${process.env["BRIGHTID_PRIVATE_KEY"]}`
let alchemyKey = `${process.env["ALCHEMY_KEY"]}`

export const dockerGtcWebImage = `${process.env["DOCKER_GTC_WEB_IMAGE"]}`;


//////////////////////////////////////////////////////////////
// Create permissions:
//  - user for logging
//////////////////////////////////////////////////////////////

const usrLogger = new aws.iam.User("usrLogger", {
    path: "/review/",
});

const usrLoggerAccessKey = new aws.iam.AccessKey("usrLoggerAccessKey", { user: usrLogger.name });

export const usrLoggerKey = usrLoggerAccessKey.id;
export const usrLoggerSecret = usrLoggerAccessKey.secret;


// See https://pypi.org/project/watchtower/ for the polciy required
const test_attach = new aws.iam.PolicyAttachment("CloudWatchPolicyAttach", {
    users: [usrLogger.name],
    roles: [],
    groups: [],
    policyArn: "arn:aws:iam::aws:policy/AWSOpsWorksCloudWatchLogs",
});


//////////////////////////////////////////////////////////////
// Create bucket for static hosting
// Check policy recomendation here: https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html#iam-policy
//////////////////////////////////////////////////////////////

const staticAssetsBucket = new aws.s3.Bucket("bucket", {
    acl: "public-read",
    website: {
        indexDocument: "index.html",
    },
    bucket: "bucket-0427bb4",
    forceDestroy: true,
});

const staticAssetsBucketPolicyDocument = aws.iam.getPolicyDocumentOutput({
    statements: [{
        principals: [{
            type: "AWS",
            identifiers: [pulumi.interpolate`${usrLogger.arn}`],
        }],
        actions: [
            "s3:PutObject",
            "s3:GetObjectAcl",
            "s3:GetObject",
            "s3:ListBucket",
            "s3:DeleteObject",
            "s3:PutObjectAcl"
        ],
        resources: [
            staticAssetsBucket.arn,
            pulumi.interpolate`${staticAssetsBucket.arn}/*`,
        ],
    },  {
        principals: [{
            type: "AWS",
            identifiers: ["*"],
        }],
        actions: [
            "s3:GetObject",
        ],
        resources: [
            pulumi.interpolate`${staticAssetsBucket.arn}/*`
        ]
    }],
});

const staticAssetsBucketPolicy = new aws.s3.BucketPolicy("staticAssetsBucketPolicy", {
    bucket: staticAssetsBucket.id,
    policy: staticAssetsBucketPolicyDocument.apply(staticAssetsBucketPolicyDocument => staticAssetsBucketPolicyDocument.json),
});

// const s3OriginId = "myS3Origin";
// const s3Distribution = new aws.cloudfront.Distribution("s3Distribution", {
//     origins: [{
//         domainName: staticAssetsBucket.bucketRegionalDomainName,
//         originId: s3OriginId,
//     }],
//     enabled: true,
//     isIpv6Enabled: true,
//     defaultRootObject: "index.html",
//     aliases: [
//         "c.gitcoin.co",
//         "s.gitcoin.co"
//     ],
//     defaultCacheBehavior: {
//         allowedMethods: [
//             "DELETE",
//             "GET",
//             "HEAD",
//             "OPTIONS",
//             "PATCH",
//             "POST",
//             "PUT",
//         ],
//         cachedMethods: [
//             "GET",
//             "HEAD",
//         ],
//         targetOriginId: s3OriginId,
//         forwardedValues: {
//             queryString: false,
//             cookies: {
//                 forward: "none",
//             },
//         },
//         viewerProtocolPolicy: "allow-all",
//         minTtl: 0,
//         defaultTtl: 3600,
//         maxTtl: 86400,
//     },
//     orderedCacheBehaviors: [
//         {
//             pathPattern: "/static/*",
//             allowedMethods: [
//                 "GET",
//                 "HEAD",
//                 "OPTIONS",
//             ],
//             cachedMethods: [
//                 "GET",
//                 "HEAD",
//                 "OPTIONS",
//             ],
//             targetOriginId: s3OriginId,
//             forwardedValues: {
//                 queryString: false,
//                 headers: ["Origin"],
//                 cookies: {
//                     forward: "none",
//                 },
//             },
//             minTtl: 0,
//             defaultTtl: 86400,
//             maxTtl: 31536000,
//             compress: true,
//             viewerProtocolPolicy: "redirect-to-https",
//         },
//     ],
//     priceClass: "PriceClass_200",
//     restrictions: {
//         geoRestriction: {
//             restrictionType: "none",
//         },
//     },
//     tags: {
//         Environment: "staging",
//     },
//     viewerCertificate: {
//         acmCertificateArn: starGitcoinCertificate,
//         cloudfrontDefaultCertificate: true,
//         sslSupportMethod: "sni-only",
//     },
// });

export const bucketName = staticAssetsBucket.id;
export const bucketArn = staticAssetsBucket.arn;
export const bucketWebURL = pulumi.interpolate`http://${staticAssetsBucket.websiteEndpoint}/`;

//////////////////////////////////////////////////////////////
// Set up VPC
//////////////////////////////////////////////////////////////

const vpc = new awsx.ec2.Vpc("gitcoin", {
    subnets: [
        { type: "public", },
        { type: "private", mapPublicIpOnLaunch: true },
    ],
});

export const vpcID = vpc.id;
export const vpcPrivateSubnetIds = vpc.privateSubnetIds;
export const vpcPublicSubnetIds = vpc.publicSubnetIds;


export const vpcPublicSubnet1 = vpcPublicSubnetIds.then((subnets) => {
    return subnets[0];
});


//////////////////////////////////////////////////////////////
// Set up RDS instance
//////////////////////////////////////////////////////////////
// let dbSubnetGroup = new aws.rds.SubnetGroup("rds-subnet-group", {
//     subnetIds: vpcPrivateSubnetIds
// });

// const db_secgrp = new aws.ec2.SecurityGroup("db_secgrp", {
//     description: "Security Group for DB",
//     vpcId: vpc.id,
//     ingress: [
//         { protocol: "tcp", fromPort: 5432, toPort: 5432, cidrBlocks: ["0.0.0.0/0"] },
//     ],
//     egress: [{
//         protocol: "-1",
//         fromPort: 0,
//         toPort: 0,
//         cidrBlocks: ["0.0.0.0/0"],
//     }],
// });

// // TODO: enable delete protection for the DB
// const postgresql = new aws.rds.Instance("gitcoin-database", {
//     allocatedStorage: 200,
//     engine: "postgres",
//     // engineVersion: "5.7",
//     instanceClass: "db.t3.medium",
//     name: dbName,
//     password: dbPassword,
//     username: dbUsername,
//     skipFinalSnapshot: true,
//     dbSubnetGroupName: dbSubnetGroup.id,
//     vpcSecurityGroupIds: [db_secgrp.id],
// });

// export const rdsEndpoint = postgresql.endpoint;
// export const rdsArn = postgresql.arn;
// export const rdsConnectionUrl = pulumi.interpolate`psql://${dbUsername}:${dbPassword}@${rdsEndpoint}/${dbName}`
// export const rdsId = postgresql.id

//////////////////////////////////////////////////////////////
// Set up Redis
//////////////////////////////////////////////////////////////

const redisSubnetGroup = new aws.elasticache.SubnetGroup("gitcoin-cache-subnet-group", {
    subnetIds: vpcPrivateSubnetIds
});

const secgrp_redis = new aws.ec2.SecurityGroup("secgrp_redis", {
    description: "gitcoin",
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 6379, toPort: 6379, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
});

const redis = new aws.elasticache.Cluster("gitcoin-cache", {
    engine: "redis",
    engineVersion: "4.0.10",
    nodeType: "cache.m5.large",
    numCacheNodes: 1,
    port: 6379,
    subnetGroupName: redisSubnetGroup.name,
    securityGroupIds: [secgrp_redis.id]
});


export const redisPrimaryNode = redis.cacheNodes[0];
export const redisConnectionUrl = pulumi.interpolate`rediscache://${redisPrimaryNode.address}:${redisPrimaryNode.port}/0?client_class=django_redis.client.DefaultClient`
export const redisCacheOpsConnectionUrl = pulumi.interpolate`redis://${redisPrimaryNode.address}:${redisPrimaryNode.port}/0`

//////////////////////////////////////////////////////////////
// Set up ALB and ECS cluster
//////////////////////////////////////////////////////////////

const cluster = new awsx.ecs.Cluster("gitcoin", { vpc });
// export const clusterInstance = cluster;
export const clusterId = cluster.id;

// Generate an SSL certificate
const certificate = new aws.acm.Certificate("cert", {
    domainName: domain,
    tags: {
      Environment: "production",
    },
    validationMethod: "DNS",
  });

const certificateValidationDomain = new aws.route53.Record(`${domain}-validation`, {
    name: certificate.domainValidationOptions[0].resourceRecordName,
    zoneId: route53Zone,
    type: certificate.domainValidationOptions[0].resourceRecordType,
    records: [certificate.domainValidationOptions[0].resourceRecordValue],
    ttl: 600,
});

const certificateValidation = new aws.acm.CertificateValidation("certificateValidation", {
    certificateArn: certificate.arn,
    validationRecordFqdns: [certificateValidationDomain.fqdn],
  });

// Create the listener for the application
// const listener = new awsx.lb.ApplicationListener("app", { 
//     port: 443, 
//     protocol: "HTTPS",
//     vpc: cluster.vpc, 
//     certificateArn: certificateValidation.certificateArn,
// });

// Creates an ALB associated with our custom VPC.
const alb = new awsx.lb.ApplicationLoadBalancer(
    `gitcoin-service`, { vpc }
  );

// Listen to HTTP traffic on port 80 and redirect to 443
const httpListener = alb.createListener("web-listener", {
    port: 80,
    protocol: "HTTP",
    defaultAction: {
        type: "redirect",
        redirect: {
        protocol: "HTTPS",
        port: "443",
        statusCode: "HTTP_301",
        },
    },
});

// Target group with the port of the Docker image
const target = alb.createTargetGroup(
    "web-target", { vpc, port: 80 }
);

// Listen to traffic on port 443 & route it through the target group
const httpsListener = target.createListener("web-listener", {
    port: 443,
    certificateArn: certificateValidation.certificateArn
}); 

const staticBucket = new aws.lb.ListenerRule("static", {
    listenerArn: httpsListener.listener.arn,
    priority: 100,
    actions: [{
        type: "redirect",
        redirect: {
            host: "s.gitcoin.co",
            port: "443",
            protocol: "HTTPS",
            statusCode: "HTTP_301",
        },
    }],
    conditions: [
        {
            pathPattern: {
                values: ["/static/*"],
            },
        },
    ],
});

 const blog = new aws.lb.ListenerRule("blog", {
     listenerArn: httpsListener.listener.arn,
     priority: 150,
     actions: [{
         type: "redirect",
         redirect: {
             host: "blog.tmp.gitcoin.co",
             port: "443",
             protocol: "HTTPS",
             statusCode: "HTTP_301",
         },
     }],
     conditions: [
         {
             pathPattern: {
             values: ["/blog/*"],
             },
         },
     ],
 });

// Create a DNS record for the load balancer
// const www = new aws.route53.Record("www", {
//     zoneId: route53Zone,
//     name: domain,
//     type: "A",
//     aliases: [{
//         name: httpsListener.endpoint.hostname,
//         zoneId: httpsListener.loadBalancer.loadBalancer.zoneId,
//         evaluateTargetHealth: true,
//     }]
// });

let environment = [
    {
        name: "ENV",
        value: "prod"
    },
    // read me to understand this file:
    // https://github.com/gitcoinco/web/blob/master/docs/ENVIRONMENT_VARIABLES.md

    ///////////////////////////////////////////////////////////////////////////////
    // BASIC PARAMS
    ///////////////////////////////////////////////////////////////////////////////
    {
        name: "CACHE_URL",
        value: "dbcache://my_cache_table"
    },
    {
        name: "REDIS_URL",
        value: redisConnectionUrl
    },
    {
        name: "CACHEOPS_REDIS",
        value: redisCacheOpsConnectionUrl
    },
    {   // TODO: drop this
        name: "COLLECTFAST_CACHE_URL",
        value: "dbcache://collectfast"
    },
    {
        name: "DATABASE_URL",
        value: databaseURL
    },
    {
        name: "READ_REPLICA_1_DATABASE_URL",
        value: readReplica1
    },
    {
        name: "READ_REPLICA_2_DATABASE_URL",
        value: readReplica2
    },
    {
        name: "READ_REPLICA_3_DATABASE_URL",
        value: readReplica1
    },
    {
        name: "READ_REPLICA_4_DATABASE_URL",
        value: readReplica2
    },
    {
        name: "DEBUG",
        value: "off"
    },
    {
        name: "BASE_URL",
        value: "https://bounties.gitcoin.co/"
    },
    {
        name: "SENTRY_DSN",
        value: sentryDSN
    },

    ///////////////////////////////////////////////////////////////////////////////
    // DOCKER PROVISIONING PARAMS
    ///////////////////////////////////////////////////////////////////////////////
    // {
    // name: "FORCE_PROVISION",
    // value: "on"
    // },
    {
        name: "DISABLE_PROVISION",
        value: "on"
    },
    {
        name: "DISABLE_INITIAL_CACHETABLE",
        value: "on"
    },
    {
        name: "DISABLE_INITIAL_COLLECTSTATIC",
        value: "on"
    },
    {
        name: "DISABLE_INITIAL_LOADDATA",
        value: "off"
    },
    {
        name: "DISABLE_INITIAL_MIGRATE",
        value: "off"
    },

    ///////////////////////////////////////////////////////////////////////////////
    // ADVANCED NOTIFICATION PARAMS
    ///////////////////////////////////////////////////////////////////////////////
    // Be VERY CAREFUL when changing this setting.  You don't want to accidentally
    // spam a bunch of github notifications :)
    {
        name: "ENABLE_NOTIFICATIONS_ON_NETWORK",
        value: "rinkeby"
    },

    // Please checkout [Integration Docs](https://github.com/gitcoinco/web/blob/master/docs/THIRD_PARTY_SETUP.md)
    {
        name: "GITHUB_API_USER",
        value: githubApiUser
    },
    {
        name: "GITHUB_API_TOKEN",
        value: githubApiToken
    },

    // For Login integration with Github (login button in top right)
    {
        name: "GITHUB_CLIENT_ID",
        value: githubClientId
    },
    {
        name: "GITHUB_CLIENT_SECRET",
        value: githubClientSecret
    },
    {
        name: "GITHUB_APP_NAME",
        value: githubAppName
    },
    {
        name: "CHAT_SERVER_URL",
        value: "chat"
    },
    {
        name: "CHAT_URL",
        value: "localhost"
    },

    // To enable Google verification(in profile's trust tab)
    {
        name: "GOOGLE_CLIENT_ID",
        value: ""
    },
    {
        name: "GOOGLE_CLIENT_SECRET",
        value: ""
    },

    // For Facebook integration (in profile's trust tab)
    {
        name: "FACEBOOK_CLIENT_ID",
        value: ""
    },
    {
        name: "FACEBOOK_CLIENT_SECRET",
        value: ""
    },

    // For notion integration (on grant creation)
    {
        name: "NOTION_API_KEY",
        value: ""
    },
    {
        name: "NOTION_SYBIL_DB",
        value: ""
    },

    {
        name: "INFURA_USE_V3",
        value: "True"
    },

    {
        name: "SUPRESS_DEBUG_TOOLBAR",
        value: "1"
    },
    {
        name: "SENDGRID_API_KEY",
        value: sendgridApiKey
    },
    {
        name: "SENDGRID_EVENT_HOOK_URL",
        value: "sg_sendgrid_event_processor"
    },
    {
        name: "CONTACT_EMAIL",
        value: "support@gitcoin.co"
    },
    {
        name: "FEE_ADDRESS",
        value: ""
    },
    {
        name: "FEE_ADDRESS_PRIVATE_KEY",
        value: ""
    },
    {
        name: "GIPHY_KEY",
        value: ""
    },
    {
        name: "YOUTUBE_API_KEY",
        value: ""
    },
    {
        name: "VIEW_BLOCK_API_KEY",
        value: ""
    },
    {
        name: "ETHERSCAN_API_KEY",
        value: etherscanApiKey
    },
    {
        name: "POLYGONSCAN_API_KEY",
        value: "K2FQK241WVVIQ66YJRK3NIMYPR8ZX3GM6D"
    },
    {
        name: "FORTMATIC_LIVE_KEY",
        value: ""
    },
    {
        name: "FORTMATIC_TEST_KEY",
        value: ""
    },
    {
        name: "XINFIN_API_KEY",
        value: ""
    },
    {
        name: "ALGORAND_API_KEY",
        value: ""
    },

    {
        name: "PYPL_CLIENT_ID",
        value: ""
    },

    {
        name: "BRIGHTID_PRIVATE_KEY",
        value: brightIdPrivateKey
    },

    {
        name: "PREMAILER_CACHE",
        value: "LRU"
    },
    {
        name: "PREMAILER_CACHE_MAXSIZE",
        value: "4096"
    },

    {
        name: "GTC_DIST_API_URL",
        value: gtcDistApiUrl
    },
    {
        name: "GTC_DIST_KEY",
        value: gtcDistKey
    },

    // CYPRESS METAMASK VARIABLES
    {
        name: "NETWORK_NAME",
        value: "localhost"
    },
    {
        name: "SECRET_WORDS",
        value: ""
    },
    {
        name: "PASSWORD",
        value: ""
    },
    {
        name: "CYPRESS_REMOTE_DEBUGGING_PORT",
        value: "9222"
    },

    {
        name: "TEST_MNEMONIC",
        value: "chief loud snack trend chief net field husband vote message decide replace"
    },

    ///////////////////////////////////////////////////////////////////////////////
    // Specific for review env test
    ///////////////////////////////////////////////////////////////////////////////
    {
        name: "AWS_ACCESS_KEY_ID",
        value: usrLoggerKey
    },
    {
        name: "AWS_SECRET_ACCESS_KEY",
        value: usrLoggerSecret
    },
    {
        name: "AWS_DEFAULT_REGION",
        value: "us-west-2"          // TODO: configure this
    },

    {
        name: "AWS_STORAGE_BUCKET_NAME",
        value: bucketName
    },
    {
        name: "STATIC_HOST",
        value: "https://d31ygswzsyecnt.cloudfront.net/"
    },
    {
        name: "AWS_S3_CUSTOM_DOMAIN",
        value: "https://d31ygswzsyecnt.cloudfront.net/"
    },
    {
        name: "STATIC_URL",
        value: "static/"
    },
    {
        name: "MEDIAFILES_LOCATION",
        value: "" // empty on purpose
    },
    // This is used for prod: STATICFILES_STORAGE = env('STATICFILES_STORAGE', default='app.static_storage.SilentFileStorage')
    // STATICFILES_STORAGE = env('STATICFILES_STORAGE', default='django.contrib.staticfiles.storage.StaticFilesStorage')
    // Going with this for the time being:  django.contrib.staticfiles.storage.StaticFilesStorage 
    {
        name: "STATICFILES_STORAGE",
        value: "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
    {
        name: "BUNDLE_USE_CHECKSUM",
        value: "false",
    },
    {
        name: "MEDIA_URL",
        value: "https://d31ygswzsyecnt.cloudfront.net/"
    },
    {
        name: "MEDIA_CUSTOM_DOMAIN",
        value: "d31ygswzsyecnt.cloudfront.net"
    },
    {
        name: "SECRET_KEY",
        value: secretKey
    },
    {
        name: "ALCHEMY_KEY",
        value: alchemyKey
    }
];

const service = new awsx.ecs.FargateService("app", {
    cluster,
    desiredCount: 6,
    subnets: vpc.privateSubnetIds,
    taskDefinitionArgs: {
        containers: {
            web: {
                image: dockerGtcWebImage,
                command: ["gunicorn", "-w", "1", "-b", "0.0.0.0:80", "app.wsgi:application", "--max-requests", "100", "--max-requests-jitter", "10", "--timeout", "60"],
                memory: 4096,
                cpu: 2000,
                portMappings: [httpsListener],
                environment: environment,
                links: []
            },
        },
    },
});

const celery1 = new awsx.ecs.FargateService("celery1", {
    cluster,
    desiredCount: 3,
    subnets: vpc.privateSubnetIds,
    taskDefinitionArgs: {
        containers: {
            worker1: {
                image: dockerGtcWebImage,
                command: ["celery", "-A", "taskapp", "-n", "worker1", "worker", "-Q", "high_priority,default,marketing,celery"],
                memory: 4096,
                cpu: 2000,
                portMappings: [],
                environment: environment,
                dependsOn: [],
                links: []
            },
            worker2: {
                image: dockerGtcWebImage,
                command: ["celery", "-A", "taskapp", "-n", "worker2", "worker", "-Q", "high_priority"],
                memory: 4096,
                cpu: 2000,
                portMappings: [],
                environment: environment,
                dependsOn: [],
                links: []
            },
        },
    },
});

const flowerBrokerString = pulumi.interpolate`--broker=${redisConnectionUrl}`.apply.toString();

const flower = new awsx.ecs.FargateService("flower", {
    cluster,
    desiredCount: 1,
    taskDefinitionArgs: {
        containers: {
            celery: {
                image: "mher/flower",
                command: ["celery", "flower", "-A" , flowerBrokerString , "taskapp", "--port=5555"],
                memory: 4096,
                cpu: 2000,
                portMappings: [],
                environment: environment,
                dependsOn: [],
                links: []
            },
        },
    },
});

const ecsTarget = new aws.appautoscaling.Target("autoscaling_target", {
    maxCapacity: 10,
    minCapacity: 1,
    resourceId: pulumi.interpolate`service/${cluster.cluster.name}/${service.service.name}`,
    scalableDimension: "ecs:service:DesiredCount",
    serviceNamespace: "ecs",
});

// Export the URL so we can easily access it.
// export const frontendURL = pulumi.interpolate`http://${listener.endpoint.hostname}/`;
// export const frontend = listener.endpoint



//////////////////////////////////////////////////////////////
// Set up EC2 instance 
//      - it is intended to be used for troubleshooting
//////////////////////////////////////////////////////////////

// Create a new security group that permits SSH and web access.
const secgrp = new aws.ec2.SecurityGroup("secgrp", {
    description: "gitcoin",
    vpcId: vpc.id,
    ingress: [
        { protocol: "tcp", fromPort: 22, toPort: 22, cidrBlocks: ["0.0.0.0/0"] },
        { protocol: "tcp", fromPort: 80, toPort: 80, cidrBlocks: ["0.0.0.0/0"] },
    ],
    egress: [{
        protocol: "-1",
        fromPort: 0,
        toPort: 0,
        cidrBlocks: ["0.0.0.0/0"],
    }],
});

export const securityGroupsForEc2 = secgrp.id;

const ubuntu = aws.ec2.getAmi({
    mostRecent: true,
    filters: [
        {
            name: "name",
            values: ["ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*"],
        },
        {
            name: "virtualization-type",
            values: ["hvm"],
        },
    ],
    owners: ["099720109477"],
});

// Script to install docker in ec2 instance
const ec2InitScript = `#!/bin/bash

# Installing docker in ubuntu
# Instructions taken from here: https://docs.docker.com/engine/install/ubuntu/

mkdir /var/log/gitcoin
echo $(date) "Starting installation of docker" >> /var/log/gitcoin/init.log
apt-get remove docker docker-engine docker.io containerd runc

apt-get update

apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
    
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
  
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io
mkdir /var/log/gitcoin
echo $(date) "Finished installation of docker" >> /var/log/gitcoin/init.log

`

const web = new aws.ec2.Instance("Web", {
    ami: ubuntu.then(ubuntu => ubuntu.id),
    associatePublicIpAddress: true,
    instanceType: "t3.medium",
    subnetId: vpcPublicSubnet1.then(),

    vpcSecurityGroupIds: [secgrp.id],
    rootBlockDevice: {
        volumeSize: 50
    },
    tags: {
        Name: "Troubleshooting instance",
    },
    userData: ec2InitScript,
});

export const ec2PublicIp = web.publicIp;

// Build and export the command to use the docker image of this specific deployment from an EC2 instance within the subnet
export const dockerConnectCmd = pulumi.interpolate`docker run -it \
-e DATABASE_URL=${tempDatabase} \
-e CACHEOPS_REDIS=${redisCacheOpsConnectionUrl} \
-e REDIS_URL=${redisConnectionUrl} \
-e STATIC_HOST=${bucketWebURL} \
-e STATIC_URL=static/ \
-e STATICFILES_STORAGE=django.contrib.staticfiles.storage.StaticFilesStorage \
-e ENV=test \
${dockerGtcWebImage} bash \
`
