Changelog
=========

1.2.6 (current)
---------------

Released: 2018-03-27

  * example include fixed

  * stylistic updates and code cleanup


1.2.5
-----

Released: 2018-03-27

  * lotz of linting - almost everything fixed complying to pylint3

  * renamed gpg module to gpgtool due to namespace restrictions


1.2.4
-----

Released: 2018-03-27

  * fixed filerotate not copying file modes as well

  * fixed encrypt function when setting recipients via user environment
    variables (GPGKEY/GPGKEYS) only

  * fixed creating a new password crypt file from scratch

  * minor cleanup in gpg module

  * added example files in addition to README and --help

  * fixed some obsolete info in README


1.2.3
-----

Released: 2018-03-22

  * some minor bugfixes to comply with new executor features (bytes, input)

  * fixed unintended executions when using TAB in a shell

  * some cosmetics for `pwcli --help` message

  * reimplemented the timer for remote access & sync to prevent unnecessary
    connection delays (if remote is used -R or config file)

  * another fix for executors byte2string feature - the default is to encode
    input strings and decode output strings what broke gpgsm en/decryption

  * [W] fixed scp put/get for windows (skipped instead of rising exceptions)


1.2.2
-----

Released: 2018-03-22

  * merged updates for executor subprocess forker to accept input and be able
    to return stdout as byte-string

  * removed unnecessary library iface from net

  * fixed ssh.put/get function if no scp available

  * fix for gpg socket location changed in newer releases - should also comply
    with older versions as well


1.2.1
-----

Released: 2018-03-18

  * [W] fixed some wrong path concatenations

  * another few lib fixes merged

  * fixed wrong current version in changelog


1.2.0
-----

Released: 2018-03-18

  * [L] fixed paramiko scp not working any more (replaced by subprocess call)

  * added file rotation for passcrypt file

  * cleanup of unused imports and libraries

  * removed unnecessary read/write actions on passcrypt

  * class GPGSMTool added to interact wit gpgsm for openssl compatibility


1.1.12
------

Released: 2017-12-12

  * fixed typo in system.which function changed to comply for windows

  ** hotfix release **


1.1.11
------

Released: 2017-12-11

  * [W] fix gpg.exe not found by system.which function

  * trying to fix some password input - gpg related issues

  * changed README file a bit for windows installation

  ** still some work todo for implementing gpg-key generating functionality **


1.1.10
------

Released: 2017-11-17

  * correcture on last release date :P

  * reverted which and gpg module *yet another hotfix release*


1.1.9
-----

Released: 2017-11-17

  * reverted system.user.whoami module to last commit *hotfix release*


1.1.8
-----

Released: 2017-11-16

  * fixed TypeError if password is an integer

  * fixed alot of stuff in gpg and passcrypt module for key-gen function
    to comply to gui mode as well

  * cleaned up remains of submodule merges


1.1.7
-----

Released: 2017-11-13

  * fixed key-gen dialog in cli and gui mode

  * fixed gpg-findkey function in secret-key-mode to not ask for password

  * fixed lotz of stuff in gpg wrapper for correctly collecting user input

  * merged almost all modules back into master and cleaned up pwclip branch

  * added xgetpass module and removed character hiding in xinput module

  * rearranged build environment with git-submodules


1.1.6
-----

Released: 2017-11-06

  * fixed issue where existing gpg-keys would not be recognised

  * fixed some message typos

  * continued implementing key-gen function when secret-key is missing


1.1.5
-----

Released: 2017-11-05

  * fixed date in changelog and other documentation fails from last release

  * fixed secret key listing requires password

  * still working on generating gpg-key functionality (slomo)


1.1.4
-----

Released: 2017-11-04

  * hotfix release for failed last upload


1.1.3
-----

Released: 2017-11-04

  * fixed some changelog entrys and release date of last release in changelog

  * fixed which function to return only absolute paths


1.1.2
-----

Released: 2017-11-01

  * [W] added missing wget dependency for gpg4win installation

  * [W] fix download & install gpg4win in gui mode

  * [W] fixed gpg2.exe was used in some cases (gpg2 does not work on windows)

  * added changelog entry for the last release

  * implementing key-gen dialog if no secret-keys found
    (incomplete & unapplied)


