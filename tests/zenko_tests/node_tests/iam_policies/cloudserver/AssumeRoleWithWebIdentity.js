const assert = require('assert');
const async = require('async');
const VaultClient = require('../../VaultClient');
const { getS3Client } = require('../../s3SDK');
const { getSTSClient } = require('../../stsSDK');
const { getTokenForIdentity } = require('../../utils/getWebIdentityToken');
const { metadataSearchResponseCode } = require('./utils');

let iamClient = null;
let stsClient = null;
let s3Client = null;

const clientAdmin = VaultClient.getAdminClient();
const accountName = 'AccountTest';
const accountInfo = {
    email: `${accountName}@test.com`,
    password: 'test',
};
const externalAccessKey = 'DZMMJUPWIUK8IWXRP0HQ';
const externalSecretKey = 'iTuJdlidzrLipymvAGrLP66Yxghl4NQxLZR3cLlu';

const duration = '1000';

const bucket1 = 'bucket1';

const storageManagerName = 'storage_manager';
const storageAccountOwnerName = 'storage_account_owner';
const dataConsumerName = 'data_consumer';
const storageManagerRole = 'storage-manager-role';
const storageAccountOwnerRole = 'storage-account-owner-role';
const dataConsumerRole = 'data-consumer-role';

describe('iam policies - cloudserver - AssumeRoleWithWebIdentity - Metadata', () => {

    before(done => {
        async.series([
            // create an account, generateAccountAccessKey for it
            // get iam client, sts client and s3 client of this account
            next => clientAdmin.createAccount(accountName, accountInfo, next),
            next => clientAdmin.generateAccountAccessKey(accountName, next, { externalAccessKey, externalSecretKey }),
            next => {
                iamClient = VaultClient.getIamClient(externalAccessKey, externalSecretKey);
                stsClient = getSTSClient(externalAccessKey, externalSecretKey);
                s3Client = getS3Client(externalAccessKey, externalSecretKey);
                next();
            },
            // use s3 client to create a bucket and put 2 objects
            next => {
                async.series([
                    next => s3Client.createBucket({ Bucket: bucket1 }, next),
                    next => s3Client.putObject({ Bucket: bucket1, Key: 'file1' }, next),
                    next => s3Client.putObject({ Bucket: bucket1, Key: 'file2' }, next),
                ], next);
            },
        ], done);
    });

    after(done => {
        async.series([
            next => s3Client.deleteObjects({
                Bucket: bucket1,
                Delete: {
                    Objects: [{ Key: 'file1' }, { Key: 'file2' }],
                    Quiet: false,
                },
            }, next),
            next => s3Client.deleteBucket({ Bucket: bucket1 }, next),
            next => clientAdmin.deleteAccount(accountName, next),
        ], done);
    });


    const tests = [
        {
            name: 'should be able to perform metadata search on all buckets for storage manager role',
            oidcIdentity: storageManagerName,
            roleName: storageManagerRole,
            assertion: result => assert.strictEqual(result.statusCode, 200),
        },
        {
            name: 'should be able to perform metadata search on all buckets for storage account owner role',
            oidcIdentity: storageAccountOwnerName,
            roleName: storageAccountOwnerRole,
            assertion: result => assert.strictEqual(result.statusCode, 200),
        },
        {
            name: 'should be able to perform metadata search on all buckets for data consumer role',
            oidcIdentity: dataConsumerName,
            roleName: dataConsumerRole,
            assertion: result => assert.strictEqual(result.statusCode, 200),
        },
    ];

    tests.forEach((test, i) => {
        it(test.name, done => {
            let jwtToken = null;
            let roleArn = null;
            async.waterfall([
                next => getTokenForIdentity(test.oidcIdentity, (err, token) => {
                    assert.ifError(err);
                    jwtToken = token;
                    next();
                }),
                next => iamClient.getRole({ RoleName: test.roleName }, (err, res) => {
                    assert.ifError(err);
                    roleArn = res.Role.Arn;
                    next();
                }),
                next => stsClient.assumeRoleWithWebIdentity({
                    RoleArn: roleArn,
                    DurationSeconds: duration,
                    WebIdentityToken: jwtToken,
                    RoleSessionName: `session-name-test-${i}`,
                }, (err, res) => {
                    assert.ifError(err);
                    return next(null, res);
                }),
                (res, next) => {
                    const sessionUserCredentials = {
                        accessKeyId: res.Credentials.AccessKeyId,
                        secretAccessKey: res.Credentials.SecretAccessKey,
                        sessionToken: res.Credentials.SessionToken,
                    };
                    // make metadataSearch request using session user's credentials
                    // and see if can get the correct response
                    metadataSearchResponseCode(sessionUserCredentials, bucket1, (err, res) => {
                        if (err) {
                            assert.ifError(err);
                            return done(err);
                        }
                        test.assertion(res);
                        return next();
                    });
                }], done);
        });
    });
});
