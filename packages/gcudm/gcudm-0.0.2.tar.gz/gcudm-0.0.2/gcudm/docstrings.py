#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 4/6/18
"""
.. currentmodule:: docstrings
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains utilities for setting up docstrings
"""

from .meta import ColumnMeta, COLUMN_META_ATTR, Usage, Requirement
from .modes import Modes
import inspect
from sqlalchemy import Column
import sys
from titlecase import titlecase
from typing import Any, List, Set, Tuple, Type, Union


class ModelRstFormatter(object):
    """
    This class supports a number of specialized methods for creating
    reStructuredText docstrings for classes in this project.
    """
    @staticmethod
    def simplify_docstring(s: str):
        """
        Simplify a docstring by removing leading and trailing spaces,

        :param s:
        :return:
        """
        # Make sure we're working with an actual value.
        _s = s if s is not None else ''
        # Remove leading and trailing whitespace.
        return _s.strip()

    @staticmethod
    def format_line(line: str, indent: int=1, wrap: bool=True):
        """
        Format a line of reStructuredText.

        :param line: the line to format
        :param indent: the indentation level of the formatted line
        :param wrap: Should a newline be placed at the end?
        :return: the formatted line
        """
        return '{}{}{}'.format('\t' * indent, line, '\n' if wrap else '')

    def enum2tbl(self,
                 enum_cls: Type[Union[Requirement, Usage]],
                 meta: ColumnMeta,
                 excluded: Set[Any],
                 indent: int = 1):
        # Get all of the enumerated values that aren't in the exclusion
        # set.
        vals = [v for v in enum_cls if v not in excluded]
        # Let's start off with the column specification for the table.
        colspec = f"|{'|'.join(['c'] * len(vals))}|"
        lines = [
            f'.. tabularcolumns:: {colspec}', ''
        ]
        # We're going to be formatting fixed-width text.  Let's do so with
        # three lists...
        tbl_hborders = [''] * len(vals)  # the horizontal borders
        tbl_headers = [''] * len(vals)  # the table headers
        tbl_values = [''] * len(vals)  # the values
        # Let's look at each of the values.
        for i in range(0, len(vals)):
            # We need the name.
            enum_name = vals[i].name
            # The character width of the column is the length of the name
            # plus one (1) padding space on each side.
            colwidth = (len(enum_name) + 2)
            # Now that we know the width, the border for this index can be
            # defined.
            tbl_hborders[i] = '-' * colwidth
            # Title-case the numeration name and place it in the headers
            # list at the current index.
            tbl_headers[i] = f' {titlecase(enum_name)} '
            # The yes-or-no indicator will only take up a single character,
            # but we need to pad it to maintain the fixed width.
            xo = [' '] * colwidth
            # Leaving one space on the left, put a yes-or-no indicator in
            # the column.  (We're using ASCII characters which we'll
            # replace in a moment.  For some reason, the extended characters
            # seem to pad the list with an extra space.)
            xo[1] = (
                u'Y' if meta.get_enum(enum_cls) & vals[i].value else u'N'
            )
            # Build the string.
            xos = ''.join(xo)
            # Update the string with visual symbols.
            xos = xos.replace('N', '✘')
            xos = xos.replace('Y', '✔')
            # That's the text for the values list at this index.
            tbl_values[i] = xos
        # Construct the table.
        hborder = f"+{'+'.join(tbl_hborders)}+"
        lines.append(hborder)
        lines.append(f"|{'|'.join(tbl_headers)}|")
        lines.append(hborder)
        lines.append(f"|{'|'.join(tbl_values)}|")
        lines.append(hborder)
        # Indent the entire table.
        lines = [
            self.format_line(line, indent=indent, wrap=False)
            for line in lines
        ]
        lines.append('')  # A blank line must follow the table.
        # Put it all together, and...
        rst = '\n'.join(lines)
        return rst  # ...that's that.

    def col2section(self,
                    table_name: str,
                    column_name: str,
                    meta: ColumnMeta) -> str:
        """
        Format a block of reStructuredText to represent a column.

        :param table_name: the name of the table to which the column belongs
        :param column_name: the name of the column
        :param meta: the column's meta data
        :return: a block of reStructuredText
        """
        # Start by creating an internal bookmark for the column.
        lines = [f'.. _ref_{table_name}_{column_name}:']
        # Create the name of the inline image used to represent the column.
        col_img_sub = f'img_{table_name}_{column_name}'
        # Add the image definition.
        lines.append(f'.. |{col_img_sub}| image:: _static/images/column.svg')
        lines.append(self.format_line(':width: 24px', wrap=False))
        lines.append(self.format_line(':height: 24px', wrap=False))
        lines.append('')
        # Create the heading.
        heading = f'|{col_img_sub}| **{column_name}**'
        lines.append(heading)
        lines.append('^' * len(heading))
        # Add the label.
        lines.append(self.format_line(f'**{meta.label}** - ', wrap=False))
        # Add the description.
        lines.append(self.format_line(self.simplify_docstring(meta.description)))
        # Add the table of Usage values.
        lines.append(
            self.enum2tbl(enum_cls=Usage, meta=meta, excluded={Usage.NONE},
                          indent=1))
        # Add the table of Requirement values.
        lines.append(
            self.enum2tbl(enum_cls=Requirement, meta=meta,
                          excluded={Requirement.NONE}, indent=1))

        # If the meta-data indicates there is a related NENA field...
        if meta.nena is not None:
            # ...we'll include it!
            lines.append(self.format_line(f':NENA: *{meta.nena}*'))

        # Append a blank line to separate this section from the next one.
        lines.append('')
        # Put it all together.
        rst = '\n'.join(lines)
        # Congratulations, we have a formatted reStructuredText string.
        return rst

    def cls2rst(self, cls, heading: str, preamble: str=None):
        """
        Create a docstring for a model class.

        :param cls: the class
        :param heading: the heading for the reStructuredText section
        :param preamble: everything that should preceed the generated docstring
        :return: a reStructuredText docstring
        """
        lines = ['']
        # If a preamble was supplied...
        if preamble is not None:
            # ...add it to the top.
            lines.append(preamble)
        # Figure out what we're going to call the in-line table image.
        tbl_img_sub = f'img_tbl_{cls.__name__}'
        # Define the in-line table image.
        lines.append(f'.. |{tbl_img_sub}| image:: _static/images/table.svg')
        lines.append(self.format_line(':width: 24px', wrap=False))
        lines.append(self.format_line(':height: 24px', wrap=False))
        # We need a couple of blank lines.
        lines.append('')
        lines.append('')
        # Create the heading.
        table_name_header = f'|{tbl_img_sub}| {heading}'
        lines.append('-' * len(table_name_header))
        lines.append(table_name_header)
        lines.append('-' * len(table_name_header))
        # If the class has it's own docstring...
        if cls.__doc__ is not None:
            # ...append it now.
            lines.append(cls.__doc__)
            lines.append('')
        # Now add the values.
        lines.append(self.format_line(f':Table Name: {cls.__tablename__}'))
        lines.append(self.format_line(f':Geometry Type: {cls.geometry_type()}'))
        lines.append('')  # We need a blank line.
        # We're going to go find all the members within the class hierarchy that
        # seem to be columns with metadata.
        column_members: List[Tuple[str, Column]] = []
        # Let's go through every class in the hierarchy...
        for mro in inspect.getmro(cls):
            # ...updating our list with information about all the members.
            column_members.extend(
                [
                    member for member in inspect.getmembers(mro)
                    if hasattr(member[1], COLUMN_META_ATTR)
                ]
            )
        # Eliminate duplicates.
        column_members = list(set(column_members))
        column_members.sort(key=lambda i: i[0])
        # Create the RST documentation for all the column members.
        cm_docstrings = [
            self.col2section(
                table_name=cls.__tablename__,
                column_name=cm[0],
                meta=cm[1].__meta__)
            for cm in column_members
        ]
        cm_docstring = '\n'.join(cm_docstrings)
        # Add the collected docstrings for the tables.
        lines.append(cm_docstring)
        # Put it all together...
        rst = '\n'.join(lines)
        # ...and that's a block of reStructuredText.
        return rst


def model(label: str):
    """
    Use this decorator to provide meta-data for your model class.

    :param label: the friendly label for the class
    """
    def docstring(cls):
        # We'll need a docstring formatter for this job.
        docstring_formatter = ModelRstFormatter()
        # Get the class' module.
        mod = sys.modules[cls.__module__]
        mod.__doc__ = docstring_formatter.cls2rst(
            cls=cls, heading=label, preamble=mod.__doc__)
        # Return the class.
        return cls

    def modelify(cls):
        # If the label parameter hasn't already been specified...
        if not hasattr(cls, '__label__'):
            # ...update it now.
            cls.__label__ = label
        # If we're doing a documentation run...
        if Modes().sphinx:
            # ...update the docstrings.
            docstring(cls)
        # return the original class to the caller.
        return cls

    # Return the inner function.
    return modelify

