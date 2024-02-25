# py-lambda-docker

Boilerplate example for setting up a serverless api using AWS Lambda via SAM.

Lambdas which run off ECR-uploaded Docker images are needed for heavier weight dependencies like Pytorch.

For longer jobs, API Gateway has a request limit of 30 seconds for HTTP/REST APIs (which can be worked around via WebSocket APIs). Here Lambda Function URLs are used instead, which support timeouts of up to 15 minutes.

## Setup

### Environment variables

Setup loading .env variables: https://direnv.net/

```bash
direnv allow
```

### Python

Uses Python 3.11. To easily switch between versions of python, consider setting up [pyenv](https://github.com/pyenv/pyenv).

[PDM](https://github.com/pdm-project/pdm) is used for proper dependency resolution and convenience scripts.

```bash
pip install pipx
pipx install pdm
```

Pre-commit is used for some commit hooks:
```bash
pip install pre-commit
pre-commit install
```

### IAM Identity Center (SSO)

1. Enable IAM Identity Center following: https://aws.amazon.com/iam/identity-center/
1. Add user `admin`
1. Add group `Admins` to Groups
1. Add `admin` to `Admins`
1. Add a permission set `AdministratorAccess` based on the `AdministratorAccess` AWS managed policy
1. Assign the permission set to the `Admins` group under `AWS accounts → Assign users or groups`

### AWS CLI
1. Install AWS CLI

    ```bash
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
    unzip awscliv2.zip
    sudo ./aws/install
    # or update:
    $ sudo ./aws/install --bin-dir /usr/local/bin --install-dir /usr/local/aws-cli --update
    ```

    (ref: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

1. Configure CLI session and login

    ```bash
    aws configure sso
    # enter info...
    aws sso login --sso-session admin
    ```

1. Check the resulting config at `~/.aws/config` and make sure it matches what you expect, for ex:

    ```
    [profile admin]
    region = us-east-1
    sso_session = admin
    sso_account_id = 123456789012
    sso_role_name = AdministratorAccess

    [sso-session admin]
    sso_region = us-east-1
    sso_start_url = https://my-sso-portal.awsapps.com/start
    sso_registration_scopes = sso:account:access
    ```

    (ref: https://docs.aws.amazon.com/cli/latest/userguide/sso-configure-profile-token.html)

## Install

```bash
pdm install-all
```

## Build

The pdm script also lints the syntax of the `template.yaml` file.

```bash
pdm sam-build
```

## Deploy

Make sure `AWS_REGION` and `AWS_ACCOUNT_ID` are set in `.env` environment variables. These are needed to login Docker to ECR.

### Lambda

Sign into AWS SSO using a user that can deploy:

```bash
aws sso login --profile admin
```

This run script triggers a build and also outputs the deployed Lambda Function URL for convenience:

```bash
pdm sam-deploy
```

## Test

Use a tool that supports AWS signature v4 to test, for example postman (https://www.postman.com/) or curl (https://stackoverflow.com/a/68456301).

### Postman

1. In Postman, select AWS Signature under the Authorization tab.
1. Add postman environment variables for the parameters:
   - AccessKey: {{access_key}}
   - SecretKey: {{secret_key}}
   - AWS Region: {{region}}
   - Service Name: {{service}}
   - Session Token: {{session_token}}
1. Create and edit the variables in an environment:
   ```
   (variable)    (type)   (initial value)
   access_key    secret   ''
   secret_key    secret   ''
   region        default  us-east-1
   service       default  lambda
   session_token secret   ''
   ```
1. For future sessions you need to copy in the credentials into "current value" for the secret variables.

### Automated

Start up local api endpoint (see [SAM local limitations](#sam-local-limitations)):
```bash
pdm local
# Separate terminal tab
pdm fwd
```

Then:
```bash
pdm test
```

## Run (local api)

Different pdm scripts exist for testing the Lambda endpoints locally:

- sam-local: local Lambda emulation
- fwd-sam-local: start up an endpoint that just forwards api requests to sam local

### Authentication

Local Lambda authentication is handled automatically--you need to setup and login to AWS SSO to use sam local.

### SAM local limitations

SAM local does not support running an api for Lambda Function URLs automatically.
ref: https://github.com/aws/aws-sam-cli/issues/4299

To run local api conveniently (shorter url, GET rather than POST), there is a Flask app to interface with SAM local.

Check which methods are implemented at `localapi/app.py` (i.e. GET, POST, ...).

```bash
# Convenience script to sam local command
pdm local
# Convenience script to run flask forwarder
pdm fwd
```

Then you can call for example: `curl http://localhost:5000/`

Alternatively, just run sam local (or `pdm local`) and then:

```bash
curl -XPOST http://localhost:3001/2015-03-31/functions/{lambda_function_name}/invocations -d '{"payload":"value"}'
```

Note that only POST and setting request body seems to be supported.

&nbsp;

---

# Default SAM documentation

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI. It includes the following files and folders.

- hello_world - Code for the application's Lambda function and Project Dockerfile.
- events - Invocation events that you can use to invoke the function.
- tests - Unit tests for the application code. 
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions and an API Gateway API. These resources are defined in the `template.yaml` file in this project. You can update the template to add AWS resources through the same deployment process that updates your application code.

## Deploy the sample application

The Serverless Application Model Command Line Interface (SAM CLI) is an extension of the AWS CLI that adds functionality for building and testing Lambda applications. It uses Docker to run your functions in an Amazon Linux environment that matches Lambda. It can also emulate your application's build environment and API.

To use the SAM CLI, you need the following tools.

* SAM CLI - [Install the SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html)
* Docker - [Install Docker community edition](https://hub.docker.com/search/?type=edition&offering=community)

You may need the following for local testing.
* [Python 3 installed](https://www.python.org/downloads/)

To build and deploy your application for the first time, run the following in your shell:

```bash
sam build
sam deploy --guided
```

The first command will build a docker image from a Dockerfile and then copy the source of your application inside the Docker image. The second command will package and deploy your application to AWS, with a series of prompts:

* **Stack Name**: The name of the stack to deploy to CloudFormation. This should be unique to your account and region, and a good starting point would be something matching your project name.
* **AWS Region**: The AWS region you want to deploy your app to.
* **Confirm changes before deploy**: If set to yes, any change sets will be shown to you before execution for manual review. If set to no, the AWS SAM CLI will automatically deploy application changes.
* **Allow SAM CLI IAM role creation**: Many AWS SAM templates, including this example, create AWS IAM roles required for the AWS Lambda function(s) included to access AWS services. By default, these are scoped down to minimum required permissions. To deploy an AWS CloudFormation stack which creates or modifies IAM roles, the `CAPABILITY_IAM` value for `capabilities` must be provided. If permission isn't provided through this prompt, to deploy this example you must explicitly pass `--capabilities CAPABILITY_IAM` to the `sam deploy` command.
* **Save arguments to samconfig.toml**: If set to yes, your choices will be saved to a configuration file inside the project, so that in the future you can just re-run `sam deploy` without parameters to deploy changes to your application.

You can find your API Gateway Endpoint URL in the output values displayed after deployment.

## Use the SAM CLI to build and test locally

Build your application with the `sam build` command.

```bash
sam-app$ sam build
```

The SAM CLI builds a docker image from a Dockerfile and then installs dependencies defined in `hello_world/requirements.txt` inside the docker image. The processed template file is saved in the `.aws-sam/build` folder.

Test a single function by invoking it directly with a test event. An event is a JSON document that represents the input that the function receives from the event source. Test events are included in the `events` folder in this project.

Run functions locally and invoke them with the `sam local invoke` command.

```bash
sam-app$ sam local invoke HelloWorldFunction --event events/event.json
```

The SAM CLI can also emulate your application's API. Use the `sam local start-api` to run the API locally on port 3000.

```bash
sam-app$ sam local start-api
sam-app$ curl http://localhost:3000/
```

The SAM CLI reads the application template to determine the API's routes and the functions that they invoke. The `Events` property on each function's definition includes the route and method for each path.

```yaml
      Events:
        HelloWorld:
          Type: Api
          Properties:
            Path: /hello
            Method: get
```

## Add a resource to your application
The application template uses AWS Serverless Application Model (AWS SAM) to define application resources. AWS SAM is an extension of AWS CloudFormation with a simpler syntax for configuring common serverless application resources such as functions, triggers, and APIs. For resources not included in [the SAM specification](https://github.com/awslabs/serverless-application-model/blob/master/versions/2016-10-31.md), you can use standard [AWS CloudFormation](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-template-resource-type-ref.html) resource types.

## Fetch, tail, and filter Lambda function logs

To simplify troubleshooting, SAM CLI has a command called `sam logs`. `sam logs` lets you fetch logs generated by your deployed Lambda function from the command line. In addition to printing the logs on the terminal, this command has several nifty features to help you quickly find the bug.

`NOTE`: This command works for all AWS Lambda functions; not just the ones you deploy using SAM.

```bash
sam-app$ sam logs -n HelloWorldFunction --stack-name "sam-app" --tail
```

You can find more information and examples about filtering Lambda function logs in the [SAM CLI Documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-logging.html).

## Unit tests

Tests are defined in the `tests` folder in this project. Use PIP to install the [pytest](https://docs.pytest.org/en/latest/) and run unit tests from your local machine.

```bash
sam-app$ pip install pytest pytest-mock --user
sam-app$ python -m pytest tests/ -v
```

## Cleanup

To delete the sample application that you created, use the AWS CLI. Assuming you used your project name for the stack name, you can run the following:

```bash
sam delete --stack-name "sam-app"
```

## Resources

See the [AWS SAM developer guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html) for an introduction to SAM specification, the SAM CLI, and serverless application concepts.

Next, you can use AWS Serverless Application Repository to deploy ready to use Apps that go beyond hello world samples and learn how authors developed their applications: [AWS Serverless Application Repository main page](https://aws.amazon.com/serverless/serverlessrepo/)
