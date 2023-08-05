[![Build Status](https://travis-ci.org/bbacker/taglightswitch.svg?branch=master)](https://travis-ci.org/bbacker/taglightswitch)

# taglightswitch

power EC2 instances on/off based on tag schedule contents

## Goals:

1. allow EC2 instance to be turned off at nights for cost control
1. minimize required interaction with AWS by the users of the EC2 instances
1. allow check power states vs schedule action to be executed by cron, jenkins, lambda, or command line
1. keep scheduled actions for instances with the instances, not a separate data store that needs to be kept in sync
    - allow cloud formation template or newly generated instance to opt in to schedule power by tagging their instance
    - allow EC2 user to opt out by removing or modifying the instance tags
1. allow a dry run mode where power changes are explained but not actually performed

## Tagging format 

### Off hours - simple range of time during the given day

Ex. applying a tag to EC2 instance

        "Key": "lightswitch:offhours", "Value": "start=19:00,end=07:00",

means you would like the instance to be powered off after 19:00 (7pm), powered back on at 07:00 (7AM).
These ranges bound when the power on/off happens, but they power is done by
the script. That means if the script was run every 10 minutes, say at 6:45AM, 6:55AM, 7:05AM,
7:15AM, etc, the executions at 7:05AM, 7:15AM, etc would power on the server if it was off.
Similarly the executions at 6:45AM and 6:55AM would have turned the server off if it
was on during that time since those times fall within the "lightswitch:offhours".

The time in the range is evaluated vs the supplied target time without timezones.
That means you if you intend a given set of ranges to be Pacific Standard Time,
the execute the command with a target time in PST.

### Off days - power off given days

        "Key": "lightswitch:offdays", "Value": "sat, sun"

means you would like the instance to be powered off any time saturdays or sundays.

The default is no off days.

### Off mode - toggle or leaveoff

        "Key": "lightswitch:offmode", "Value": "offonly"

or

        "Key": "lightswitch:offmode", "Value": "toggle"

Toggle means turn off the instances during offhours or off days. If neither outside of
offhours and offdays (i.e. the normal work days) and the server is seen to be off,
turn it on.  Specifying mode 'leaveoff' only powers servers off, does not
turn them back on automatically. This is useful for situations where users tend
to perform proof of concept work, not clean up afterwards, but have console or CLI access
to turn instances back on, edit tags manually when they wish to resume work.

The default mode is toggle.

### Viewing tags

See tagged instances

    $ export AWS_PROFILE=myaccountprofile
    $ aws ec2 describe-instances --filters 'Name=tag-key,Values=lightswitch*'

see tagged instances ids and power states only, requires [jq](https://stedolan.github.io/jq/tutorial/).

    $ export AWS_PROFILE=myaccountprofile
    $ aws ec2 describe-instances --filters 'Name=tag-key,Values=lightswitch*' \
        | jq '.Reservations | .[] | .Instances | .[] | .InstanceId,.State.Name'

# Setup

 The tools do not have arguments for aws roles, keys, profiles, etc but rely on either the
executing environment (e.g. a jenkins instance's EC2 role or 
[environment variables](http://boto3.readthedocs.io/en/latest/guide/configuration.html#environment-variables)
) to provide access. 

Execute this to set AWS_PROFILE env var before any of the following examples:

    $ export AWS_PROFILE=myaccountprofile

## Power 'advise' usage

To give advice for right now on which should be on or off.

    $ check_lightswitches.py

or

    $ check_lightswitches.py -a advise

To give advice for which should be on or off at 9pm tonight

    $ check_lightswitches.py -t 21:00

To give advice for which should be on or off at 9pm next Sunday

    $ check_lightswitches.py -t 21:00 -d sunday

## Power 'correct' usage

To have the script take action (power on or off) for instances not matching their desired power state.

Apply power changes suitable for today and current time:

    $ check_lightswitches.py -a correct

The -t and -d arguments can be applied for 'correct' as well, but be careful - you're applying power changes
for a different time than the original user applying the tags desired.

## TODO
    * install check script somewhere in $PATH
    * package to pypi
    * examples on how to add, change tags from CLI
    * mock boto3 calls so tests can can include platform agnostic find and boto3 failure mode tests
    * test and document use of timezones in offhours parsing

## TO CONSIDER
    * document minimum viable AWS role to allow users to power instances back on, adjust tags to temporarally suspend power off
    * output results of real power actions to SNS
    * ? ASG - reduce min and desired to zero. problem: when bringing back up, where to store original count to which min should be restored?
