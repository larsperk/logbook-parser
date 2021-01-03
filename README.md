# logbook-parser
This project takes an exported logbook file from ForeFlight and adds flight distances to each flight.

It is tuned to my own needs and does a bunch of cleanup of typos and changed airport IDs (see "trans_dict" variable; you can edit this for your own needs,
or simply make it an empty dictionary)

It also takes multi-segment flights (KJFK-KLAX-KJFK) that were entered as a single entry and parsees them into individual segments,
reallocating all flight time variables (PIC, X-country, IMC, dual given, dual received, night) proportionaly based on the flight segment distance
as a percentage of total flight distance - This may not be appropriate, but then again, it's more accurate than leaving it lumped together.

3 letter alpha-only airport IDs are prepended with a "K", those with numbers in them (e.g. "9B1") aren't. 

You'll need to edit the input filename to reflect the name of the Foreflight export.

Use carefully and at your own risk - before importing back into ForeFlight carefully chack the logbook-output.csv for accuracy.

ALWAYS KEEP A BACKUP OF YOUR ORGINAL FOREFLIGHT EXPORT SO YOU CAN REVERT IF YOU DON"T LIKE WHAT COMES OUT

