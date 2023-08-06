from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from struct import unpack

import numpy as np

import steno3d


class stl(steno3d.parsers.BaseParser):                          # nopep8
    """class stl

    Parser class for .stl stereolithography files native to CAD software
    by 3D Systems. This parser supports both ASCII and Binary stl files.
    """

    extensions = ('stl',)

    def parse(self, project=None, verbose=True):
        """function parse

        Parses the .stl file (binary or ASCII) provided at parser
        instantiation into a Steno3D project.

        Optional input:
            project: Preexisting Steno3D project to add .stl file components
                     to. If not provided, a new project will be created.
            verbose: Print messages and warnings during file parsing.
                     (default: True)

        Output:
            tuple containing one Steno3D project with components parsed
            from the .stl file
        """

        warnings = set()

        if project is None:
            project = steno3d.Project(
                description='Project imported from ' + self.file_name
            )
        elif not isinstance(project, steno3d.Project):
            raise steno3d.parsers.ParseError('Only allowed input for parse is '
                                             'optional Steno3D project')

        f = open(self.file_name, 'rb')
        first_line = f.readline().split()
        f.close()
        if len(first_line) > 0 and first_line[0] == b'solid':
            (tris, verts, title) = self._parse_ascii(verbose, warnings)
        else:
            (tris, verts) = self._parse_binary(verbose, warnings)
            title = ''

        if len(tris) == 0 or len(verts) == 0:
            raise steno3d.parsers.ParseError(
                'Invalid file. No triangles or vertices extracted.'
            )
        if np.min(tris) < 0 or np.max(tris) >= len(verts):
            raise steno3d.parsers.ParseError(
                'Invalid surface geometry encountered in parsed file. '
                'Triangle indices must be between 0 and '
                '{}'.format(len(verts)-1)
            )
        steno3d.Surface(
            project=project,
            title=title,
            mesh=steno3d.Mesh2D(
                vertices=verts,
                triangles=tris
            )
        )

        if verbose and len(warnings) > 0:
            print('  If you are interested in contributing to unsupported '
                  'features, please visit\n'
                  '      https://github.com/seequent/steno3d-stl')

        return (project,)

    def _parse_binary(self, verbose, warnings):
        """Function to parse faces and vertices from binary stl file"""

        if verbose:
            print('Parsing as binary file:\n{}'.format(self.file_name))

        f = open(self.file_name, 'rb')

        header = unpack('80s', f.read(80))[0]
        if b'COLOR' in header:
            self._warn('Unsupported feature: Solid color', warnings, verbose)
        if b'MATERIAL' in header:
            self._warn('Unsupported feature: Material', warnings, verbose)

        ntri = unpack('<I', f.read(4))[0]
        tris = np.zeros((ntri, 3)).astype(int)
        verts = []
        for n in range(ntri):
            f.read(4)  # Ignore normal vector
            f.read(4)
            f.read(4)
            for xyz in range(3):
                vert = [unpack('<f', f.read(4))[0],
                        unpack('<f', f.read(4))[0],
                        unpack('<f', f.read(4))[0]]
                try:
                    i = verts.index(vert)
                except ValueError:
                    i = len(verts)
                    verts.append(vert)
                tris[n, xyz] = i

            if unpack('<h', f.read(2))[0] != 0:
                self._warn('Unsupported feature: Facet color',
                           warnings, verbose)

        if f.read() != b'':
            self._warn('Unsupported feature: Additional content after '
                       'reading facets', warnings, verbose)
        f.close()

        return (tris, verts)

    def _parse_ascii(self, verbose, warnings):
        """Function to parse faces and vertices from ASCII stl file"""

        if verbose:
            print('Parsing as ASCII file:\n{}'.format(self.file_name))

        f = open(self.file_name, 'r')

        line = f.readline().split()
        self._check(line, 'solid')
        title = ' '.join(line[1:])
        line = f.readline().split()

        tris = []
        verts = []
        while True:
            self._check(line, 'facet')
            self._check(f.readline().split(), 'outer')

            tri = [-1, -1, -1]
            for xyz in range(3):
                line = f.readline().split()
                self._check(line, 'vertex')
                if len(line) != 4:
                    raise steno3d.parsers.ParseError(
                        '\nInvalid vertex encountered. Must have 3 components:'
                        '\n{}'.format(' '.join(line))
                    )
                vert = [float(val) for val in line[1:]]
                try:
                    i = verts.index(vert)
                except ValueError:
                    i = len(verts)
                    verts.append(vert)
                tri[xyz] = i
            tris.append(tri)

            self._check(f.readline().split(), 'endloop')
            self._check(f.readline().split(), 'endfacet')

            line = f.readline().split()
            try:
                self._check(line, 'endsolid')
                break
            except steno3d.parsers.ParseError:
                continue

        if len(f.readlines()) > 0:
            self._warn('Unsupported feature: Additional content after '
                       'first `endsolid` keyword', warnings, verbose)
        f.close()

        return (tris, verts, title)

    @staticmethod
    def _warn(warning, warnings, verbose):
        if warning in warnings:
            return
        warnings.add(warning)
        if verbose:
            print('  ' + warning)

    @staticmethod
    def _check(line, expectation):
        if len(line) == 0:
            raise steno3d.parsers.ParseError('Invalid empty line encountered')
        if line[0] != expectation:
            raise steno3d.parsers.ParseError(
                '\nInvalid line: {}\n Expected keyword {}'.format(
                    line, expectation
                )
            )
