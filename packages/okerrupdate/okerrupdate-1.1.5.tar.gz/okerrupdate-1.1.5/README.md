# okerrupdate - simple interface to update okerr indicator

## Simplest 

Reads textid and secret from default config file (/etc/okerrclient.conf), updates heartbeat indicator 'test:1' with status OK. If no such indicator - creates it (if policy allows autocreate). 
~~~
#!/usr/bin/python
import okerrupdate
op = okerrupdate.OkerrProject()
i = op.indicator("test:1")
i.update('OK')
~~~


## More detailed

Sets verbose mode. Sets textid and secret from script. Creates numerical indicator and sets parameters for it, then updates it.
~~~
#!/usr/bin/python
import okerrupdate

# create okerr project
op = okerrupdate.OkerrProject('MyTextID', secret='MySecret1')
op.verbose()

# create indicator
i = op.indicator("test:1", method='numerical|maxlim=37')
i.update('36.6', 'Current temperature is normal')
~~~

