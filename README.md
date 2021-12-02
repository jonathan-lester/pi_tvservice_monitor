# pi_tvservice_monitor
This is a simple python script which runs the Raspberry Pi tvservice, [tvservice.c](https://github.com/raspberrypi/userland/blob/master/host_applications/linux/apps/tvservice/tvservice.c), to listen for HDMI detach and attach events. It can then execute shell commands provided in a JSON file on these events. For example, the current ```config.json``` and ```magic_mirror.refreshonattach.service``` file are setup to trigger a [MagicMirror](https://github.com/MichMich/MagicMirror) weather map to update when the display powers on.

A simple systemd .service file is also provided so you can run this a systemd service that will keep itself running.

* Detach events
  * Specify the display that was detached
  * Occur when a display is powered off or the cable is unplugged
* Attach events
  * Don't specify the display that was attached
  * Occur when a display is powered on or the cable is plugged in

### Installation
Edit your ```config.json``` file to run the commands you care about. Then copy the .service file in ```/etc/systemd/system``` and use the following command (as root) to have systemd scan for changes: 
```
systemctl daemon-reload
```
Then you can check the status and start/stop the service with the following commands:
```shell
systemctl restart magic_mirror.refreshonattach.service
systemctl stop magic_mirror.refreshonattach.service
systemctl start magic_mirror.refreshonattach.service
systemctl status magic_mirror.refreshonattach.service
```

### Config.json
You can specify an arbitrary shell command specified in the config.json file for "onattach" events or "ondetach" events. The syntax is a simple key/value pair for each command. Key names must be unique. Commands must run properly with the user setup by the service and the Python invocation: ```subprocess.run( yourShellCommand, shell=True, text=True )```
```js
{
  "onattach": {
    "update_mmm": "curl --location --request GET 'http://localhost:8080/api/notification/MMM-WINDYV2REFRESH?apiKey=ReplaceWithAPIKey'",
    "cmd2": "echo 'Second command'"
  },
  "ondetach": [

  ]
}
```
Note, that the provided service file will run the script, tvservice, and the commands as root. It is recommended that you configure it to run it as a lesser privileged user add ```User=``` and ```Group=``` in the ```[Service]``` section. See this StackOverflow discussion for more details: https://askubuntu.com/a/676022

### Example tvservice -M output:
Monitoring mode output events look like:
```
[I] HDMI cable is unplugged. Display 2
[I] HDMI is attached
[I] HDMI cable is unplugged. Display 2
[I] HDMI is attached
```
