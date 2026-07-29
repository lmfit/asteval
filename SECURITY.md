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

Sadly, we have experienced a several advisories that needed substantial editing.  We assume that most of 
these are well-intentioned, but feel compelled to give guidance on these to consider when creating a 
security advisory for Asteval.   Please be aware of the following:

1. Asteval does not ever run on a network. It can not do so. It always is run by a Python process on a local
   machine, providing an asteval.Interpreter() to a user. That Python process may give access to the filesystem
   to the user, and it may allow the user to use NumPy.  These are both choices for how to run Asteval.  If you
   say the Attack Vector is "Network", you will need to explain that fully.   An instance of Asteval that is
   exposed as a web service would NOT qualify, as asteval is running in a Python process on the local machine.   
3. Similarly, the Asteval user *is* enabled by the Python process providing the asteval Interpreter to use this
   software.  If you say the Privilege Required is "None", you will need to explain that fully.  Similarly, if you
   say that User Interaction is "None" you will need to explain how a user can do anything with a Python library
   that does not require User Interaction.
4. You should apply similar care when selecting the Scope, Confidentiality, Integrity, and Availability.
5. If your report describes using NumPy from within Asteval, clearly explain why this is not already covered in the
   documentation and why, "Well, then don't expose NumPy to your Asteval users" is insufficient.
