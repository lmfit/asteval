class Module:
    def __init__(self, name, interp, filename):
        self.name = name
        self.__name__ = name
        self.__asteval__ = interp
        self.filename = filename
        self.frames = []

    def push_frame(self, frame):
        self.frames.append(frame)

    def pop_frame(self):
        assert len(self.frames) > 2
        return self.frames.pop()

    def get_current_frame(self):
        assert len(self.frames) > 0
        return self.frames[-1]

    def get_global_frame(self):
        assert len(self.frames) > 1
        return self.frames[1]

    def get_builtins_frame(self):
        assert len(self.frames) > 0
        return self.frames[0]

    def find_frame_by_id(self, _id):
        for f in self.frames:
            if f.get_id() == _id:
                return f  # make defensive copy?

    def set_symbol(self, name, val):
        self.get_current_frame().set_symbol(name, val)

    def __getattr__(self, item):
        for frame in reversed(self.frames):
            if frame.is_symbol(item):
                val = frame.get_symbol_value(item)
                return val

    def __repr__(self):
        return "<Module {}: fn={}, frames={}>".format(self.name, self.filename, self.frames)

    def __str__(self):
        return repr(self)
