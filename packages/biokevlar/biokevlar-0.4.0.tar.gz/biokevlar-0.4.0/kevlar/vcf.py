#!/usr/bin/env python
#
# -----------------------------------------------------------------------------
# Copyright (c) 2018 The Regents of the University of California
#
# This file is part of kevlar (http://github.com/dib-lab/kevlar) and is
# licensed under the MIT license: see LICENSE.
# -----------------------------------------------------------------------------

import sys
import kevlar


class Variant(object):
    """Base class for handling variant calls and no-calls."""

    def __init__(self, seqid, pos, refr, alt, **kwargs):
        """
        Constructor method.

        The `pos` parameter expects the genomic position as a 0-based index.
        Setting the `refr` or `alt` parameters to `.` will designate this
        variant as a "no call".
        """
        self._seqid = seqid
        self._pos = pos
        self._refr = refr
        self._alt = alt
        self.info = dict()
        for key, value in kwargs.items():
            self.annotate(key, value)

    @property
    def seqid(self):
        return self._seqid

    @property
    def position(self):
        return self._pos

    @property
    def vcf(self):
        """Print variant to VCF."""
        attrstr = '.'
        if len(self.info) > 0:
            kvpairs = list()
            for key in sorted(self.info):
                if key != 'QS':
                    kvpairs.append(self.attribute(key, pair=True))
            queryseq = self.attribute('QS', pair=True)
            if queryseq:
                kvpairs.append(queryseq)
            attrstr = ';'.join(kvpairs)

        filterstr = 'PASS' if self._refr != '.' else '.'
        return '{:s}\t{:d}\t.\t{:s}\t{:s}\t.\t{:s}\t{:s}'.format(
            self._seqid, self._pos + 1, self._refr, self._alt, filterstr,
            attrstr
        )

    @property
    def cigar(self):
        return self.attribute('CG')

    @property
    def window(self):
        """
        Getter method for the variant window.

        The "variant window" (abbreviated `VW` in VCF output) is the sequence
        interval in the proband contig that encompasses all k-mers overlapping
        the variant.

        GCCTAGTTAGCTAACGTCCCGATCACTGTGTCACTGC
                    .....A
                     ....A.
                      ...A..
                       ..A...
                        .A....
                         A.....
                         |        <-- position of variant
                    [---------]   <-- variant window, interval (inclusive)
                                      encompassing all 6-mers that overlap the
                                      variant
        """
        return self.attribute('VW')

    @property
    def windowlength(self):
        window = self.window
        if window is None:
            return 0
        return len(window)

    @property
    def refrwindow(self):
        """Similar to `window`, but encapsulating the reference allele."""
        return self.attribute('RW')

    def annotate(self, key, value):
        if key in self.info:
            if isinstance(self.info[key], set):
                self.info[key].add(value)
            else:
                oldvalue = self.info[key]
                self.info[key] = set((oldvalue, value))
        else:
            self.info[key] = value

    def attribute(self, key, pair=False):
        if key not in self.info:
            return None
        value = self.info[key]
        if isinstance(value, set):
            value = ','.join(sorted(value))
        value = value.replace(';', ':')
        if pair:
            keyvaluepair = '{:s}={:s}'.format(key, value)
            return keyvaluepair
        else:
            return value

    @property
    def genotypes(self):
        gt = self.attribute('GT')
        if not gt:
            return None
        return tuple(gt.split(','))


class VariantSNV(Variant):
    def __str__(self):
        return '{:s}:{:d}:{:s}->{:s}'.format(self._seqid, self._pos,
                                             self._refr, self._alt)


class VariantIndel(Variant):
    def __str__(self):
        """
        Return a string representation of this variant.

        The reason that 1 is added to the variant position is to offset the
        nucleotide shared by the reference and alternate alleles. This position
        is still 0-based (as opposed to VCF's 1-based coordinate system) but
        does not include the shared nucleotide.
        """
        pos = self._pos + 1
        if len(self._refr) > len(self._alt):
            dellength = len(self._refr) - len(self._alt)
            return '{:s}:{:d}:{:d}D'.format(self._seqid, pos, dellength)
        else:
            insertion = self._alt[1:]
            return '{:s}:{:d}:I->{:s}'.format(self._seqid, pos, insertion)
