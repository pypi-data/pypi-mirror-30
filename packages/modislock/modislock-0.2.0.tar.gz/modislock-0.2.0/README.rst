
|logo|_


.. image:: https://badge.fury.io/py/modislock.png
    :target: https://badge.fury.io/py/modislock

==========
Modis Lock
==========

Overview
========
Modis Lock allows complete digital control over your physical security needs utilizing the latest digital security
techniques. Two-Factor-Authentication such as FIDO U2F and Google Authenticator are easily deployable over your
physical security domain.

If you are just getting started, make sure to review the **First Steps** below.

- Project Homepage: https://github.com/Modis-GmbH/ModisLock-WebAdmin
- Releases Page: https://github.com/Modis-GmbH/ModisLock-WebAdmin/releases

Capable of using anything from low-security protocols like PIN codes, RFID keys, to secure protocols such
as `Yubico <http://www.yubico.com>`_ OTP keys,
`Google Authenticator <https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2&hl=en>`_
(TOTP), and `FIDO <https://fidoalliance.org/>`_ U2F USB or NFC keys.

Security protecting governments and banks can now be used on both your PCs and the facility that houses them.

.. figure:: http://modis.io/wp-content/uploads/2017/09/Screenshot-Dashboard-1024x698.png
   :align: center
   :width: 600px

   Front end administration for the `Modis lock <http://www.modislab.com>`_. Facilitates user/key management,
   reporting as well as system settings.

Features
========
- Local validation of secure digital keys
- Multiple key protocols supported (PIN, RFID, OTP, TOTP, U2F)
- Cloud service validation for Yubico keys
- Reporting and logging for events
- Email notifications
- API for custom applications

Installation
============
Administration is installation is accomplished with few steps.

Prerequisites
-------------
A MySQL database is used to store events and user information:
``sudo apt install mysql-server``

Webserver used is Ngnix. This can be modified by the installer if needed:
``sudo apt install nginx``

Supervisor is an amazing tool that will start and re-start processes with ease:
``sudo supervisor``

**Suggested that a virtual environment is used**

.. note:: example ``virtualenv -p python3 .env``

Management install
------------------
1. ``sudo pip3 install git+https://github.com/Modis-GmbH/ModisLock-WebAdmin.git``

2. Modify the ``nginx /etc/nginx/sites-available/modis_admin`` server-name to reflect your host name and directory

3. Modify the ``/etc/supervisor/conf.d/modis_admin.conf`` file to reflect your installation directory

.. |logo| image:: http://modis.io/wp-content/uploads/2017/04/logo_100.png
   :align: middle
.. _logo: http://modis.io
