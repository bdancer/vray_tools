#!/usr/local/bin/python3
#
# V-Ray Python Tools
#
# http://chaosgroup.com
#
# Author: Andrei Izrantcev
# E-Mail: andrei.izrantcev@chaosgroup.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# All Rights Reserved. V-Ray(R) is a registered trademark of Chaos Software.
#

import os

if __name__ == '__main__':
    from pyparsing import Literal, CaselessLiteral, Word, Keyword
    from pyparsing import OneOrMore, ZeroOrMore, Group, Combine, Optional
    from pyparsing import alphas, nums, alphanums, quotedString, delimitedList, quotedString
    from pyparsing import restOfLine, cStyleComment
    from pyparsing import Dict
else:
    from .pyparsing import Literal, CaselessLiteral, Word, Keyword
    from .pyparsing import OneOrMore, ZeroOrMore, Group, Combine, Optional
    from .pyparsing import alphas, nums, alphanums, quotedString, delimitedList, quotedString
    from .pyparsing import restOfLine, cStyleComment


# Returns parsed description dict
#
def getPluginDesc(s,loc,toks):
    plType  = toks[0][0]
    plName  = toks[0][1]
    plAttrs = toks[0][2]

    attrs = {}
    for plAttr in plAttrs:
        attrs[plAttr[0]] = plAttr[1]

    return {
        "ID" : plType,
        "Name" : plName,
        "Attributes" : attrs,
    }

# Converters
#
to_int    = lambda s,l,t: int(t[0])
to_float  = lambda s,l,t: float(t[0])
to_list   = lambda s,l,t: tuple(t[0])
no_quotes = lambda s,l,t: t[0][1:-1]

# Generic syntax
#
lparen = Literal("(").suppress()
rparen = Literal(")").suppress()
lbrace = Literal("{").suppress()
rbrace = Literal("}").suppress()
equals = Literal("=").suppress()
semi   = Literal(";").suppress()
dot    = Literal(".")
comma  = Literal(",")
aster  = Literal("*").suppress()
minus  = Literal("-").suppress()

# Keywords
#
Color        = Keyword("Color").suppress()
AColor       = Keyword("AColor").suppress()
Vector       = Keyword("Vector").suppress()
Matrix       = Keyword("Matrix").suppress()
Transform    = Keyword("Transform").suppress()
TransformHex = Keyword("TransformHex").suppress()

List          = Keyword("List").suppress()
ListInt       = Keyword("ListInt").suppress()
ListFloat     = Keyword("ListFloat").suppress()
ListVector    = Keyword("ListVector").suppress()
ListString    = Keyword("ListString").suppress()

ListIntHex    = Keyword("ListIntHex").suppress()
ListFloatHex  = Keyword("ListFloatHex").suppress()
ListVectorHex = Keyword("ListVectorHex").suppress()
ListColorHex  = Keyword("ListColorHex").suppress()

# Values
#
nameType = Word(alphanums+"@_:|")

real    = Combine(Word(nums+"+-", nums) + Optional(dot) + Optional(Word(nums)) + Optional(CaselessLiteral("E") + Word(nums+"+-",nums))).setParseAction(to_float)
integer = Word(nums+"+-", nums).setParseAction(to_int)
number  = integer ^ real

number_range = Group(number + minus + number).setParseAction(to_list)

color  = Color  + lparen + Group(delimitedList(number)).setParseAction(to_list) + rparen + Optional(aster + number)
acolor = AColor + lparen + Group(delimitedList(number)).setParseAction(to_list) + rparen
vector = Vector + lparen + Group(delimitedList(number)).setParseAction(to_list) + rparen

matrix    = Matrix + lparen + Group(delimitedList(vector)).setParseAction(to_list) + rparen

transform = Transform + lparen + Group(matrix + comma.suppress() + vector).setParseAction(to_list) + rparen
transformHex = TransformHex  + lparen + quotedString.setParseAction(no_quotes) + rparen
tm = transform ^ transformHex

listStr    = List      + lparen + Group(Optional(delimitedList(nameType ^ acolor ^ integer ^ number))).setParseAction(to_list) + rparen
listInt    = ListInt   + lparen + Group(Optional(delimitedList(integer))).setParseAction(to_list)            + rparen
listFloat  = ListFloat + lparen + Group(delimitedList(number)).setParseAction(to_list)             + rparen
listVector = ListVector + lparen + Group(delimitedList(vector)).setParseAction(to_list) + rparen
listString = ListString + lparen + Group(quotedString.setParseAction(no_quotes)).setParseAction(to_list) + rparen

