
# oathguardian: one-time password (TOTP/HOTP) generator


Oathguardian is a GTK-3 graphical tool for generating
[Time-based one-time password](https://en.wikipedia.org/wiki/Time-based_One-time_Password_algorithm)
as defined in [RFC6238](https://tools.ietf.org/html/rfc6238). Those one-time passwords are frequently
used as a two-factory authentication mechanism, by using a smartphone application such as 
[Google authenticator](https://en.wikipedia.org/wiki/Google_Authenticator).

Oathguardian permits to store the key secret either in a
[secret service](https://specifications.freedesktop.org/secret-service) such as Gnome Keyring ; or into a
[Yubikey 4](https://www.yubico.com/products/yubikey-hardware/yubikey4/). The yubikey is an USB device that has many
security-related usages, such as storing a PGP private key, or doing TOTP/HOTP computations.

## Screenshot

![oathguardian screenshot](https://framagit.org/avaiss/oathguardian/raw/master/docs/img/oathguardian_capture.png "OathGuardian main window")

## Installation

For now the best way to install oathguardian is to use pip.

The following instructions describe how to install oathguardian on a debian system, and should be transposable
to any other linux distribution.

### Dependencies

Some dependencies have to be installed beforehand:

```shell
$ sudo apt install python3-pip
$ sudo apt install libzbar0
$ sudo apt install pcscd libpcsclite-dev swig
```


### oathguardian

```shell
$ pip3 install --user oathguardian
```

### Post-installation

The main executable, `oathguardian-gtk` will be automatically installed into `$HOME/.local/bin`. If this path
is not currently in your `PATH` variable, please add it by adding to your `$HOME/.profile`:

    PATH="$PATH:$HOME/.local/bin"

## Licence

Oathguardian is released under the
[original ISC license](https://cvsweb.openbsd.org/cgi-bin/cvsweb/src/share/misc/license.template?rev=HEAD), as used by
[OpenBSD](https://www.openbsd.org) project.

