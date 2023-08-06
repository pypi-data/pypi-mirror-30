LRZ Sync+Share Library
----------------------

This little library makes it easy to upload and manage files on LRZ Sync+Share.

Usage::

    from lrz_sync_share import lrz_session

    lrz = lrz_session("username", "password", "ldap")
    lrz.login()

    lrz.upload("share", "a.txt")
    url = lrz.get_link("share", "a.txt")


Shibboleths
===========
For the third parameter for ``lrz_session(user, password, shibboleth)`` use the following shibboleths:

============================================== ===============================================================
Establishment                                  Shibboleth
============================================== ===============================================================
Gastkennungen/Guests/Extern                    ldap
Akademie der Bildenden Künste                  ldap
Akademie für Politische Bildung                ldap
BAdW LRZ WMI                                   ldap
Hochschule München                             ldap
Hochschule Weihenstephan-Triesdorf             ldap
LMU München                                    ldap
TU München                                     ldap
Hochschule Kempten                             https://syncandshare.lrz.de/Shibboleth.sso/Login?SAMLDS=1&target=https%3A//syncandshare.lrz.de/login/shibboleth&entityID=https%3A//idp.hs-kempten.de/idp/shibboleth
Hochschule Neu-Ulm                             https://syncandshare.lrz.de/Shibboleth.sso/Login?SAMLDS=1&target=https%3A//syncandshare.lrz.de/login/shibboleth&entityID=https%3A//sso.hs-neu-ulm.de/idp/shibboleth
Hochschule Rosenheim                           https://syncandshare.lrz.de/Shibboleth.sso/Login?SAMLDS=1&target=https%3A//syncandshare.lrz.de/login/shibboleth&entityID=https%3A//idp.fh-rosenheim.de/idp/shibboleth
Ostbayerische Technische Hochschule Regensburg https://syncandshare.lrz.de/Shibboleth.sso/Login?SAMLDS=1&target=https%3A//syncandshare.lrz.de/login/shibboleth&entityID=https%3A//sso.hs-regensburg.de/idp/shibboleth
Universität Passau                             https://syncandshare.lrz.de/Shibboleth.sso/Login?SAMLDS=1&target=https%3A//syncandshare.lrz.de/login/shibboleth&entityID=https%3A//sso.uni-passau.de/idp/shibboleth
============================================== ===============================================================


TODO
====
* Editing filenames
* Deleting files
* Creating directories
* Creating root folders

etc., basically full web functionality


