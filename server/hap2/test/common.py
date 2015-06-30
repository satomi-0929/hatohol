def assertNotRaises(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception:
        raise

def returnPrivObj(instance, obj_name, class_name=None):
    if class_name is None:
        class_name = instance.__class__.__name__
    return eval("instance._"+class_name+obj_name)

class TraceableTestCommon:
    def __init__(self):
        self.stores = {"trace":[]}

    def ensure_connection(self):
        self.stores["trace"].append("ensure_connection")

    def collect_hosts_and_put(self):
        self.stores["trace"].append("collect_host_and_put")

    def collect_host_groups_and_put(self):
        self.stores["trace"].append("collect_host_groups_and_put")

    def collect_host_group_membership_and_put(self):
        self.stores["trace"].append("collect_host_group_membership_and_put")

    def collect_triggers_and_put(self, fetch_id=None, host_ids=None):
        self.stores["trace"].append("collect_triggers_and_put")
        self.stores["fetch_id"] = fetch_id
        self.stores["host_ids"] = host_ids

    def collect_events_and_put(self, fetch_id=None, last_info=None, count=None,
                               direction=None):
        self.stores["trace"].append("collect_events_and_put")
        self.stores["fetch_id"] = fetch_id
        self.stores["last_info"] = last_info
        self.stores["count"] = count
        self.stores["direction"] = direction
