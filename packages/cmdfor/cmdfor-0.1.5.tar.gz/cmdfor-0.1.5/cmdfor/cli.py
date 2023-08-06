import click
import cmdfor


@click.command()
@click.argument('command', type=str, nargs=-1)
@click.option('input_data', '-i', '--input', type=click.File('r'), default='-',
              help="Input data. File or STDIN.")
@click.option('-d', '--separator', type=str, default=None,
              help='Input field delimiter. Default: consecutive whitespace.')
# TODO: Add proper quoted CSV parsing
# @click.option('-c', '--csv', is_flag=True,
#               help="Input is a csv file with optional quotes.")
@click.option('-o', '--out-dir', default=None,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True),
              help='The directory in which to write each commands stdout.')
@click.option('-e', '--err-dir', default=None,
              type=click.Path(exists=True, file_okay=False, dir_okay=True,
                              writable=True, resolve_path=True),
              help='The directory in which to write each commands stderr. '
                   '(Implies -E)')
@click.option('-E', '--err-files', is_flag=True,
              help='Write stderr to different files than stdout.')
@click.option('-t', '--threads', type=int, default=1,
              help='How many concurrent commands to run.')
@click.option('-l', '--label-field', type=int, default=None,
              help="Use an input field the filename for output files. By "
                   "default, the line number of the input is used.")
@click.option('-I', '--ignore-missing', is_flag=True,
              help='Continue anyway when there is not enough data fields for '
                   'the command. This line will be skipped, and a message '
                   'printed to stderr.')
# TODO: Custom formatter class to substitute missing fields.
# @click.option('-I', '--ignore-substitute', type=str, default=None,
#               help='Continue when there is not enough data fields for '
#                    'the command. Substitute missing fields with <str>.')
@click.option('-v', '--verbose', is_flag=True,
              help="Print some verbose output to stdout.")
def cli(command, input_data, separator=None, out_dir=None, err_dir=None,
        err_files=False, threads=1, label_field=None, ignore_missing=False,
        verbose=False):
    """
    Run a CMD FOR every line of <input>

    <input> can be either STDIN or a file.

    Examples:

        \b
        cat files.txt | cmdfor rm

        \b
        cat users_passwords.csv | cmdfor -d, -- login -u {} -p {}

    """
    cmd_str = str(' '.join(command))

    # click can't specify a multi-positional argument that also requires at
    # least one, so we will check for the lack of a command here.
    if not command:
        msg = "No command specified!\nSee --help for more info."
        click.echo(msg, err=True)
        exit(3)

    itercmd_gen = cmdfor.multi_itercmd(cmd_str, input_data, separator, out_dir,
                                       err_dir, err_files, label_field,
                                       ignore_missing, threads)
    try:
        number = 1  # set the number before loop in case the first iter fails
        for number, child, msg, childpids in itercmd_gen:
            pid = child.pid if child is not None else 'None'
            msg = 'task: {}, pid: {}, {} ({} working)'.format(
                number, pid, msg, str(len(childpids))
            )
            click.echo(msg)
    except cmdfor.FieldMismatchError as e:
        msg = (
            "Command field count does not match input field count at line:"
            " {}\nUse -i to ignore.\nSee --help for more info.\n"
            " error({})"
        ).format(number, e.message)
        click.echo(msg, err=True)
        exit(4)
    except cmdfor.FieldLabelError as e:
        msg = (
            "Missing label field from input on line: {}\n"
            " error({})"
        ).format(number, e.message)
        click.echo(msg, err=True)
        exit(5)
    except cmdfor.UnknownInputError as e:
        msg = (
            "Couldn't understand the input at line: {}\n"
            " error({})"
        ).format(number, e.message)
        click.echo(msg, err=True)
        exit(6)
    except Exception as e:
        msg = (
            "runtime error on line: {}\n"
            " error({})"
        ).format(number, e.message)
        click.echo(msg, err=True)
        exit(6)

    exit(0)


if __name__ == '__main__':
    cli()
