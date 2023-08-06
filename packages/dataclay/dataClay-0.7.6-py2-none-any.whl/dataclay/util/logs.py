import json


class JSONFormatter(object):
    """Simple JSON formatter for the logging facility."""
    def format(self, obj):
        """Note that obj is a LogRecord instance."""
        # Copy the dictionary
        ret = dict(obj.__dict__)

        # Perform the message substitution
        args = ret.pop("args")
        msg = ret.pop("msg")
        ret["message"] = msg % args

        # Dump the dictionary in JSON form
        return json.dumps(ret)
