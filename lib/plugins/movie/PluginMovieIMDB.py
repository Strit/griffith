# -*- coding: UTF-8 -*-

__revision__ = '$Id$'

# Copyright (c) 2005-2013 Vasco Nunes, Piotr OÅ¼arowski
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA

# You may use and distribute this software under the terms of the
# GNU General Public License, version 2 or later

# Edited by Peter Munch-Ellingsen and Dan Johansen
# Puplished by Dan Johansen

import gutils, movie
import string, re

plugin_name         = 'IMDb'
plugin_description  = 'Internet Movie Database'
plugin_url          = 'www.imdb.com'
plugin_language     = _('English')
plugin_author       = 'Vasco Nunes, Piotr OÅ¼arowski'
plugin_author_email = 'griffith@griffith.cc'
plugin_version      = '1.15'

class Plugin(movie.Movie):
    def __init__(self, id):
        self.encode   = 'utf-8'
        self.movie_id = id
        self.url      = "http://imdb.com/title/tt%s" % self.movie_id

    def initialize(self):
        self.cast_page = self.open_page(url=self.url + '/fullcredits')
        self.plot_page = self.open_page(url=self.url + '/plotsummary')
        self.comp_page = self.open_page(url=self.url + '/companycredits')
        self.tagl_page = self.open_page(url=self.url + '/taglines')

    def get_image(self):
        tmp = gutils.trim(self.page, '<div class="poster">', '</div>')
        image_link = gutils.trim(tmp, '<a href="', '"')
        poster_page = self.open_page(url='http://www.imdb.com' + image_link)
#        tmp = gutils.trim(poster_page, '<div class="photo">', '</div>')
        self.image_url = gutils.trim(tmp, 'src="', '"')

    def get_o_title(self):
        self.o_title = gutils.regextrim(self.page, 'class="title-extra">', '<')
        if not self.o_title:
            self.o_title = gutils.regextrim(self.page, '<h1 itemprop="name" class>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.o_title:
            self.o_title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))

    def get_title(self):    # same as get_o_title()
        self.title = gutils.regextrim(self.page, '<h1 itemprop="name" class>', '([ ]|[&][#][0-9]+[;])<span')
        if not self.title:
            self.title = re.sub(' [(].*', '', gutils.trim(self.page, '<title>', '</title>'))

    def get_director(self):
        self.director = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, '>Directed by', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                director = string.strip(string.replace(gutils.trim(part, '>', '<'), '\n', ''))
                self.director = self.director + director + ', '
            self.director = self.director[0:len(self.director) - 2]

    def get_plot(self):
        self.plot = gutils.regextrim(self.page, 'itemprop="description"', '<')
        self.plot = gutils.after(self.plot, '>')
        elements = string.split(self.plot_page, '<p class="plotpar">')
        if len(elements) < 2:
            elements = re.split('<li class="(?:odd|even)">', self.plot_page)
        if len(elements) > 1:
            self.plot = self.plot + '\n\n'
            elements[0] = ''
            for element in elements[1:]:
                if element <> '':
                    self.plot = self.plot + gutils.strip_tags(gutils.before(element, '</a>')) + '\n\n'

    def get_year(self):
        self.year = gutils.trim(self.page, '<a href="/year/', '</a>')
        self.year = gutils.after(self.year, '>')
        if not self.year:
            tmp = gutils.trim(self.page, '<title>', '</title>')
            tmp = re.search('([0-9]{4})[)]', tmp)
            if tmp:
                self.year = tmp.group(0)

    def get_runtime(self):
        self.runtime = gutils.regextrim(self.page, 'Runtime:<[^>]+>', ' min')

    def get_genre(self):
        self.genre = string.replace(gutils.regextrim(self.page, 'Genre[s]*:<[^>]+>', '</div>'), '\n', '')
        self.genre = self.__before_more(self.genre)

    def get_cast(self):
        self.cast = ''
        self.cast = gutils.trim(self.cast_page, '<table class="cast_list">', '</table>')
        if self.cast == '':
            self.cast = gutils.trim(self.page, '<table class="cast">', '</table>')
        self.cast = string.replace(self.cast, ' ... ', _(' as '))
        self.cast = string.replace(self.cast, '...', _(' as '))
        self.cast = string.replace(self.cast, "\n", '')
        self.cast = string.replace(self.cast, '</tr>', "\n")
        self.cast = self.__before_more(self.cast)
        self.cast = gutils.clean(self.cast)
        self.cast = re.sub('[ \t]+', ' ', self.cast)
        self.cast = re.sub(' \n ', '\n', self.cast)

    def get_classification(self):
        self.classification = gutils.trim(self.page, '(<a href="/mpaa">MPAA</a>)', '</div>')
        self.classification = gutils.trim(self.classification, 'Rated ', ' ')

    def get_studio(self):
        self.studio = ''
        tmp = gutils.regextrim(self.comp_page, 'name="production"', '</ul>')
        tmp = string.split(tmp, 'href="')
        if len(tmp)>1:
            for entry in tmp[1:]:
                entry = string.strip(string.replace(gutils.trim(entry, '>', '<'), '\n', ''))
                if entry:
                    self.studio = self.studio + entry + ', '
            if self.studio:
                self.studio = self.studio[:-2]

    def get_o_site(self):
        self.o_site = ''

    def get_site(self):
        self.site = "http://www.imdb.com/title/tt%s" % self.movie_id

    def get_trailer(self):
        self.trailer = "http://www.imdb.com/title/tt%s/trailers" % self.movie_id

    def get_country(self):
        self.country = '<' + gutils.trim(self.page, 'Country:<', '</div>')
        self.country = re.sub('[ ]+', ' ', re.sub('[\n]+', '', self.country))

    def get_rating(self):
