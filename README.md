![Python Version](https://img.shields.io/badge/Python-3.6-green.svg)


# MALListCreator
Written in Python 3.
Converts a text file to XML format that can be imported into MAL.
Leverages the MAL API and Google Search to obtain the anime ids.

## Usage
You first need to create a file called `login.txt` with your MAL credentials, and have it sit next to the `converter.py` script.

Your credentials should be of the form `username:password`

On the command line run `python converter <mal skeleton xml file> <anime list text file>`

The anime list text file should be formatted as `number.title`, with each series on its own line. Why? Because it was how I had my anime list.

Example:

```
12.Bleach
13.Violet Evergarden
14.SYD*
```

## Intelligence
The script has limited awareness of typical ways a user may write the series titles. There are:

- Anime title ending with *s2* will replace the s2 with just *2*
- Anime title ending with *s1* will remove the s1

Requires:
- Internet connection
- Python 3.X
- lxml (if you run python 3.6 as the default `py -3.6 -m pip install lxml`)
- BeautifulSoup4 (e.g. `py -3.6 -m pip install beautifulsoup4`)

