# shazam_downloader

## About

This script fetches the latest songs you have [Shazam'd'](https://www.shazam.com/) on your account and looks for links to those songs in Deezer.

It uses  an (almost) never-expiring cookie from Shazam to list all of your Shazams, compares to a list of links it alread created, and only keeps the new songs you Shazam'd.  

[Fuzzywuzzy](https://github.com/seatgeek/fuzzywuzzy) is used to match the name of songs and authors in Shazam to find the correct version of the song and its link on Deezer.

## Usage

You will only need to do the following once since the cookie set by Shazam is used for many years

* Go to https://www.shazam.com and log into your account
* Open developper mode (Ctrl, Shift, C) and look at the cookie it created
* Copy the values for "codever" and "inid"
  * Firefox:
    * Go to the storage tab
    * On the left look at the "Cookies" and copy the value for "codever"
    * Go to the *Local Storage" and copy the value for "inid"
  * Chrome:
    * Go to "Application" tab
    * Go to Cookies and copy the value for "codever"
    * Go to "Local Storage" and cpy the value for "inid"
* Paste the two values near the top of the script where it says to
* Run the script and enjoy the links
