####################################################################
# License
####################################################################
# This file is part of Blitzprog.

# Blitzprog is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Blitzprog is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Blitzprog.  If not, see <http://www.gnu.org/licenses/>.

####################################################################
# Imports
####################################################################
import sys

####################################################################
# Functions
####################################################################
def printTraceback():
    import traceback
    traceback.print_exc()

def isVarChar(char):
    return char.isalnum() or char == '_'

def isVarChar2(stri = str, index = int):
    return index < len(stri) and (stri[index].isalnum() or stri == "_")

def isValidVarName(stri):
    for char in stri:
        if not isVarChar(char):
            return False
    return True

def startswith(stri = str, prefix = str):
    stri = stri.lower()
    prefix = prefix.lower()
    return stri.startswith(prefix) and (len(prefix) == len(stri) or stri[len(prefix)].isspace())
