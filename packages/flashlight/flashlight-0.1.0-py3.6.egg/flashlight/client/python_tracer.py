import sys


class PythonTracer:
    """ Tracer module that acts as a context manager sets and unsets sys.settrace
    and returns the traced data
    """

    def __init__(self):
        self.trace = []
        self.user_file_indices = []

    def __enter__(self):
        sys.settrace(self._trace_callback)
        return self

    def __exit__(self, type, value, traceback):
        sys.settrace(None)

    def _create_tracehistory(self, frame, why, filename):
        if why == 'call':
            code = frame.f_code
            self.trace.append((filename, code.co_name, frame.f_lineno))
        if why == "line":
            class_obj = frame.f_locals.get("self", None)
            if class_obj is not None:
                class_name = class_obj.__class__.__name__
            else:
                class_name = '<NO_CLASS_NAME>'
            self.trace.append((filename, class_name, frame.f_lineno))

    def _trace_callback(self, frame, why, arg):
        filename = frame.f_code.co_filename
        self._create_tracehistory(frame, why, filename)
        if 'lucent/' not in filename:
            if '/torch/' in filename:
                pass
            else:
                pass
            return self._trace_callback