#        pattern = re.compile('>([0-9]([.][0-9])*)(<[^>]+>)+[/](<[^>]+>)[0-9][0-9]<')
#        result = pattern.search(self.page)
#        if result:
#            self.rating = result.groups()[0]
#            if self.rating:
#                try:
#                    self.rating = round(float(self.rating), 0)
#                except Exception, e:
#                    self.rating = 0
        tmp = gutils.trim(self.page, '<div class="ratingValue">', '</div>')
#        image_link = gutils.trim(tmp, '<a href="', '"')
        poster_page = self.open_page(url='http://www.imdb.com')
#        tmp = gutils.trim(poster_page, '<div class="photo">', '</div>')
        self.rating = gutils.trim(tmp, '<span itemprop="ratingValue">', '</span>')
#        else:
#            self.rating = 0

    def get_notes(self):
        self.notes = ''
        language = gutils.regextrim(self.page, 'Language:<[^>]+>', '</div>')
        language = gutils.strip_tags(language)
        language = re.sub('[\n]+', '', language)
        language = re.sub('[ ]+', ' ', language)
        language = language.strip()
        color = gutils.regextrim(self.page, 'Color:<[^>]+>', '</div>')
        color = gutils.strip_tags(color)
        color = re.sub('[\n]+', '', color)
        color = re.sub('[ ]+', ' ', color)
        color = color.strip()
        sound = gutils.regextrim(self.page, 'Sound Mix:<[^>]+>', '</div>')
        sound = gutils.strip_tags(sound)
        sound = re.sub('[\n]+', '', sound)
        sound = re.sub('[ ]+', ' ', sound)
        sound = sound.strip()
        tagline = gutils.regextrim(self.tagl_page, '>Taglines', '>See also')
        taglines = re.split('<div[^>]+class="soda[^>]*>', tagline)
        tagline = ''
        if len(taglines)>1:
            for entry in taglines[1:]:
                entry = gutils.clean(gutils.before(entry, '</div>'))
                if entry:
                    tagline = tagline + entry + '\n'
        if len(language)>0:
            self.notes = "%s: %s\n" %(_('Language'), language)
        if len(sound)>0:
            self.notes += "%s: %s\n" %(gutils.strip_tags(_('<b>Audio</b>')), sound)
        if len(color)>0:
            self.notes += "%s: %s\n" %(_('Color'), color)
        if len(tagline)>0:
            self.notes += "%s: %s\n" %('Tagline', tagline)

    def get_screenplay(self):
        self.screenplay = ''
        parts = re.split('<a href=', gutils.trim(self.cast_page, '>Writing Credits', '</table>'))
        if len(parts) > 1:
            for part in parts[1:]:
                screenplay = string.strip(string.replace(gutils.trim(part, '>', '<'), '\n', ''))
                if screenplay == 'WGA':
                    continue
                screenplay = screenplay.replace(' (written by)', '')
                screenplay = screenplay.replace(' and<', '<')
                self.screenplay = self.screenplay + screenplay + ', '
            if len(self.screenplay) > 2:
                self.screenplay = self.screenplay[0:len(self.screenplay) - 2]
                self.screenplay = re.sub('[ \t]+', ' ', self.screenplay)

    def get_cameraman(self):
        self.cameraman = ''
        tmp = gutils.regextrim(self.cast_page, '>Cinematography by', '</table>')
        tmp = string.split(tmp, 'href="')
        if len(tmp) > 1:
            for entry in tmp[1:]:
                entry = string.strip(string.replace(gutils.trim(entry, '>', '<'), '\n', ''))
                if entry:
                    self.cameraman = self.cameraman + entry + ', '
            if self.cameraman:
                self.cameraman = self.cameraman[:-2]

    def __before_more(self, data):
        for element in ['>See more<', '>more<', '>Full summary<', '>Full synopsis<']:
            tmp = string.find(data, element)
            if tmp>0:
                data = data[:tmp] + '>'
        return data

