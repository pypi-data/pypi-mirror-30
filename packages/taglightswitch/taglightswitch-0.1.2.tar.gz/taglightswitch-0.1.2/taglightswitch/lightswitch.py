"""
tags used by lightswitch to determine power on/off behavior for a given EC2 instance.

At this time, only

   lightswitch:offhours

is defined.
"""

import datetime
import logging

import boto3
from taglightswitch import ControlTags
from taglightswitch import SwitchableItem

class BadTagError(ValueError):
    """Wrap value exception in project custom error"""
    pass

class LightSwitch(object):
    """find and parse values for EC2 instances with lightswitch: tags"""

    @classmethod
    def get_version(cls):
        return "ls:1"

    def __init__(self, target_time=None, target_date=None):
        self.tag_pattern = ControlTags.get_target_tag_name()

        self.target_time = target_time
        if not self.target_time:
            self.target_time = datetime.datetime.now().time()

        self.target_date = target_date
        if not self.target_date:
            self.target_date = datetime.datetime.now().date()

        self.ec2 = None
        self.logger = logging.getLogger(__name__)

        self.switchable_list = {}
        self.session = None
        self.ec2 = None
        self.caller_identity = None
        self.account = None

    # fetch or initialize boto3 client
    def _get_ec2(self):
        if not self.ec2:
            self.session = boto3.session.Session()
            self.ec2 = self.session.resource('ec2')
            self.caller_identity = boto3.client('sts').get_caller_identity()
            self.account = self.caller_identity['Account']
        self.logger.debug('boto: %s', self.ec2)

        return self.ec2

    def find_tagged_instances(self):
        """return flattened keys and instance IDs for instances with lightswitch tags"""
        ec2 = self._get_ec2()

        instances = ec2.instances.all() # TODO: make smarter match with filter
        found_instances = {}

        for instance in instances:
            # if tags is NoneType, no tags and iterate will die so just add all to found lists
            if instance.tags:
                for this_tag in instance.tags:
                    if this_tag["Key"].startswith(self.tag_pattern):
                        found_instances[instance] = SwitchableItem(instance)
                        break

        self.switchable_list = found_instances
        return found_instances

    def dump_aws_info(self):
        return "AWSaccount={} AWSprofile={} access_key={}".format(self.account, self.session.profile_name, self.session.get_credentials().access_key)

    def advise(self):
        if not self.switchable_list.keys():
            self.find_tagged_instances()

        sw_dict = self.switchable_list.items()
        print(self.dump_aws_info())
        print("advise power changes against {} switchable items for target time {} date {}".format(len(sw_dict), self.target_time.isoformat(), self.target_date.isoformat()))
        for (inst, switchable_item) in sw_dict:
            advice_text = switchable_item.advise_power_state(self.target_time, self.target_date)
            print(advice_text)

    def correct(self):
        if not self.switchable_list.keys():
            self.find_tagged_instances()

        sw_dict = self.switchable_list.items()
        print(self.dump_aws_info())
        print("correct power states for {} switchable items for target time {} date {}".format(len(sw_dict), self.target_time.isoformat(), self.target_date.isoformat()))
        for (inst, switchable_item) in sw_dict:
            correction_text = switchable_item.correct_power_state(self.target_time, self.target_date)
            print(correction_text)
