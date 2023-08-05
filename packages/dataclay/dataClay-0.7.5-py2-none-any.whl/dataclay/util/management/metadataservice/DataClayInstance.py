from dataclay.util.MgrObject import ManagementObject

    
class DataClayInstance(ManagementObject):
    _fields = ["dcID",
               "name",
               "host",
               "port",
               ]

    _internal_fields = []
