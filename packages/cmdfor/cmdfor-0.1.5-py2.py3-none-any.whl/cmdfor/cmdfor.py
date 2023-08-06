from subprocess import Popen
import os
import sys
import time


def multi_itercmd(cmd, iterable, separator=None, out_dir=None, err_dir=None,
                  err_files=False, label_field=None, ignore_missing=False,
                  threads=1):
    """
    Use mutitple concurrent threads to loop over iterable and execute a cmd for
    each iteraton.

    :param cmd:
    :param iterable:
    :param separator:
    :param out_dir:
    :param err_dir:
    :param err_files:
    :param label_field:
    :param ignore_missing:
    :param threads:
    :return:
    """
    if not threads or not isinstance(threads, int):
        threads = 1

    children = {}
    itercmd_gen = itercmd(cmd, iterable,
                          separator=separator,
                          out_dir=out_dir,
                          err_dir=err_dir,
                          err_files=err_files,
                          label_field=label_field,
                          ignore_missing=ignore_missing,
                          waitpid=False)
    for line_no, child, msg in itercmd_gen:
        if child is not None:
            child.number = line_no
            children[child.pid] = child
        yield line_no, child, msg, list(children.keys())
        # If there are no available threads, stop spawning children, and reap
        # them until at least one has exited.
        while len(children) >= threads:
            for reaped in _reapchildren(children):
                yield reaped

    # We need to do a final reap, as there could still be working children.
    for reaped in _reapchildren(children):
        yield reaped


def _reapchildren(children):
    """
    Check all <children> Popen objects in the dictionary for returncodes.

    Yield the result if they have completed.

    :param children:
    :return:
    """
    for pid in list(children.keys()):
        ret = children[pid].poll()
        if ret is None:
            continue
        msg = "child exited with %s" % ret
        yield children[pid].number, children[pid], msg, list(children.keys())
        del (children[pid])


def itercmd(cmd, iterable, separator=None, out_dir=None, err_dir=None,
            err_files=False, label_field=None, ignore_missing=False,
            waitpid=True, timeout=300):
    """
    Loop over iterable, running cmd for each iteration.

    Command arguments with .format() placeholders will be substituted with the
    corresponding field in the iteration.

    :param iterable:
    :param cmd:
    :param separator:
    :return:
    """
    # print(repr(cmd))
    if not isinstance(cmd, str if sys.version_info[0] >= 3 else basestring):
        raise InvalidCommandError(
            "command must be a string {} given".format(cmd.__class__))

    line_no = 0
    for item in iterable:
        line_no += 1

        # Checking to make sure the that the iteration is usable data.
        if isinstance(item, str if sys.version_info[0] >= 3 else basestring):
            fields = item.split(separator)
        elif hasattr(item, 'append'):
            fields = item
        elif isinstance(item, tuple):
            fields = list(item)
        else:
            raise UnknownInputError(
                'input should be string or iterable sequence '
                '{} given'.format(item.__class__))

        # Here we're emulating the intuitive field numbering scheme of other
        # shell tools such as awk, where $0 denotes the whole line, and $1
        # denotes the 1st field. This is of course less pythonic, but this is
        # meant to be used in the shell.

        if label_field is not None and label_field <= len(fields):
            if label_field > 0:
                filename = str(fields[label_field - 1]).strip()
            elif label_field == 0:
                filename = str('.'.join(fields)).strip()
            else:
                try:
                    filename = str(fields[label_field]).strip()
                except IndexError as e:
                    msg = (
                        "label field `{}` doesn't exist, {} fields total."
                    ).format(label_field, len(fields))
                    if ignore_missing:
                        yield (line_no, None, 'skipped. ' + msg)
                        continue
                    else:
                        raise FieldLabelError(msg)

        else:
            filename = 'task_{}'.format(line_no)

        # Here we handle the output behaviour for different output scenarios.
        # From the CLI, these will handle the -o -e and -E options.
        #
        # Basically, if there is an output directory, we will create a file in
        # there for everything, unless stderr is sent to another file, or
        # another directory. By default, we will suppress all output, since
        # anything sent to the shell would be pretty mangled when this is used
        # multi-threaded. (which is the intended use case)

        if out_dir is not None and str(out_dir).lower() != '/dev/null':
            out_path = os.path.join(out_dir, str(filename))
            out_filename = str(out_path) + '.out'
        else:
            out_path = None
            out_filename = '/dev/null'

        out_fh = open(out_filename, 'w')

        if err_dir is not None and str(err_dir).lower() != '/dev/null':
            err_path = os.path.join(err_dir, str(filename))
            err_filename = str(err_path) + '.err'
        elif out_path is not None and err_files:
            err_filename = str(out_path) + '.err'
        elif out_path is not None:
            err_filename = out_filename
        else:
            err_filename = '/dev/null'

        err_fh = open(err_filename, 'w')

        # Handle the formatting of the command prior to execution.
        try:
            final_cmd = cmd.format(*fields)
        except IndexError as e:
            msg = 'insufficient input fields to build command.'
            if ignore_missing:
                yield (line_no, None, 'skipped. ' + msg)
                continue
            else:
                raise FieldMismatchError(msg)

        child = Popen(final_cmd, stdout=out_fh, stderr=err_fh, shell=True)
        if waitpid:
            start = time.time()
            while (time.time() - start) < timeout:
                ret = child.poll()
                if ret is not None:
                    msg = 'process exited with %s' % ret
                    break
                else:
                    msg = 'process timed out after %s sec' % timeout
                    continue
        else:
            msg = 'process spawned'

        yield line_no, child, msg

        continue


class FieldLabelError(Exception):
    pass


class FieldMismatchError(Exception):
    pass


class UnknownInputError(Exception):
    pass


class InvalidCommandError(Exception):
    pass
