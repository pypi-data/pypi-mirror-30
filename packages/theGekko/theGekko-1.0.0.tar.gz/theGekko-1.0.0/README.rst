Gekko
==========

--------------
Installation
--------------
::

  $ sudo apt-get update && sudo apt-get install -y python3 python3-pip
  $ sudo pip3 install thegekko

---------------------
Enable tab-complete
---------------------
Add the content of this_ to ~/.bashrc. Then,

.. _this: https://github.com/CYRO4S/Gekko/blob/master/tab-complete/gekko_tc

::

  $ source ~/.bashrc


-------------
Quick Start
-------------
Add files or directories you don't want to sync.
::

  $ gekko camo venv/
  Checking for venv/... Exist.
  /home/me/gekkotest/.gekkoign saved.

Set up SFTP connection.
::

  $ gekko grip root@myserver.com:/root/gekkotest-remote -s MyServer
  Host:             myserver.com
  SSH Port:         22
  User:             root
  Upload Directory: /root/gekkotest-remote
  Remark:           MyServer

  Connection Saved.

Set up SFTP connection using a rsa key and specify the ssh port.
::

  $ gekko grip root@myserver.com:/root/gekkotest-remote -s MyServer -p 1080 -k ~/.ssh/id_rsa
  Host:             myserver.com
  SSH Port:         1080
  User:             root
  Upload Directory: /root/gekkotest-remote
  Remark:           MyServer
  Private key:      /home/ice/.ssh/id_rsa

Check for changes.
::

  $ gekko sense MyServer -p P@ssw0rd
  Connecting to myserver.com... Connected.
  Checking for /root/gekkotest-remote... Exist.
  Changes will be taken:
  * /root/gekkotest-remote/app.py
  + /root/gekkotest-remote/assets/logo.png
  Disconnecting... Done.

  0.102 MB need to upload.

Sync using password. Add "-f" if you want to a full sync.
Full sync will erase remote folder and re-upload local files.
::

  $ gekko run MyServer -p P@ssw0rd -r
  Connecting to myserver.com... Connected.
  Make directory at /root/gekkotest-remote... Skipped.
  Change directory to /root/gekkotest-remote... Done.
  Ignored:   .gekkoign
  Uploading: app/main/views.py... Done.
  Uploading: app/templates/index.html... Done.
  Skipped:   app/templates/old.html
  Ignored:   venv/lib/python3.5/site.py
  ......
  Ignored:   venv/pip-selfcheck.json
  Skipped:   oldone.txt
  Uploading: requirements.txt... Done.
  Uploading: manager.py... Done.
  Reserved:  db.py
  Disconnecting... Done.

----------
Commands
----------
* camouflage (camo) : Define a file or a directory which will be ignored when uploading. This will generate '.gekkoign' file.
* grip (gp) : Create a host which files will be uploaded to. You can also save the host or remove it.
* list (ls) : Show all the connections.
* remove (rm) : Remove a connecion.
* sense (ss) : Check for the changes which will taken in uploading.
* run (rn) : Start the upload sequence.
* version (ver) : Show Gekko version.
