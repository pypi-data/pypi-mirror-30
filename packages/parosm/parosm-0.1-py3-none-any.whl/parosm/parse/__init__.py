"""
Exposes parsers for osm files
"""

from parosm.parse.parsexml import XMLParser
from parosm.parse.parsepbf import PBFParser


__all__ = ('XMLParser', 'PBFParser')
