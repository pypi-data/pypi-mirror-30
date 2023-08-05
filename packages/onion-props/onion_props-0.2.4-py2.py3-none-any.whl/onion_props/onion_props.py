'''
onion_props.py  ver. 0.2.4

(C) Conrad Heidebrecht (github.com/eternali) 20 March 2018

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

from collections import OrderedDict  # to cover python versions < 3.6
from datetime import datetime
import os
import time


# Should have recursive dict property values so I can parse __getitem__ properly

class Property:
    '''
    Data class containing the property value and the comments corresponding to it.

    '''

    def __init__(self, prop, comments=[]):
        self.prop = prop
        self.comments = comments[:]  # copy comments by value, not reference


class Properties:

    def __init__(self):
        self.__dict__ = OrderedDict()

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        ret = self.__dict__[key]
        if hasattr(ret, 'prop'):
            return ret.prop
        else:
            return ret

    def __contains__(self, key):
        return key in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def get(self, key):
        return self.__dict__[key]

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    # comments only apply to terminal properties (properties that are of type Property, not Properties)
    def get_comments(self, key):
        prop = self.__dict__[key]
        if hasattr(prop, 'comments'):
            return prop.comments
        else:
            raise KeyError('The requested terminal property does not exist.')

    def get_property(self, key):
        prop = self.__dict__[key]
        if type(prop) is not Properties:
            return prop
        else:
            raise KeyError('The requested terminal property does not exist.')


class PropParser:
    '''
    PropParser is a properties parser that explicitly supports hierarchical document structure.
    Levels of property hierarchy is denoted by '.' in the property name.
    For example:
        a.b = 12
        a.c=test
        d=321
    will be parsed to be available as a dictionary:
        {
            'a': {
                'b': '12',
                'c': 'test'
            },
            'd': 321
        }

    You can nest as many levels as you like, however the root property of a hierarchy must not be explicitly set.
    For example the following will raise an error:
        a = 123
        a.b = test
    This is because 'a' is initially set to an integer, but then wants to be reassigned to a dictionary.

    You can also (optionally) parse comments included in the properties file (you can customize what is parsed 
    as a comment with the COMMENT parameter in the constructor).
    Note: a line can either be a property or a comment, you cannot have an inline comments
    i.e. `a.b=123 #comment` is invalid, but
         `#comment
          a.b=123` is what you should be doing.
    If comments are included in property parsing, you can access them through the comments property,

    e.g. 

    #comment one
    a.b=123
    a.c=value
    #comment two
    b.d=number

    will be parsed as

    {
        'a': {
            'b': '123' (comments='comment one')
            'c': 'value'
        },
        'b': {
            'd': 'number (comments='comment two')
        }
    }

    To access a.b's value, nothing changes (just do properties['a']['b'] and you will get '123'),
    and to get a.b's comments, you can simply do properties['a']['b'].comments
    Note: the way comments are parsed is they are stored in the first property below it (as seen in the example)

    '''

    def __init__(self, load_file, COMMENT='#'):
        # allows for custom comment denotation
        self.COMMENT = COMMENT
        self.__properties__ = Properties()
        if load_file is not None:
            self.load(load_file)

    def __setitem__(self, key, value):
        self.__properties__[key] = value

    def __getitem__(self, key):
        return self.__properties__[key]

    def __contains__(self, key):
        return key in self.__properties__

    def load(self, filename):
        self.__properties__ = Properties()
        
        if not os.path.isfile(filename):
            return False
        
        with open(filename, 'r') as f:
            cached_comments = []
            for n, l in enumerate(f):
                line = l.rstrip(os.linesep).strip('\t')
                if line.startswith(self.COMMENT):
                    cached_comments.append(line.strip(self.COMMENT).strip(' '))
                    continue
                if len(line) < 2 or '=' not in line:
                    continue
                line = line.split('=', 1)
                key = line[0].strip()
                value = line[1].strip() if len(line) > 1 else ''
                self.__parse_prop(self.__properties__, cached_comments, key.split('.'), value)
        
        return True

    def __parse_prop(self, props, comments, keys, value):
        if keys[0] in props:
            self.__parse_prop(props[keys[0]], comments, keys[1:], value)
        elif len(keys) > 1:
            props[keys[0]] = Properties()
            self.__parse_prop(props[keys[0]], comments, keys[1:], value)
        else:
            # save the final value and reset the comments for the next property
            props[keys[0]] = Property(value, comments)
            del comments[:]

    def save(self, filename, timestamp=True, incl_comments=True):
        # formatted timestamp example: 'Sat Feb 10 16:07:17 EST 2018'
        # note datetime's strftime %Z interpolation only returns a nonempty string if
        # it is not a default zone (whatever that means), so I'm just using time.strftime's
        ts = datetime.now().strftime('%a %b %d %H:%M:%S {} %Y'.format(time.strftime('%Z')))
        filename = (os.getcwd() + os.sep if os.sep not in filename else '') + filename
        if not os.path.exists(filename.rsplit('/', 1)[0]):
            os.makedirs(filename.rsplit('/', 1)[0])

        with open(filename, 'w+') as f:
            if timestamp:
                f.write(self.COMMENT + ts + '\n')
            compiled = []
            self.__build(self.__properties__, '', compiled, incl_comments=incl_comments)
            f.write('\n'.join(compiled))

    def __build(self, prop, cur_line, compiled, incl_comments=True):
        if type(prop) in [Properties, dict]:
            for key in prop:
                try:
                    self.__build(prop.get_property(key),
                                 cur_line + ('.' if cur_line else '') + key,
                                 compiled, incl_comments)
                except (AttributeError,  KeyError):
                    self.__build(prop[key],
                                 cur_line + ('.' if cur_line else '') + key,
                                 compiled, incl_comments)
        elif type(prop) is Property:
            if incl_comments:
                compiled += [self.COMMENT + comment for comment in prop.comments]
            compiled.append(cur_line + '=' + prop.prop)
        else:
            compiled.append(cur_line + '=' + prop)

        