class SearchPlugin(movie.SearchMovie):
    PATTERN = re.compile(r"""<a href=['"]/title/tt([0-9]+)/[^>]+[>](.*?)</td>""")
    PATTERN_DIRECT = re.compile(r"""value="/title/tt([0-9]+)""")

    def __init__(self):
        # http://www.imdb.com/List?words=
        # finds every title sorted alphabetically, first results are with a quote at
        # the beginning (episodes from tv series), no popular results at first
        # http://www.imdb.com/find?more=tt;q=
        # finds a whole bunch of results. if you look for "Rocky" you will get 903 results.
        # http://www.imdb.com/find?s=tt;q=
        # seems to give the best results. 88 results for "Rocky", popular titles first.
        self.original_url_search   = 'http://www.imdb.com/find?s=tt&q='
        self.translated_url_search = 'http://www.imdb.com/find?s=tt&q='
        self.encode                = 'utf8'

    def search(self,parent_window):
        if not self.open_search(parent_window):
            return None
        return self.page

    def get_searches(self):
        elements = string.split(self.page, '<tr')
        if len(elements):
            for element in elements[1:]:
                match = self.PATTERN.findall(element)
                if len(match) > 1:
                    tmp = re.sub('^[0-9]+[.]', '', gutils.clean(match[1][1]))
                    self.ids.append(match[1][0])
                    self.titles.append(tmp)
        if len(self.ids) < 2:
            # try to find a direct result
            match = self.PATTERN_DIRECT.findall(self.page)
            if len(match) > 0:
                self.ids.append(match[0])
            else:
                # try to look for IMDb id directly
                if len(self.title) == 7 and re.match('[0-9]+', self.title):
                    self.ids.append(self.title)


#
# Plugin Test
#
class SearchPluginTest(SearchPlugin):
    #
    # Configuration for automated tests:
    # dict { movie_id -> [ expected result count for original url, expected result count for translated url ] }
    #
    test_configuration = {
        'Rocky Balboa'         : [ 10, 10 ],
        'Ein glÃ¼ckliches Jahr' : [ 3, 3 ]
    }

