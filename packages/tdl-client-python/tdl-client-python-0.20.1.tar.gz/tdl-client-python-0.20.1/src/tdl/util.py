class Util:

    @staticmethod
    def compress_text(parameter):
        if not isinstance(parameter, basestring):
            return str(parameter)
        lines = str(parameter).split('\n')
        if len(lines) == 1:
            return '"{}"'.format(lines[0])
        if len(lines) == 2:
            return '"{} .. ( 1 more line )"'.format(lines[0])
        return '"{} .. ( {} more lines )"'.format(lines[0], len(lines) - 1)
