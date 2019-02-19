# -*- coding: utf-8 -*-

import click
import psutil
import time
from psutil import NoSuchProcess
from attrdict import AttrDict


@click.command()
@click.argument("pid", type=int)
def main(**kwargs):
    """Deamon script for watching webdriver's back, it will kill all
    sub-processes it spawned after webdriver exitted.

    PID: WebDriver's PID
    """

    kwargs = AttrDict(kwargs)

    wdp = psutil.Process(kwargs.pid)

    # Get the children tree, so we could kill them if webdriver not clean
    # exited.
    children = wdp.children(recursive=True)

    while True:
        time.sleep(5)

        click.echo("Check webdriver status ...")

        try:
            if wdp.status() not in [
                psutil.STATUS_STOPPED,
                psutil.STATUS_ZOMBIE,
                psutil.STATUS_DEAD,
            ]:
                continue
        except NoSuchProcess:
            pass

        if psutil.pid_exists(kwargs.pid):
            continue

        def on_terminate(proc):
            click.echo(
                "Process %s terminated with exit code %s"
                % (proc, proc.returncode)
            )

        for p in children:
            try:
                p.terminate()
            except:
                # Try our best to do jobs, but if something happened, we won't
                # let it break us.
                pass

        gone, alive = psutil.wait_procs(
            children, timeout=10, callback=on_terminate
        )
        for p in alive:
            click.echo("Process %s killed after timeout." % p)
            try:
                p.kill()
            except:
                # We don't care if it really killed.
                pass

        break


if __name__ == "__main__":
    main()
