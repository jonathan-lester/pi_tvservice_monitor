"""Use the tvservice -M callback to run commands when a monitor is powered on/off (or attached/detached)

Subprocess code modeled after https://github.com/tomashapl/kodi/blob/master/service.hyperion_control/main.py
tvservice -M output looks like:
    Starting to monitor for HDMI events
    [I] HDMI cable is unplugged. Display 2
    [I] HDMI is attached
    [I] HDMI cable is unplugged. Display 2
    [I] HDMI is attached
    Shutting down...
"""

import subprocess
import re
import json
import os
import argparse
import logging
try:
    # Optional "rich" log formatter:
    from rich.logging import RichHandler
    
    FORMAT = "%(message)s"
    logging.basicConfig(
        level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
    log = logging.getLogger("rich")
except ImportError:
    log = logging.getLogger()

try:
    # Optional "rich" tracebacks and inspect/pprint for debugging:
    from rich.traceback import install
    from rich import inspect
    from rich import pretty
    from rich.pretty import pprint
    pretty.install() # Color all output
    install(show_locals=True)
except:
    log.warning( f"Rich tracebacks unavailable")


parser = argparse.ArgumentParser()
parser.add_argument('-c','--config_file', type=str, dest='config_file', help='Path and filename of the JSON configruation file', required=True)

def tvservice_loop(config):
    # Run tvservice in monitor mode, and redirect stderr to stdout
    # https://github.com/raspberrypi/userland/blob/master/host_applications/linux/apps/tvservice/tvservice.c
    # tvservice_callback prints to LOG_INFO which is sent to stderr
    process = subprocess.Popen( 'tvservice -M',
        shell=True,
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE )
    log.info("Tvservice monitor running, waiting for new events")

    while True:
        output = process.stdout.readline()
        output = output.decode("utf-8").strip()
        log.info( f"tvservice event recieved: '{output}'")
        
        if output == "" and process.poll() is not None:
            log.error( f"tvservice has exited with status '{process.returncode}'")
            log.error( "Exiting")
            exit(-1)

        if output:
            if re.search("attached", output):
                log.info( "Monitor attached")
                if 'onattach' in config and isinstance(config['onattach'],dict):
                    for k,v in config['onattach'].items():
                        log.info( f" onattach run '{k}' with command '{v}'")
                        subprocess.run( v, shell=True, text=True )
            if re.search("unplugged", output):
                log.info( "Monitor unplugged")
                if 'ondetach' in config and isinstance(config['ondetach'],dict):
                    for k,v in config['ondetach'].items():
                        log.info( f" ondetach run '{k}' with command '{v}'")
                        subprocess.run( v, shell=True, text=True )

        # Uncomment to debug:
        # import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    # Load the set of commands to run when a screen is turned on/off from JSON file
    args = parser.parse_args()
    inputFilename = os.path.abspath(os.path.expanduser(args.config_file))
    if not os.path.isfile(inputFilename):
        log.error( f"Config JSON file not found: '{inputFilename}'")
        exit(-1)

    log.info( f"Loading config from file: '{inputFilename}'")
    with open(inputFilename) as f:
        config = json.load(f)

    tvservice_loop(config)
