#REUSED code  from https://github.com/orgs/sanskrit for Hindi to English only.And did some addition and  deletion of code part
#This improved the mapping of Hindi to English from earlier

import six

from builtins import zip
from builtins import object

#Internal referecne variables  of Hindi and English 

HINDI = 'Hindi'

ENGLISH = 'English'

SCHEMES = {}


class Scheme(dict):

    #REUSED this same from https://github.com/orgs/sanskrit

    """Represents all of the data associated with a given scheme. In addition
    to storing whether or not a scheme is roman, :class:`Scheme` partitions
    a scheme's characters into important functional groups.
    :class:`Scheme` is just a subclass of :class:`dict`.
    :param data: a :class:`dict` of initial values.
    :param is_roman: `True` if the scheme is a romanization and `False`
                     otherwise.
    """

    def __init__(self, data=None, is_roman=True):
        super(Scheme, self).__init__(data or {})
        self.is_roman = is_roman
        
class SchemeMap(object):

    #REUSED this same from https://github.com/orgs/sanskrit

    """Maps one :class:`Scheme` to another. This class grabs the metadata and
    character data required for :func:`transliterate`.
    :param from_scheme: the source scheme
    :param to_scheme: the destination scheme
    """

    def __init__(self, from_scheme, to_scheme):
        """Create a mapping from `from_scheme` to `to_scheme`."""
        self.marks = {}
        self.virama = {}

        self.vowels = {}
        self.consonants = {}
        self.other = {}
        self.from_roman = from_scheme.is_roman
        self.to_roman = to_scheme.is_roman
        self.longest = max(len(x) for g in from_scheme
                           for x in from_scheme[g])

        for group in from_scheme:
            if group not in to_scheme:
                continue
            sub_map = {k: v for (k, v) in zip(from_scheme[group],
                                              to_scheme[group])}
            if group.endswith('marks'):
                self.marks.update(sub_map)
            elif group == 'virama':
                self.virama = sub_map
            else:
                self.other.update(sub_map)
                if group.endswith('consonants'):
                    self.consonants.update(sub_map)
                elif group.endswith('vowels'):
                    self.vowels.update(sub_map)


def _roman(data, scheme_map, **kw):

    #REUSED this same from https://github.com/orgs/sanskrit

    """Transliterate `data` with the given `scheme_map`. This function is used
    when the source scheme is a Roman scheme.
    :param data: the data to transliterate
    :param scheme_map: a dict that maps between characters in the old scheme
                       and characters in the new scheme
    """
    vowels = scheme_map.vowels
    marks = scheme_map.marks
    virama = scheme_map.virama
    consonants = scheme_map.consonants
    other = scheme_map.other
    longest = scheme_map.longest
    to_roman = scheme_map.to_roman

    togglers = kw.pop('togglers', set())
    suspend_on = kw.pop('suspend_on', set())
    suspend_off = kw.pop('suspend_off', set())
    if kw:
        raise TypeError('Unexpected keyword argument %s' % list(kw.keys())[0])

    buf = []
    i = 0
    had_consonant = found = False
    len_data = len(data)
    append = buf.append

    # If true, don't transliterate. The toggle token is discarded.
    toggled = False
    # If true, don't transliterate. The suspend token is retained.
    # `suspended` overrides `toggled`.
    suspended = False

    while i <= len_data:
        # The longest token in the source scheme has length `longest`. Iterate
        # over `data` while taking `longest` characters at a time. If we don`t
        # find the character group in our scheme map, lop off a character and
        # try again.
        #
        # If we've finished reading through `data`, then `token` will be empty
        # and the loop below will be skipped.
        token = data[i:i + longest]

        while token:
            if token in togglers:
                toggled = not toggled
                i += 2  # skip over the token
                found = True  # force the token to fill up again
                break

            if token in suspend_on:
                suspended = True
            elif token in suspend_off:
                suspended = False

            if toggled or suspended:
                token = token[:-1]
                continue

            # Catch the pattern CV, where C is a consonant and V is a vowel.
            # V should be rendered as a vowel mark, a.k.a. a "dependent"
            # vowel. But due to the nature of Brahmic scripts, 'a' is implicit
            # and has no vowel mark. If we see 'a', add nothing.
            if had_consonant and token in vowels:
                mark = marks.get(token, '')
                if mark:
                    append(mark)
                elif to_roman:
                    append(vowels[token])
                found = True

            # Catch any other character, including consonants, punctuation,
            # and regular vowels. Due to the implicit 'a', we must explicitly
            # end any lingering consonants before we can handle the current
            # token.
            elif token in other:
                if had_consonant:
                    append(virama[''])
                append(other[token])
                found = True

            if found:
                had_consonant = token in consonants
                i += len(token)
                break
            else:
                token = token[:-1]

        # We've exhausted the token; this must be some other character. Due to
        # the implicit 'a', we must explicitly end any lingering consonants
        # before we can handle the current token.
        if not found:
            if had_consonant:
                append(virama[''])
            if i < len_data:
                append(data[i])
                had_consonant = False
            i += 1

        found = False

    return ''.join(buf)


