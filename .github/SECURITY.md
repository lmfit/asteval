# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are currently being supported
with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.9   | :white_check_mark: |
| 1.0.10  | :white_check_mark: |


## Reporting a Vulnerability

Thanks for looking into the possible security vulnerabilities of Asteval.  As we clearly state in
the documentation, we are aiming to remove as many known vulnerabilities that can crash the Python
program running Asteval or allow access to system files that the program running the Asteval
Interpreter cannot access.

Sadly, we have experienced a very large number of reports of vulnerabilities that either required 
substantial editing or have been wrong.  Some of these submission are clearly are well-intentioned, 
but they do demand attention from the developers. For some of these submissions, it is not obvious
that they are well-intentioned. The people raising these seem much more interested in getting credit
for finding a vulnerabilty than in improving Asteval. 

If the report of a security vulnerability is your goal, we are probably not interested.  Our interest
is in using and maintaining Asteval.  We vastly prefer Issues being raised or Discussions being started 
*before* a security report is submitted.

If you are going to submit a security issue for Asteval, we feel compelled to give guidance on this.  
Please be aware of the following:

1. Asteval does not ever run on a network. It can not run over a network. It always is run by a
   Python process on a local machine that provides an asteval.Interpreter(). An instance of Asteval
   that is exposed from a web service would NOT qualify, as asteval is running in a Python process 
   on the server. If you say the Attack Vector is "Network", you will need to explain in detail why
   that is the case.  And you will probably be wrong.
3. Similarly, the Asteval user is enabled by the Python process providing the Interpreter to use
   this software.  If you say the Privilege Required is "None", you will need to explain that
   fully.  Similarly, if you say that User Interaction is "None" you will need to explain how a
   user can do anything with a Python library that does not require User Interaction. You should
   apply similar care when selecting the Scope, Confidentiality, Integrity, and Availability.
4. If your report describes using NumPy from within Asteval, clearly explain why this is not
   already covered in the documentation and why a response of, "Well, then don't expose NumPy
   to your Asteval users" is not sufficient.  The fact that NumPy may be enabbled by default is
   most definitely not sufficient.  It is exceptionally unlikely that any vulnerability that
   involves NumPy will be published.  

If your report says the Attack Vector is "Netork",  Privilege Required is "None", or the issue involves 
NumPy and you do not include a clear demonstration of why the points above do not apply, your report will 
likely be closed, and you will be pointed to this policy.  Sadly, we see far too many reports like this, 
and they time just to read and respond. If you do issue such a False report, we will have to view you 
as a troll, seeking attention and aiming to get credit for reported vulnerabilities instead of actually 
helping this project.  If you persist, we may report abuse.

On the other hand, ff you believe that some aspect of Asteval, including its use of NumPy should be changed
including to make it safer, then please submit an Issue and eventually a Pull Request. If the Issue is seen 
to be a security problem, then we will consider issuing a security notice.