listIntHex    = ListIntHex    + lparen + quotedString.setParseAction(no_quotes) + rparen
listFloatHex  = ListFloatHex  + lparen + quotedString.setParseAction(no_quotes) + rparen
listVectorHex = ListVectorHex + lparen + quotedString.setParseAction(no_quotes) + rparen
listColorHex  = ListColorHex  + lparen + quotedString.setParseAction(no_quotes) + rparen

vectorList = listVector ^ listVectorHex
intList    = listInt    ^ listIntHex

# map_channels=List(
#     List(
#         1,
#         ListVectorHex("ZIPC6000000017000000eJxjYEAGDfYMWAGx4jA+iIawAZoWBHs="),
#         ListIntHex("ZIPC1800000015000000eJxjY2BgYAFidiBmhdIgPgAB7AAi")
#     )
# );
mapChannel = List + lparen + integer + comma.suppress() + vectorList  + comma.suppress() + intList + rparen
mapChannelsList = List + lparen + ZeroOrMore(Group(delimitedList(mapChannel))) + rparen

# instances=List(0,
#     List(0,TransformHex(""),TransformHex(""),Node),
#     List(1,TransformHex(""),TransformHex(""),Node),
#     List(2,TransformHex(""),TransformHex(""),Node)
# )
instancerItem = List + lparen + integer + comma.suppress() + tm + comma.suppress() + tm + comma.suppress() + nameType + rparen
instancerList = List + lparen + integer + comma.suppress() + ZeroOrMore(Group(delimitedList(instancerItem))) + rparen

output = nameType + Optional(Word("::") + Word(alphas+"_"))

frame = real ^ integer

interpolate_start = (Word("interpolate((") + frame + comma).suppress()
interpolate_end   = Literal("))").suppress()

# Plugin Attribute
#
attrName  = nameType

attrValue = integer ^ real ^ color ^ acolor ^ vector ^ nameType ^ output ^ quotedString.setParseAction(no_quotes)
attrValue = attrValue ^ listStr ^ listInt ^ listFloat ^ listVector ^ listString
attrValue = attrValue ^ matrix ^ transform ^ transformHex
attrValue = attrValue ^ listIntHex ^ listFloatHex ^ listVectorHex
attrValue = attrValue ^ mapChannelsList ^ instancerList
attrValue = attrValue ^ number_range

attrAnimValue = Optional(interpolate_start) + attrValue + Optional(interpolate_end)

pluginAttr = Group(attrName + equals + attrAnimValue + semi)

# Plugin
#
pluginType = Word(alphanums)
pluginName = nameType

pluginDesc = Group(pluginType + pluginName + lbrace + Group(ZeroOrMore(pluginAttr)) + rbrace).setParseAction(getPluginDesc)
pluginDesc.ignore("//"+restOfLine)
pluginDesc.ignore(cStyleComment)

# Scene
#
sceneDesc = OneOrMore(pluginDesc)
sceneDesc.ignore("//"+restOfLine)
sceneDesc.ignore(cStyleComment)

nameParser = ZeroOrMore(Group(pluginType + pluginName + lbrace))
nameParser.ignore("//"+restOfLine)
nameParser.ignore(cStyleComment)


def ParseVrscene(filepath):
    vrsceneDict = list(sceneDesc.parseString(open(filepath, "r").read()))
    vrsceneDict.append({
        "ID" : 'ImportSettings',
        "Name" : "Import Settings",
        "Attributes" : {
            'filepath' : filepath,
            'dirpath'  : os.path.dirname(filepath),
        },
    })
    return vrsceneDict


def GetMaterialsNames(filepath):
    materialPluginNames = []
    with open(filepath, "r") as f:
        for l in f:
            result = nameParser.parseString(l)
            if result:
                res = result[0]
                if res[0].startswith("Mtl"):
                    if res[1] == 'MANOMATERIALISSET':
                        continue
                    materialPluginNames.append(res[1])
    return materialPluginNames


if __name__ == '__main__':
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', nargs='?')
    args = parser.parse_args()

    vrsceneDict = ParseVrscene(args.filepath)

    for pluginDesc in vrsceneDict:
        print("Name:", pluginDesc['Name'])
        print("ID:  ", pluginDesc['ID'])
        print("Attributes:")
        pprint(pluginDesc['Attributes'], indent=4)
