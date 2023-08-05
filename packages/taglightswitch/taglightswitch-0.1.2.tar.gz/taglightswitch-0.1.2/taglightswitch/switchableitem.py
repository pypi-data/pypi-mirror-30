"""
Wrap the EC2 instance in an object so we can keep state, parsed versions of
info like start/stop tag values with the instance info

"""
# pylint: disable=line-too-long, too-many-instance-attributes
import logging

import boto3
import datetime
from taglightswitch import ControlTags

nowdate=datetime.datetime.now().date()

class SwitchableItem(object):
    """tagged EC2 info and state"""

    def get_power_state(self):
        """ return current power state - e.g. running or stapped. see AWS docs for all possible values """
        return self.instance.state["Name"]

    # make separate class methods so easier to unit test without real EC2 data
    @classmethod
    def _compute_recommended_power_state(cls, current_state, offhours, current_time, lightswitchmode, offdays=[], current_date=nowdate):

        # possible states are  (pending | running | shutting-down | terminated | stopping | stopped ).
        # rule 1: we will only consider instances in the 'running' or 'stopped'
        # states, leave instances in any other states unchanged
        if not (current_state.lower() == 'stopped' or
                current_state.lower() == 'running'):
            return current_state

        is_offhours = ControlTags.time_is_within_range(offhours[0], offhours[1], current_time)
        is_offday = ControlTags.date_matches_an_offday(offdays, current_date)

        # rule 2: offhours powered on so turn off
        if is_offhours and current_state == "running":
            return "stopped"

        # rule 3: offday powered on so turn off
        if is_offday and current_state == "running":
            return "stopped"

        # rule 4: it's not offhours or offdays and it's powered off so turn back on if mode is toggle
        if (not is_offhours) and (current_state == "stopped") and lightswitchmode == ControlTags.MODE_TOGGLE:
            return "running"

        return current_state


    def advise_power_state(self, current_time, current_date=nowdate):
        """ given current time, return string describing object and present, desired power state"""
        presentstate = self.get_power_state()
        nextstate = SwitchableItem._compute_recommended_power_state(presentstate, self.offhours, current_time, self.offmode, self.offdays, current_date)
        advice = '  {}  current={}  desired={}'.format(self, presentstate, nextstate)
        return advice

    def correct_power_state(self, current_time, current_date=nowdate):
        """ given current time, return string describing object and present,
        desired power state, initiate on/off required to correct if present and
        desired do not match"""
        presentstate = self.get_power_state()
        nextstate = SwitchableItem._compute_recommended_power_state(presentstate, self.offhours, current_time, self.offmode, self.offdays, current_date)

        # TODO: new boto3 client each time, optimization = reuse parent class's
        toprint = "NO OP"
        if presentstate == "stopped" and nextstate == "running":
            response = boto3.client('ec2').start_instances(InstanceIds=[self.instance.id])
            toprint = "ACTION=POWERON (result={})".format(response)

        if presentstate == "running" and nextstate == "stopped":
            # note Force is default which is false
            response = boto3.client('ec2').stop_instances(InstanceIds=[self.instance.id])
            toprint = "ACTION=POWEROFF (result={})".format(response)

        correction = '  {}  current={}  desired={}\n       {}'.format(self, presentstate, nextstate, toprint)
        return correction

    def __init__(self, instance):
        self.ec2 = None
        self.name = ''
        self.logger = logging.getLogger(__name__)
        self.offhours=[]
        self.offmode = ControlTags.MODE_TOGGLE # default
        self.offdays=[]

        if instance:
            self.instance = instance

            self.tags = {}
            if instance.tags:
                for this_tag in instance.tags:
                    k = this_tag["Key"]
                    val = this_tag["Value"]
                    self.tags[k] = val
                    if k == ControlTags.TAGNAME_HOURS:
                        self.range_tag = val
                        self.offhours = ControlTags.parse_offhours(val)
                    if k == ControlTags.TAGNAME_MODE:
                        self.offmode = ControlTags.parse_offmode(val)

                    if k == ControlTags.TAGNAME_DAYS:
                        self.offdays = ControlTags.parse_offdays(val)

                    if k.lower() == 'name':
                        self.name = val

    def __str__(self):
        return "switchable({}/{}, offhours={}-{} offdays={} offmode={})".format(self.instance.id, self.name,
                        self.offhours[0].strftime("%H:%M"), self.offhours[1].strftime("%H:%M"), self.offdays, self.offmode)
