# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 1.0.9   | :white_check_mark: |


## Reporting a Vulnerability

Thanks for looking into the possible vulnerabilities of Asteval.  As we clearly state in the documentation, 
we are aiming to removing known vulnerabilities that can crash the Python program running Asteval or allow 
access to system files that the program the Asteval Interpreter cannot access.

Sadly, we have experienced a several advisories that required substantial editing.  We assume that most of 
these submission are well-intentioned, but they do demand attention from the developers.  We feel compelled 
to give guidance on these to consider when creating a security advisory for Asteval.

Please be aware of the following:

1. Asteval does not ever run on a network. It can not run over a network. It always is run by a Python process on
   a local machine that provides an asteval.Interpreter() to a user. An instance of Asteval that is exposed from
   a web service would NOT qualify, as asteval is running in a Python process on the local machine. That Python
   process may give access to the filesystem to the user account running the web service.  These are both choices
   for how to run Asteval. If you say the Attack Vector is "Network", you will need to explain that fully.  
2. Similarly, the Asteval user is enabled by the Python process providing the Interpreter to use this software.
   If you say the Privilege Required is "None", you will need to explain that fully.  Similarly, if you say that User
   Interaction is "None" you will need to explain how a user can do anything with a Python library that does not
   require User Interaction. You should apply similar care when selecting the Scope, Confidentiality, Integrity, and
   Availability.
4. If your report describes using NumPy from within Asteval, clearly explain why this is not already covered in the
   documentation and why, "Well, then don't expose NumPy to your Asteval users" is insufficient.
   
Note that advisories about NumPy functions being able to write to the local disk are simply not issues that we intend 
to solve.  Such advisories will be closed. If having NumPy functions able to write to the local disk are a problem, 
then the user should not include NumPy in an Asteval Interpreter. 

If you believe that some aspect of Asteval's use of NumPy should be changed, then submit an Issue and/or a Pull Request.  
Issues involving NumPy are extremely unlikely to be treated as security problems.

