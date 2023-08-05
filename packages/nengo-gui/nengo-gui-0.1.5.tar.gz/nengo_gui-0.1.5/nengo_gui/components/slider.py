import numpy as np
import struct
import collections

from nengo_gui.components.component import Component

class Slider(Component):
    config_defaults = dict(max_value=1, min_value=-1, 
                           **Component.config_defaults)

    def __init__(self, node):
        super(Slider, self).__init__()
        self.node = node
        self.base_output = node.output
        self.override = [None] * node.size_out
        self.last_time = None
        self.value = np.zeros(node.size_out)
        self.start_value = np.zeros(node.size_out, dtype=float)
        self.struct = struct.Struct('<%df' % (1 + node.size_out))
        self.data = collections.deque()
        if not callable(self.base_output):
            self.start_value[:] = self.base_output

    def attach(self, page, config, uid):
        super(Slider, self).attach(page, config, uid)
        self.label = page.get_label(self.node)

    def add_nengo_objects(self, page):
        self.node.output = self.override_output

    def remove_nengo_objects(self, page):
        self.node.output = self.base_output

    def override_output(self, t, *args):
        if self.last_time is None or t < self.last_time:
            self.override = [None] * self.node.size_out
        self.last_time = t
        if callable(self.base_output):
            self.value[:] = self.base_output(t, *args)
            self.data.append(self.struct.pack(t, *self.value))
        else:
            self.value[:] = self.base_output

        for i, v in enumerate(self.override):
            if v is not None:
                self.value[i] = v
        return self.value

    def javascript(self):
        info = dict(uid=id(self), n_sliders=len(self.override),
                    label=self.label,
                    start_value=[float(x) for x in self.start_value])
        json = self.javascript_config(info)
        return 'new Nengo.Slider(main, sim, %s);' % json


    def update_client(self, client):
        while len(self.data) > 0:
            data = self.data.popleft()
            client.write(data, binary=True)

    def message(self, msg):
        index, value = msg.split(',')
        index = int(index)
        if value == 'reset':
            self.override[index] = None
        else:
            value = float(value)
            self.override[index] = value

    def code_python_args(self, uids):
        return [uids[self.node]]
