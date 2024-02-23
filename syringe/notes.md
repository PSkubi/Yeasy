## Manual notes:
- baud rate &rarr; 19200 standard, if too noisy try lower rate, need to add option to GUI to change this
- can network multiple pumps &rarr; adresses are important, default address is 0, pumps will ignore commands if it is not sent to their address
- pump will not accept communications until current command is processed
- know command is finished when you get a response from the syringe
- every command received by a pump in the network is acknowledged by the pump with a
response packet that includes a status character indicating the current operational state of
the pump

## What we're gonna program:
- baud rate can be set overall, but can also be specified in the specific command
- queue jobs &rarr; add jobs, remove jobs
- need a queue for each pump