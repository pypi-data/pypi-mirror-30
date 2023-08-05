import click
from termcolor import colored
from s3_restore import *
from s3_empty_bucket import *
from s3_scan_key_perms import *
from __init__ import *

@click.group()
@click.version_option()
def cli():
    """This is your s3 friend(bro), that will help you with bucket iterations.
    Try:\n
    \b
    # s3bro restore --help
    # s3bro purge --help
    # s3tk --help
    
    For more help or detailed information please check:
    https://github.com/rsavordelli/s3bro
    https://pypi.org/project/s3bro/
    
    """
    pass


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@cli.command()
@click.argument('restore', nargs=-1)
@click.option('--bucket', '-b', type=str, help='bucket name', required=True)
@click.option('--prefix','-p', type=str, help=' prefix', default='')
@click.option('--days', '-d', type=int, help='Days to keep the restore', required=True)
@click.option('--type', '-t', type=click.Choice(['Standard', 'Expedited', 'Bulk']), help='restore type (Tier)', required=True)
@click.option('--versions/--no-versions','-v', default=False, help='[--no-versions is DEFAULT] - this option will make the restore to include all versions excluding delete markers')
@click.option('--update-restore-date/--do-not-update-restore-date', '-urd', default=False, help='If passed, it will change the restore date for already restored key')
@click.option('--include', '-in', type=str, multiple=True, help='Only restore keys that matches with a given string, you can add multiples times by passing --include multiple times')
@click.option('--exclude', '-ex', type=str, multiple=True, help='Do not restore if key name matches with a given pattern,'
                                  'you can add multiple patterns by inputting')
@click.option('--workers', type=int, help='How many helpers to include in task, default is 10', default=10)
@click.option('--log-level', type=click.Choice(['INFO', 'ERROR', 'DEBUG', 'WARNING']), help='logging type', default='ERROR')
def restore(restore, bucket, prefix, days, type, versions, update_restore_date, workers, include, exclude, log_level):
    if type == "Expedited":
        print(colored('Note: ', 'yellow') + "Expedited requests will likely be throttled. If you want to avoid this please check: ")
        click.echo('https://docs.aws.amazon.com/AmazonS3/latest/dev/restoring-objects.html#restoring-objects-expedited-capacity')
        click.echo(30*'=')
    loglevel(log_level)
    collect_keys(restore, bucket, prefix, days, type, versions, update_restore_date, workers, include, exclude)


@cli.command()
@click.argument('purge', nargs=-1)
@click.option('--bucket','-b', type=str, help='Bucket name', required=True)
@click.option('--prefix', '-p', type=str, default='', help='prefix name - optional')
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to wipe the bucket?', help="first confirmation")
@click.option('--yes-really', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt="I'm going to delete everything in your bucket, are you really sure?", help="second confirmation")
@click.option('--log-level', type=click.Choice(['INFO', 'ERROR', 'DEBUG', 'WARNING']), help='logging type', default='ERROR')
def purge(purge, bucket, prefix, log_level):
    loglevel(log_level)
    clean_bucket(bucket, prefix)


@cli.command()
@click.argument('scanperms', nargs=-1)
@click.option('--bucket','-b', type=str, help='Bucket name', required=True)
@click.option('--prefix', '-p', type=str, default='', help='prefix name - optional')
@click.option('--bucket-level-only', '-bl', is_flag=True, help="Only scan at bucket level")
@click.option('--object-level-only', '-ol', is_flag=True, help="Only scan object level")
@click.option('--workers', type=int, help='How many helpers to include in task, default is 10', default=10)
@click.option('--log-level', type=click.Choice(['INFO', 'ERROR', 'DEBUG', 'WARNING']), help='logging type', default='ERROR')
def scanperms(scanperms, bucket, prefix, workers, log_level, bucket_level_only, object_level_only):
    loglevel(log_level)
    if bucket_level_only:
        get_bucket_permission(bucket)
    else:
        scan_key_perms(scanperms, bucket, prefix, workers, object_level_only)


