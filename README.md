# musicmp3spb.org

Python script to automatically download albums from http://musicmp3spb.org site

## Usage

#### Download all songs from the album's page:

```sh
$ musicmp3spb.py http://musicmp3spb.org/album/dualism.html
```

#### Download all albums from the band's page:

```sh
$ musicmp3spb.py -a http://musicmp3spb.org/artist/textures.html

```

## Examples

#### Download all albums from http://musicmp3spb.org/artist/intronaut.html:

```sh
[user@linux Intronaut]$ musicmp3spb.py -a http://musicmp3spb.org/artist/intronaut.html
-------------------------------------------------------------------------------
  Album "Habitual Levitations"
  http://musicmp3spb.org/album/habitual_levitations.html
-------------------------------------------------------------------------------
01-killing_birds_with_stones.mp3                11.05 of 11.05 MB [100%]
02-the_welding.mp3                              08.26 of 08.26 MB [100%]
03-steps.mp3                                    07.87 of 07.87 MB [100%]
04-sore_sight_for_eyes.mp3                      07.58 of 07.58 MB [100%]
05-milk_leg.mp3                                 09.31 of 09.31 MB [100%]
06-harmonomicon.mp3                             08.96 of 08.96 MB [100%]
07-eventual.mp3                                 09.27 of 09.27 MB [100%]
08-blood_from_a_stone.mp3                       04.25 of 04.25 MB [100%]
09-the_way_down.mp3                             12.32 of 12.32 MB [100%]
-------------------------------------------------------------------------------
  Album "Void"
  http://musicmp3spb.org/album/void_intronaut.html
-------------------------------------------------------------------------------
01-a_monumental_vulgarity.mp3                   13.71 of 13.71 MB [100%]
02-gleamer.mp3                                  12.45 of 12.45 MB [100%]
03-fault_lines.mp3                              14.69 of 14.69 MB [100%]
04-nostalgic_echo.mp3                           12.16 of 12.16 MB [100%]
05-teledildonics.mp3                            16.36 of 16.36 MB [100%]
06-iceblocks.mp3                                14.98 of 14.98 MB [100%]
07-rise_to_the_midden.mp3                       14.90 of 14.90 MB [100%]
[user@linux Intronaut]$
```

## Requirements

You need Python2 (since mechanize is not available for Pyton3) and [mechanize](https://pypi.python.org/pypi/mechanize/).

## License

[WTFPL – Do What the Fuck You Want to Public License](http://www.wtfpl.net/)

## Ports

There is a [Python 3 port](https://github.com/damsgithub/musicmp3spb-3.py) of this script using [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) instead of [Mechanize](https://pypi.python.org/pypi/mechanize/).