1.1.1
-----

Released: 2017-10-24

  * [W] fix for readline import not working on windows

  * made input readline compatible if on linux


1.1.0
-----

Released: 2017-10-12

  * replaced the gpg4win binary hack by wget (with internet connectivity) as
    dependencies

  * IMHO this is no micro change so directly bumping to next minor version


1.0.5
-----

Released: 2017-09-08

  * [W] hotfix - readded __gpg4win__.py


1.0.4
-----

Released: 2017-09-08

  * fixed depreicated link to nowhere in README

  * linted again - fixed lots of things


1.0.3
-----

Released: 2017-09-08

  * [W] fixed using wrong PATH delimiter for which on windows

  * [W] implemented question if gpg4win is not installed (install on "yes")

  * [W] fixed hard coded gpg2.exe path (replaced by which function as well)

  * fixed missing [W] tags in a few previous changelog messages

  * first "whole in one" release


1.0.2
-----

Released: 2017-09-08

  * [W] made lib.system.which windows compatible (hopefully)

  * [W] fix for non-generic installed gpg4win installation recovery


1.0.1
-----

Released: 2017-09-07

  * [W] trying to implement gpg4win installation on windows systems

  * removed depricated installation desclaimer/links


1.0.0
-----

Released: 2017-08-27

  * final version bumper


0.4.43
------

Released: 2017-08-27

  * finally fixed the last issue about windows command box displaying

  * removed printing messages on gui errors (just exit returning 1)

  * some i/o related changes without logical relevance

  * displaying one more changelog message


0.4.42
------

Released: 2017-08-27

  * fixed setting sys.path in __init__.py for windows compatibility

  * trying to fix command box showup on windows

  * linted the whole code - so lots of changes, some just stylistically,
    others where errors in syntax or even logical (see git diff for details)

  * (still) preparing final version :P


0.4.32-41
---------

Released: 2017-08-25

  * [W] hotfix release for gpg binary path selection

  * w00ht @ dev-environemnt - linux/windows dev/testing can be very... intense

  * made changelog => readme generic via __pkginfo__.py

  * [W] fixed colortext (disabled colors)

  * fixed changelog not beeing displayed ... again

  * fixed displying of changelog while program exec

  * fixed unnecessarily asking for passphrase


0.4.31
------

Released: 2017-08-25

  * hotfix release for gui calls

  * readded work revoked unintensionally

  * fixed yubico mode and ykclip gui


0.4.30
------

Released: 2017-08-25

  * made reading configs somewhat more modular

  * made gui function accepting option for (pw/yk)mode switching

  * made yubikey challenge-response mode behave correctly

  * changed names of binaries to pwcli(cmdline), pwclip(gui), ykclip(gui)


0.4.29
------

Released: 2017-08-25

  * removed empty password check and info

  * added pwclip-gui to "provides" section in __pkginfo__.py

  * hotfix release (fixing password-prompter)


0.4.28
------

