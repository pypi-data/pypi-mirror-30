from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

import steno3d


class obj(steno3d.parsers.BaseParser):                          # nopep8
    """class obj

    Parser class for Wavefront .obj ASCII object files.
    """

    extensions = ('obj',)

    unsupported = {
        'Textures': ['vt'],
        'Normals': ['vn'],
        'Free-Form Curves/Surfaces': ['cstype', 'deg', 'bmat', 'step', 'curv',
                                      'curv2', 'surf', 'parm', 'trim', 'hole',
                                      'scrv', 'sp', 'end', 'con', 'vp'],
        'Grouping': ['g', 's', 'mg', 'o'],
        'Display Attributes': ['bevel', 'c_interp', 'd_interp', 'lod',
                               'usemtl', 'mtllib', 'shadow_obj', 'trace_obj',
                               'ctech', 'stech'],
        'Old Superseded Syntax': ['fo', 'bsp', 'bzp', 'cdc', 'cdp', 'res']
    }

    def parse(self, project=None, verbose=True):
        """function parse

        Parses the .obj file provided at parser instantiation into a
        Steno3D project.

        Optional input:
            project: Preexisting Steno3D project to add .obj file components
                     to. If not provided, a new project will be created.
            verbose: Print messages and warnings during file parsing.
                     (default: True)

        Output:
            tuple containing one Steno3D project with components parsed
            from the .obj file
        """
        if project is None:
            project = steno3d.Project(
                description='Project imported from ' + self.file_name
            )
        elif not isinstance(project, steno3d.Project):
            raise steno3d.parsers.ParseError('Only allowed input for parse is '
                                             'optional Steno3D project')

        warnings = set()
        vertices = []
        points = []
        triangles = []
        segments = []

        with open(self.file_name, 'r') as f:
            if verbose:
                print('Parsing file: {}'.format(self.file_name))
            ext_line = []
            for line in f:
                try:
                    line = ext_line + line.split()
                    # Check for comment
                    if len(line) == 0 or line[0] == '#':
                        continue

                    # Check for line continuation
                    if line[-1] == '\\':
                        ext_line = line[:-1]
                        continue
                    else:
                        ext_line = []

                    # Vertex
                    if line[0] == 'v':
                        if len(line) == 5:
                            self._warn('Unsupported feature: Vertex Weight',
                                       warnings, verbose)
                        vertices.append([float(v) for v in line[1:4]])
                        continue

                    # Surface
                    if line[0] == 'f':
                        tri = [int(v.split('/')[0]) for v in line[1:]]
                        tri = [v-1 if v > 0 else v+len(vertices) for v in tri]
                        for i in range(len(tri)-2):
                            triangles.append([tri[0], tri[i+1], tri[i+2]])
                        continue

                    # Line
                    if line[0] == 'l':
                        seg = [int(v.split('/')[0]) for v in line[1:]]
                        seg = [v-1 if v > 0 else v+len(vertices) for v in seg]
                        for i in range(len(seg)-1):
                            segments.append([seg[i], seg[i+1]])
                        continue

                    # Point
                    if line[0] == 'p':
                        pnt = [int(v) for v in line[1:]]
                        pnt = [v-1 if v > 0 else v+len(vertices) for v in pnt]
                        for p in pnt:
                            points.append(vertices[p])
                        continue

                    # Unsupported features
                    for feat in self.unsupported:
                        if line[0] in self.unsupported[feat]:
                            self._warn('Unsupported feature: {}'.format(feat),
                                       warnings, verbose)
                            break
                    else:
                        self._warn(
                            'Skipping unknown keyword: {}'.format(line[0]),
                            warnings, verbose
                        )

                except:
                    raise steno3d.parsers.ParseError(
                        'Bad file line encountered while '
                        'parsing {}:\n{}'.format(
                            self.file_name,
                            ' '.join(line)
                        )
                    )

        if len(points) == 0 and len(segments) == 0 and len(triangles) == 0:
            raise steno3d.parsers.ParseError(
                'No valid geometry extracted while parsing {}.\nPlease '
                'ensure this file has vertices (v) and points (p), lines (l), '
                'or faces (f).\nOther features are currently unsupported. If '
                'you would like to contribute, visit\n'
                'https://github.com/seequent/steno3d-obj'.format(
                    self.file_name
                )
            )

        if len(segments) > 0:
            if np.min(segments) < 0 or np.max(segments) >= len(vertices):
                raise steno3d.parsers.ParseError(
                    'Invalid line geometry encountered in parsed file. '
                    'Segment indices must be between 0 and '
                    '{}'.format(len(vertices)-1)
                )
            steno3d.Line(
                project=project,
                mesh=steno3d.Mesh1D(
                    segments=segments,
                    vertices=vertices
                )
            )

        if len(triangles) > 0:
            if np.min(triangles) < 0 or np.max(triangles) >= len(vertices):
                raise steno3d.parsers.ParseError(
                    'Invalid surface geometry encountered in parsed file. '
                    'Triangle indices must be between 0 and '
                    '{}'.format(len(vertices)-1)
                )
            steno3d.Surface(
                project=project,
                mesh=steno3d.Mesh2D(
                    triangles=triangles,
                    vertices=vertices
                )
            )

        if len(points) > 0:
            steno3d.Point(
                project=project,
                mesh=steno3d.Mesh0D(
                    vertices=points
                )
            )

        if verbose and len(warnings) > 0:
            print('  If you are interested in contributing to unsupported '
                  'features, please visit\n'
                  '      https://github.com/seequent/steno3d-obj')

        return (project,)

    @staticmethod
    def _warn(warning, warnings, verbose):
        if warning in warnings:
            return
        warnings.add(warning)
        if verbose:
            print('  ' + warning)


class Wavefront(steno3d.parsers.AllParsers):
    """class Wavefront

    The Wavefront parser can be used for any Wavefront file. Currently,
    only .obj files are supported so this class is a bit redundant, and
    more for demonstration purposes of how to define a class that
    inherits AllParsers.
    """
    extensions = {
        'obj': obj
    }
