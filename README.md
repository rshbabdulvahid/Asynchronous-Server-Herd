# Asynchronous-Server-Herd
Script written in Python and is used to instantiate a single server (one of five).

"The overarching intent of this project was as follows: given a 
client and a herd of servers, implement a system such that the 
client can communicate geographic information via TCP to 
one member of the herd and get a request serviced by another 
member of the herd, irrespective of which server initially 
received the required information. This lends itself well to an 
asynchronous event-loop for a couple of reasons. Firstly, the 
propagation of information from one server to the rest is 
suited for an asynchronous framework, as the chain of events 
in a propagation may vary based on naturalistic factors. 
Secondly, client requests can be dynamic, sent to one server at 
one point and then quickly to another server at a different 
point: it makes sense that dynamic request sequences be mirrored 
in a server proxy that is equally dynamic"

Project was created in order to investigate asynchronous programming and evaluate
its efficacy for the purposes of this pet project (a miniature server herd). 
More details are given in report.pdf
