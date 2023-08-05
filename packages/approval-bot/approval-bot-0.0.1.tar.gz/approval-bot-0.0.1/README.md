# approval-bot (WIP...)
![](https://raw.githubusercontent.com/danielwhatmuff/approval-bot/master/img/approval-request-screenshot.png)

## Intro
This tool was created to facilitate a flexible approval workflow using a simple CLI and custom Slack slash command.
It can be easily integrated with any CI/CD tool to request an approval from a private Slack channel and provides an audit trail for who approved what.

## Setup
![](https://raw.githubusercontent.com/danielwhatmuff/approval-bot/master/img/add-to-slack.png)
* )Install the approval-bot Slack app to your workspace and authorise permissions - [Add to Slack](https://slack.com/oauth/authorize?client_id=316313168788.316454218293&scope=commands,chat:write:bot)
* Create a token to access the slack API, at https://api.slack.com/custom-integrations/legacy-tokens click `Create token`
* Find out your team ID by navigating to https://api.slack.com/methods/team.info/test and clicking `Tester` then `Test Method`, it will be shown like the below:
```
{
    "ok": true,
    "team": {
        "id": "YOURIDHERE",
        ...
```
* Install the approval-bot python package in your job/script and add a call of the CLI providing the required arguments `--message, --teamid and --channel`.
```
$ pip install approval-bot
approval-bot --message 'Thing to be approved' --teamid 'teamid' --channel 'approvers'
```
* Optionally set a --timeout in seconds, the default is 300 (please take into account any billing impact this may have if you pay per build minute!)

## About the approval message `--message`
* This is used to provide approvers with a description of what requires approval, make sure it is descriptive!
* It needs to be unique across all runs of all jobs, so make sure it changes each time. A simple method is to add a timestamp e.g. `$(date +%s)` or use build environment variables if you are running from a CI provider (see examples below).
* CI injected environment variables can be used to create dynamic approval messages, see examples below:

```
$ approval-bot -m "Deploying commit $TRAVIS_COMMIT of project $TRAVIS_REPO_SLUG to prod - Travis build $TRAVIS_BUILD_NUMBER"
$ approval-bot -m "Pushing new assets from $CIRCLE_PROJECT_USERNAME/$CIRCLE_PROJECT_REPONAME  - Circle CI build $CIRCLE_BUILD_NUM"
$ approval-bot -m "Deploying commit $GIT_COMMIT of $JOB_NAME - Jenkins build $JENKINS_URL"
$ approval-bot -m "Deploying branch $BITBUCKET_BRANCH of repo $BITBUCKET_REPO_SLUG - Bitbucket Pipelines $BITBUCKET_BUILD_NUMBER"
$ approval-bot -m "Scheduling nightly shutdown of dev servers - Circle $CI_BUILD_ID"
$ approval-bot -m "Syncing files to $DRONE_DEPLOY_TO - PR number $DRONE_PULL_REQUEST"
```

## About the approval channel `--channel`
* Create a channel used for approvals, it can either be company/team/project/repo specific and can be made private to restric permissions.

## How it works
*  you've installed/authorised the approval-bot slack command and added the `approval-bot`.
* Your job will pause when the approval-bot command is executed until its approved, denied or times out after the `--timeout`.
* Approvers will be notified in the channel specified in `--channel` and can then reply using the `/approval-bot` slash command with the ID and either `approve` or `deny` (this will be explained in the approval message).
* The job will then either abort, continue or time out depending on the approvers response.
* A notification will be sent back to the slack channel detailing who approved / denied the request as an audit trail.
* If a job times out or was accidentally denied, it can simply be re-run and then approved.

## References
* https://docs.travis-ci.com/user/environment-variables/#Convenience-Variables
* https://confluence.atlassian.com/bitbucket/environment-variables-794502608.html
* https://wiki.jenkins.io/display/JENKINS/Building+a+software+project#Buildingasoftwareproject-belowJenkinsSetEnvironmentVariables
* https://circleci.com/docs/2.0/env-vars/
* http://readme.drone.io/0.5/usage/environment-reference/

## Args
```
approval-bot --help
usage: approval-bot [-h] -m MESSAGE -c CHANNEL -T TEAMID [-t TIMEOUT] [-d]
                    [-v]

Request approval CLI

optional arguments:
  -h, --help            show this help message and exit
  -m MESSAGE, --message MESSAGE
                        A message describing the approval job
  -c CHANNEL, --channel CHANNEL
                        Slack channel to use for approvals
  -T TEAMID, --teamid TEAMID
                        Slack Team ID
  -t TIMEOUT, --timeout TIMEOUT
                        Approval wait timeout in seconds
  -d, --debug           Enable debug output
  -v, --version         Show installed version
```