#I have changed the the _brahmic function as per my requirement of transliterate script 
#Specially to remove extra A in the end of each tranliterated word 

def _brahmic(data, scheme_map, **kw):
    """Transliterate `data` with the given `scheme_map`. This function is used
    when the source scheme is a Brahmic scheme.
    :param data: the data to transliterate
    :param scheme_map: a dict that maps between characters in the old scheme
                       and characters in the new scheme
    """
    marks = scheme_map.marks
    virama = scheme_map.virama
    consonants = scheme_map.consonants
    other = scheme_map.other
    to_roman = scheme_map.to_roman

    buf = []
    had_consonant = False
    append = buf.append
    for L in data:
        #print(L,len(L))
        if L in marks:
            append(marks[L])
            #print('marks')
            #print(marks[L])
        elif L in virama:
            append(virama[L])
            #print('virama')
            #print(virama[L])
        else:
            #print('1',+ had_consonant)
            #print(L1,len(L1))
            if had_consonant and L != ' ':
                append('A')
                #print('A')
            append(other.get(L, L))
            #print(other.get(L, L))
        had_consonant = to_roman and L in consonants
        #L1 = L
        #print('2',+ had_consonant)
        #print(L,L1)
    #print('3',+ had_consonant)
    #if had_consonant:
    #    append('A')
    return ''.join(buf)



#I had changed the the _brahmic function as per my requirement of transliterate script 

def transliterate(data, _from=None, _to=None, scheme_map=None, **kw):
    
    #Chnaged the mapping of Hindi to English characters as per my understanding  of matter 
    #Also, added other consanants,vowels & marks from DEVANAGARI 

    """Transliterate `data` with the given parameters::
        output = transliterate('idam adbhutam', HK, DEVANAGARI)
    Each time the function is called, a new :class:`SchemeMap` is created
    to map the input scheme to the output scheme. This operation is fast
    enough for most use cases. But for higher performance, you can pass a
    pre-computed :class:`SchemeMap` instead::
        scheme_map = SchemeMap(SCHEMES[HK], SCHEMES[DEVANAGARI])
        output = transliterate('idam adbhutam', scheme_map=scheme_map)
    :param data: the data to transliterate
    :param _from: the name of a source scheme
    :param _to: the name of a destination scheme
    :param scheme_map: the :class:`SchemeMap` to use. If specified, ignore
                       `_from` and `_to`. If unspecified, create a
                       :class:`SchemeMap` from `_from` to `_to`.
    """
    if scheme_map is None:
        from_scheme = SCHEMES[_from]
        to_scheme = SCHEMES[_to]
        scheme_map = SchemeMap(from_scheme, to_scheme)

    options = {
        'togglers': set(['##']),
        'suspend_on': set('<'),
        'suspend_off': set('>')
    }
    options.update(kw)

    func = _roman if scheme_map.from_roman else _brahmic
    return func(data, scheme_map, **options)


def _setup():
    """Add a variety of default schemes."""
    s = six.text_type.split

    SCHEMES.update({
       HINDI: Scheme({
            'vowels': s("""अ आ इ ई उ ऊ ऋ ॠ ऌ ॡ ऍ ए ऐ ऑ ओ औ"""),
            'marks': s("""ा ि ी ु ू ृ ॄ ॢ ॣ े ै ो ौ"""),
            'virama': s('्'),
            'other': s('ं ः ँ'),
            'consonants': s("""
                            क ख ग घ ङ
                            च छ ज झ ञ
                            ट ठ ड ढ ण
                            त थ द ध न
                            प फ ब भ म
                            य र ल व
                            श ष स ह
                            ळ क्ष ज्ञ त्र ब् श्
                            """),
            'symbols': s("""
                       ॐ ऽ । ॥
                       ० १ २ ३ ४ ५ ६ ७ ८ ९
                       """)
            }, is_roman=False),
        ENGLISH: Scheme({
            'vowels': s("""A AA I EE U OO R RR LR LRR E E AI O O AU"""),
            'marks': s("""A I EE U OO R RR lR lRR E AI O AU"""),
            'virama': [''],
            'other': s('N H N'),
            'consonants': s("""
                            K KHA G GH R
                            CH CHH J JH N
                            TT TTH DD DDH N
                            T TH D DH N
                            P PH B BH M
                            Y R L V
                            SH SH S H
                            LL KSH GY TR B S
                            """),
            'symbols': s("""
                       OM ' | ||
                       0 1 2 3 4 5 6 7 8 9
                       """)
        })
    })

_setup()