class PluginTest:
    #
    # Configuration for automated tests:
    # dict { movie_id -> dict { arribute -> value } }
    #
    # value: * True/False if attribute only should be tested for any value
    #        * or the expected value
    #
    test_configuration = {
        '0138097' : {
            'title'             : 'Shakespeare in Love',
            'o_title'           : 'Shakespeare in Love',
            'director'          : 'John Madden',
            'plot'              : True,
            'cast'              : 'Geoffrey Rush' + _(' as ') + 'Philip Henslowe\n\
Tom Wilkinson' + _(' as ') + 'Hugh Fennyman\n\
Steven O\'Donnell' + _(' as ') + 'Lambert\n\
Tim McMullan' + _(' as ') + 'Frees (as Tim McMullen)\n\
Joseph Fiennes' + _(' as ') + 'Will Shakespeare\n\
Steven Beard' + _(' as ') + 'Makepeace - the Preacher\n\
Antony Sher' + _(' as ') + 'Dr. Moth\n\
Patrick Barlow' + _(' as ') + 'Will Kempe\n\
Martin Clunes' + _(' as ') + 'Richard Burbage\n\
Sandra Reinton' + _(' as ') + 'Rosaline\n\
Simon Callow' + _(' as ') + 'Tilney - Master of the Revels\n\
Judi Dench' + _(' as ') + 'Queen Elizabeth\n\
Bridget McConnell' + _(' as ') + 'Lady in Waiting (as Bridget McConnel)\n\
Georgie Glen' + _(' as ') + 'Lady in Waiting\n\
Nicholas Boulton' + _(' as ') + 'Henry Condell\n\
Gwyneth Paltrow' + _(' as ') + 'Viola De Lesseps\n\
Imelda Staunton' + _(' as ') + 'Nurse\n\
Colin Firth' + _(' as ') + 'Lord Wessex\n\
Desmond McNamara' + _(' as ') + 'Crier\n\
Barnaby Kay' + _(' as ') + 'Nol\n\
Jim Carter' + _(' as ') + 'Ralph Bashford\n\
Paul Bigley' + _(' as ') + 'Peter - the Stage Manager\n\
Jason Round' + _(' as ') + 'Actor in Tavern\n\
Rupert Farley' + _(' as ') + 'Barman\n\
Adam Barker' + _(' as ') + 'First Auditionee\n\
Joe Roberts' + _(' as ') + 'John Webster\n\
Harry Gostelow' + _(' as ') + 'Second Auditionee\n\
Alan Cody' + _(' as ') + 'Third Auditionee\n\
Mark Williams' + _(' as ') + 'Wabash\n\
David Curtiz' + _(' as ') + 'John Hemmings\n\
Gregor Truter' + _(' as ') + 'James Hemmings\n\
Simon Day' + _(' as ') + 'First Boatman\n\
Jill Baker' + _(' as ') + 'Lady De Lesseps\n\
Amber Glossop' + _(' as ') + 'Scullery Maid\n\
Robin Davies' + _(' as ') + 'Master Plum\n\
Hywel Simons' + _(' as ') + 'Servant\n\
Nicholas Le Prevost' + _(' as ') + 'Sir Robert De Lesseps\n\
Ben Affleck' + _(' as ') + 'Ned Alleyn\n\
Timothy Kightley' + _(' as ') + 'Edward Pope\n\
Mark Saban' + _(' as ') + 'Augustine Philips\n\
Bob Barrett' + _(' as ') + 'George Bryan\n\
Roger Morlidge' + _(' as ') + 'James Armitage\n\
Daniel Brocklebank' + _(' as ') + 'Sam Gosse\n\
Roger Frost' + _(' as ') + 'Second Boatman\n\
Rebecca Charles' + _(' as ') + 'Chambermaid\n\
Richard Gold' + _(' as ') + 'Lord in Waiting\n\
Rachel Clarke' + _(' as ') + 'First Whore\n\
Lucy Speed' + _(' as ') + 'Second Whore\n\
Patricia Potter' + _(' as ') + 'Third Whore\n\
John Ramm' + _(' as ') + 'Makepeace\'s Neighbor\n\
Martin Neely' + _(' as ') + 'Paris / Lady Montague (as Martin Neeley)\n\
The Choir of St. George\'s School in Windsor' + _(' as ') + 'Choir (as The Choir of St. George\'s School Windsor) rest of cast listed alphabetically:\n\
Jason Canning' + _(' as ') + 'Nobleman (uncredited)\n\
Kelley Costigan' + _(' as ') + 'Theatregoer (uncredited)\n\
Rupert Everett' + _(' as ') + 'Christopher Marlowe (uncredited)\n\
John Inman' + _(' as ') + 'Character Player (uncredited)',
            'country'           : 'USA',
            'genre'             : 'Comedy | Drama | Romance',
            'classification'    : False,
            'studio'            : 'Universal Pictures, Miramax Films, Bedford Falls Productions',
            'o_site'            : False,
            'site'              : 'http://www.imdb.com/title/tt0138097',
            'trailer'           : 'http://www.imdb.com/title/tt0138097/trailers',
            'year'              : 1998,
            'notes'             : _('Language') + ': English\n'\
+ _('Audio') + ': Dolby Digital\n'\
+ _('Color') + ': Color\n\
Tagline: ...A Comedy About the Greatest Love Story Almost Never Told...\n\
Love is the only inspiration',
            'runtime'           : 123,
            'image'             : True,
            'rating'            : 7,
            'screenplay'        : 'Marc Norman, Tom Stoppard',
            'cameraman'         : 'Richard Greatrex',
            'barcode'           : False
        },
    }
