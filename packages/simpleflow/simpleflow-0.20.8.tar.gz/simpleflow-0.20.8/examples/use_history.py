#!/usr/bin/env python
import ipdb
import json

from swf.models import History as BaseHistory
from simpleflow.history import History

raw = open("examples/analysis_171527__22xPGMLVq45Yq23cA3buAHbl89PNVfVz9OCXwB%2BERvAAs%3D.json").read()
events = json.loads(raw)["events"]
events = sorted(events, key=lambda x: x["eventId"])

# raw history from "swf" module
base_history = BaseHistory.from_event_list(events)

# simpleflow history
history = History(base_history)
history.parse()

ipdb.set_trace()
