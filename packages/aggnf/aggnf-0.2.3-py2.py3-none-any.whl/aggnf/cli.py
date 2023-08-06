import click
import sys

try:
    from collections import Counter
except:
    from backport_collections import Counter

from signal import signal, SIGPIPE, SIG_DFL

# We have to ignore SIGPIPE due to a BrokenPipeError being raised when the
# result is piped to head.
signal(SIGPIPE, SIG_DFL)


@click.command()
@click.argument('in_data', type=click.File('r'), default='-')
@click.option('-d', '--sep', type=str,
              help='Field delimiter. Defaults to whitespace.')
@click.option('-n', '--fieldnum', type=int,
              help='The field to use as the key, default: last field.')
@click.option('-o', '--sort', type=str, is_flag=True,
              help='Sort result.')
@click.option('-i', '--ignore-err', is_flag=True,
              help="Don't exit if field is specified and out of range.")
def cli(in_data, fieldnum, sep, sort, ignore_err):
    """Group text data based on a Nth field, and print the aggregate result.

        \b
        Works like SQL:
            `select field, count(*) from tbl group by field`

        \b
        Or shell:
            `cat file | awk '{print $NF}' | sort | uniq -c`

        \b
        Arguments:
            IN_DATA   Input file, if blank, STDIN will be used.

    """
    if fieldnum is None:
        fieldnum = -1
    elif fieldnum == 0:
        fieldnum = 1

    cnt = countfile(in_data, sep, fieldnum, ignore_err)

    if sort:
        for k in cnt.most_common():
            echoln(str(k[0]), str(k[1]))
            # click.echo("%s:\t%s" % (str(k[0]), str(k[1])))
    else:
        for k in cnt:
            echoln(str(k), str(cnt[k]))
            # click.echo("%s:\t%s" % (str(k), str(cnt[k])))


def countfile(in_data, sep, fieldnum, ignore_err):
    """Takes the input stream and does the actual counting."""
    cnt = Counter()
    i = 0
    for line in in_data:
        i += 1
        lst = line.strip().split(sep)
        try:
            cnt[lst[fieldnum]] += 1
        except IndexError:
            if ignore_err:
                continue
            click.echo('{}: Field {} is out of range at line {}'.format(
                sys.argv[0], fieldnum, i))
            exit(2)
    return cnt


def echoln(k, v):
    """Echo a formatted result line like key: count"""
    click.echo("{k: >8}: {v: <10}".format(k=k, v=v))


if __name__ == '__main__':
    cli()