Released: 2017-08-25

  * fixed password-search function on cmdline

  * reimplemented gui function for pwclip-gui executable

  * fixed program exit when forked to not endup in stack-dump

  * fixed gpg decrypt iterator to begin with 0

  * fighting gpg-agent (passphrase remember) to comply to my pass-prompter

  * [W] fixed non-sence printing of colored text (no colors on windows)

  * preparing final version (it's getting serious :D)


0.4.27
------

Released: 2017-08-23

  * [W] hotfix for clipboard paste function to return objects correctly

  * implemented -S to set the slot number of the yubikey used which is
    only relevant for the challenge-response functionality (-y)

  * added a "Troubleshooting" section to README on fixing yubico-usb-hid-bug

  * (still) preparing final version


0.4.26
------

Released: 2017-08-22

  * changed entry-points to match reverted names - trying to find correct
    exec mode for windows

  * cleanup of build environment - preparing final version


0.4.25
------

Released: 2017-08-21

  * [W|O] changed copy & paste functions to handle modes correctly

  * [W] lots of fixed for xlib functions to set focus correctly

  * [W] fixed catching/setting password (no password-agent for now)

  * reverted seperation of gui and cli

  * some classes are renamed to fit the intension


0.4.24
------

Released: 2017-08-21

  * [W] fixed I/O error wich occours when setting gpg to utf-8 on gpg4win

  * [W] fixed path errors and other platform related stuff

  * seperated gui from cli via entry-points (experimental)


0.4.20-23
---------

Released: 2017-08-16

  * fixed README location

  * fixed release date of last release

  * some documentation updates


0.4.19
------

Released: 2017-08-15

  * merged private libs into ./lib - many changes related to that
    lib respectivly:
    - ./lib/net:
     -- ssh.py module updated to match paramiko changes and some other fixes
     -- added functions to do DNS lookups for the (optional) scp backup
        function
    - ./lib/secrecy/gpg.py
     -- fixed passing of command line setting of gpg-key-recipient option
     -- [W] fixed path to gnupg home
     -- [W] fixed setting wrong keystores (.gpg|.kbx) in windows
     -- [W] replaced concatenated string by path.join
     -- [W] added passphrase input mode while pinentry is not available
    - ./lib/secrecy/passcrypt.py
     -- if debugging is enabled the plaintext file is removed no more
    - ./__init__.py
     -- fixed comment for strange lib include
     -- changed wrapper to gereric name


0.4.18
------

Released: 2017-07-23

  * hotfix release

  * some documentation fixes

  * [W] fixed receiving clipboard content


0.4.17
------

Released: 2017-07-23

  * committed the changes for the last release :P

  * changelog file updated


0.4.16
------

Released: 2017-07-23

  * fixed dependency to psutil

  * removed printing of debugging output & fixed some syntax and indentation
    errors

  * [W] environment error fixed (USER => USERNAME)

  * [W] gi import error fixed (no xnotify on windows)


0.4.15
------

Released: 2017-07-21

  * readded last 3 changelog messages wich where mistakenly removed completley
    from the README.rst file

  * keeping the last 3 changelog messages in the README.rst file while the
    complete changelog is moved to a seperate CHANGELOG.rst file


0.4.14
------

Released: 2017-07-21

  * moved the changelog section from the README.rst to this CHANGELOG.rst file

  * some typo & formatting fixes in changelog

  * [W] minor path-join fix


0.4.13
------

Released: 2017-05-25

  * minor fix in disclaimer ``\`` => ``\\``

  * made some performance improvements

  * minor overall fixes

  * [L] fixed fileage checking if remote option is used


0.4.12
------

Released: 2017-03-17

  * hotfix for import without correct library path

  * fixed some obvious flaws...


0.4.11
------

Released: 2017-03-16

  * hotfix for the command line parsing which did not honor the absence of the
    -l option with- and without arguments corretly

  * added missing release dates for the last few relases in the changelog

  * split up the remote and use-remotes options

  * [L] remote can be set in the config file ~/.config/pwclip.conf


0.4.10
------

Released: 2017-03-16

  * implemented option for sftp backup of passcrypt using paramiko (optional)

  * fixed countless bugs in pwclip itself as well as within its local
    dependencies

  * pylinted the whole code - now there are 3 recommendations left (ignoring
    my indentation style etc.)

  * [L] added my pylintrc to make pylint tests reproducible

  * [L] fixed xnotification bug which made pwclip crash if it cannot use
    notifications

  * [L] removed xsel logging (even if it anyways doesn't log clip-contents)


0.4.9
-----

Released: 2017-01-26

  * [L] hotfix for the clipboard copy function which i've damaged in 0.4.8

  * [L] fixed bug regarding xsel to not have it running in background forever

  * fixed mode switch (introduced for linux) on other os's clips


0.4.8
-----

Released: 2017-01-07

  * [L] bunch of optimisations for the linux clip library regarding
    the copy function which now is able to save into PRIMARY and CLIPBOARD
    instead of PRIMARY only.

  * [W] made some success on gpg4win but still does not work for our thing

  * some other things i've forgotten inbetween wich is caused by the fact
    that i've mistakenly released 0.4.7

  * implemented scp functionality to optionally mirror the passcrypt to some
    scp-compatible server and access it from more than one machine.


0.4.7
-----

Released: 2017-01-04

 * beginning to tag linux related stuff within the changelog with [L],
   windows entrys with [W] and OSX related ones with [O] if they are related
   to that topic only

 * fixed minor "try: except:" statement issues

 * code cleanup, misspelling corrections & some other minor fixes

 * renamed cypher library to secrecy while that better matches it's intension

 * [W] continued windows implementation and again left it unfinished - gpg4win
   only supports gpg-2.0 keys what made me confused using it with
   gpg-2.1-made-keys which is incompatible when using ed25519-keys

 * [W] ran into python-gnupg bugs where gpg signals have not been catched
   (unsure if that is compromising somehow anyways)

 * [W] implementing gpg4win giving me a hard time while many issues appear
   which do not exists under linux regarding the libraries libusb and yubico
   and PATH related issues as gpg4win does not use C:\Users\%USER% as home
   directory for the personal .gnupg folder and so on...


0.4.6
-----

Released: 2016-11-24

 * added compatibility for gpg on windows (assuming gpg4win installed)

 * fixed a few bugs on windows regarding input & copy/paste things but even
   so could not get it to work finally

 * again stolen code from pyperclip regarding windows & osx clips

 * added credits for pyperclip which i (shame on me) have forgotten untill now

 * fixed password input on false input by correctly raising exceptions


0.4.5
-----

Released: 2016-11-21

 * fixed bug if not having a .passcrypt file already
   (workaround would have been `touch ~/.passcrypt`)

 * fixed bug when pressing ESC in yubi-mode - now inserts empty string hash

 * fixed bug when pressing ESC in gpg-mode - now error-exits with appropriate
   error-message (if on terminal)

 * added example .pwd.yaml file to explain a bit how pwclip is ment to work

 * updated the above explanation a bit

 * i feel like this is the first real, more or less, stable version ;D


0.4.4
-----

Released: 2016-10-28

* implemented the named but forgotten timer option

* implemented gpg-agent restart function while that agent tends to fuck around

* now there is an error message displayed in gpg-mode without an existing yaml
  and passcrypt file (if both don't exist

* fixed I/O issue where empty passcrypt was written (now double-checking)

* fixed some argparse related issues (timer settings corrected)

* fixed notification timer to be displayed as long as the password is stored

* fixed crash on blank search pattern input in gpg-mode


0.4.3
-----

Released: 2016-10-28

* bunch of documentation corrections to fit the below implementations


0.4.2
-----

Released: 2016-10-27

* fixed many issues caused by changes/implementations of v0.4.1

* fixed many search and listing issues caused by laziness (who ever did this)

* added another cmdline switch to not have passwords replaced by asterisks (*)
  which is now default for output on terminals

* fixed greedly matching entrys (if lenght of entered search pattern is < 2)

* added restriction of at least 2 caracters for each user, password and
  comment for not breaking the above greedly matching search fix


0.4.1
-----

Released: 2016-10-27

* python2 support is now discontinued (dependency differences are nasty)

* implemented command line argument parsing including help

* stylistic updates regarding cmdline output and passcrypt management

* fixed another bunch of bugs around the GUI for user input

* fixed empty gpg-passphrase usage (keys without passphrases are used anyways)

* fixed user input which was repeatedly asking for input on escape/cancle

* fixed error if no ~/.passcrypt file was found

* fixed some issues with adding/changing/deleting passwords from passcrypt

* fixed bugs caused by merging build environment development branch


0.4.0
-----

Released: 2016-10-26

* implemented PIN/Passphrase input gui for GPG decryption

* fixed many I/O encryption/decryption on-the-fly issues

* merged monolithic code into smaller files for better modularity/compliance

* some stylistic updates/fixes


0.3.3
-----

Released: 2016-10-22

* final release of pwclip with new function and documentation


0.2.6 - 0.3.2
-------------

Released: 2016-10-22

* minor documentation fixes (playing around with rst formatting)


0.2.5
-----

Released: 2016-10-22

* seperated the code into submodules within lib/ to be more compliant to my
  usual environment

* added complete new en/decryption mode via python3-gnupg - now it's capable
  of selecting gpg-keys by GPGKEYS environment variable to en/decrypt
  ~/.passcrypt

* documentation updated and cleanup on typo/irrelevant text

* FIXED: issue where the gpg-agent isn't able decrypt without passphrase/pin
  and clould not ask for it
