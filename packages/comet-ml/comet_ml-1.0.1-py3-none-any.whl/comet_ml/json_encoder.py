# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************

import json


class NestedEncoder(json.JSONEncoder):
    '''
    A JSON Encoder that converts floats/decimals to strings and allows nested objects
    '''

    def default(self, obj):
        if obj.__class__.__name__ == "float32":
            return self.floattostr(obj)
        elif obj.__class__.__name__ == "type":
            return str(obj)
        elif hasattr(obj, 'repr_json'):
            return obj.repr_json()
        else:
            return json.JSONEncoder.default(self, obj)

    def floattostr(self,
                   o,
                   _inf=float('Inf'),
                   _neginf=-float('-Inf'),
                   nan_str="None"):
        if o != o:
            return nan_str
        else:
            return o.__repr__()
