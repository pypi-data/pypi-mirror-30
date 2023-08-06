
Gpxity is a Python - library making it easy to move activities between different backends.
In this context, a backend is a place where activities can be stored.

Implemented backends are:

  * Directory          for .gpx files on an accessible file system
  * ServerDirectory    suited for a server implementation
  * MMT                for activities on http://mapmytracks.com
  * GPSIES             for activities on https://gpsies.com

Sometimes you might just change a harmless thing like the description but
the backend does not allow changing this separately, so we have to re-upload
the whole activity. If it is is big and the remote server slow, this might
take 10 minutes or more. Right now this library has no asynchronous interface,
so it can really take some time until your program continues.



