# -*- coding: utf-8 -*-

import os.path
import re
from datetime import date, datetime

import numpy as np
from numpy.testing import assert_array_almost_equal, assert_array_equal
from nose.tools import ok_, eq_, raises

from galvani import MPTfile, MPRfile
from galvani.BioLogic import MPTfileCSV, str3  # not exported

testdata_dir = os.path.join(os.path.dirname(__file__), 'testdata')


def test_open_MPT():
    mpt1, comments = MPTfile(os.path.join(testdata_dir, 'bio_logic1.mpt'))
    eq_(comments, [])
    eq_(mpt1.dtype.names, ("mode", "ox/red", "error", "control changes",
                           "Ns changes", "counter inc.", "time/s",
                           "control/V/mA", "Ewe/V", "dQ/mA.h", "P/W",
                           "I/mA", "(Q-Qo)/mA.h", "x"))


@raises(ValueError)
def test_open_MPT_fails_for_bad_file():
    mpt1 = MPTfile(os.path.join(testdata_dir, 'bio_logic1.mpr'))


def test_open_MPT_csv():
    mpt1, comments = MPTfileCSV(os.path.join(testdata_dir, 'bio_logic1.mpt'))
    eq_(comments, [])
    eq_(mpt1.fieldnames, ["mode", "ox/red", "error", "control changes",
                          "Ns changes", "counter inc.", "time/s",
                          "control/V/mA", "Ewe/V", "dq/mA.h", "P/W",
                          "<I>/mA", "(Q-Qo)/mA.h", "x"])


@raises(ValueError)
def test_open_MPT_csv_fails_for_bad_file():
    mpt1 = MPTfileCSV(os.path.join(testdata_dir, 'bio_logic1.mpr'))


def test_open_MPR1():
    mpr1 = MPRfile(os.path.join(testdata_dir, 'bio_logic1.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr1.startdate, date(2011, 10, 29))
    eq_(mpr1.enddate, date(2011, 10, 31))


def test_open_MPR2():
    mpr2 = MPRfile(os.path.join(testdata_dir, 'bio_logic2.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr2.startdate, date(2012, 9, 27))
    eq_(mpr2.enddate, date(2012, 9, 27))


def test_open_MPR3():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic3.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr.startdate, date(2013, 3, 27))
    eq_(mpr.enddate, date(2013, 3, 27))


def test_open_MPR4():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic4.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr.startdate, date(2011, 11, 1))
    eq_(mpr.enddate, date(2011, 11, 2))


def test_open_MPR5():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic5.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr.startdate, date(2013, 1, 28))
    eq_(mpr.enddate, date(2013, 1, 28))


def test_open_MPR6():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic6.mpr'))
    ## Check the dates as a basic test that it has been read properly
    eq_(mpr.startdate, date(2012, 9, 11))
    ## no end date because no VMP LOG module


@raises(ValueError)
def test_open_MPR_fails_for_bad_file():
    mpr1 = MPRfile(os.path.join(testdata_dir, 'arbin1.res'))


def timestamp_from_comments(comments):
    for line in comments:
        time_match = re.match(b'Acquisition started on : ([0-9/]+ [0-9:]+)', line)
        if time_match:
            timestamp = datetime.strptime(str3(time_match.group(1)),
                                          '%m/%d/%Y %H:%M:%S')
            return timestamp
    raise AttributeError("No timestamp in comments")


def assert_MPR_matches_MPT(mpr, mpt, comments):

    def assert_field_matches(fieldname, decimal):
        if fieldname in mpr.dtype.fields:
            assert_array_almost_equal(mpr.data[fieldname],
                                      mpt[fieldname],
                                      decimal=decimal)

    def assert_field_exact(fieldname):
        if fieldname in mpr.dtype.fields:
            assert_array_equal(mpr.data[fieldname], mpt[fieldname])

    assert_array_equal(mpr.get_flag("mode"), mpt["mode"])
    assert_array_equal(mpr.get_flag("ox/red"), mpt["ox/red"])
    assert_array_equal(mpr.get_flag("error"), mpt["error"])
    assert_array_equal(mpr.get_flag("control changes"), mpt["control changes"])
    if "Ns changes" in mpt.dtype.fields:
        assert_array_equal(mpr.get_flag("Ns changes"), mpt["Ns changes"])
    ## Nothing uses the 0x40 bit of the flags    
    assert_array_equal(mpr.get_flag("counter inc."), mpt["counter inc."])

    assert_array_almost_equal(mpr.data["time/s"],
                              mpt["time/s"],
                              decimal=2)  # 2 digits in CSV

    assert_field_matches("control/V/mA", decimal=6)
    assert_field_matches("control/V", decimal=6)

    assert_array_almost_equal(mpr.data["Ewe/V"],
                              mpt["Ewe/V"],
                              decimal=6)  # 32 bit float precision

    assert_field_matches("dQ/mA.h", decimal=17)  # 64 bit float precision
    assert_field_matches("P/W", decimal=10)  # 32 bit float precision for 1.xxE-5
    assert_field_matches("I/mA", decimal=6)  # 32 bit float precision
    
    assert_field_exact("cycle number")
    assert_field_matches("(Q-Qo)/C", decimal=6)  # 32 bit float precision
    
    try:
        eq_(timestamp_from_comments(comments), mpr.timestamp)
    except AttributeError:
        pass


def test_MPR1_matches_MPT1():
    mpr1 = MPRfile(os.path.join(testdata_dir, 'bio_logic1.mpr'))
    mpt1, comments = MPTfile(os.path.join(testdata_dir, 'bio_logic1.mpt'))
    assert_MPR_matches_MPT(mpr1, mpt1, comments)


def test_MPR2_matches_MPT2():
    mpr2 = MPRfile(os.path.join(testdata_dir, 'bio_logic2.mpr'))
    mpt2, comments = MPTfile(os.path.join(testdata_dir, 'bio_logic2.mpt'))
    assert_MPR_matches_MPT(mpr2, mpt2, comments)


## No bio_logic3.mpt file


def test_MPR4_matches_MPT4():
    mpr4 = MPRfile(os.path.join(testdata_dir, 'bio_logic4.mpr'))
    mpt4, comments = MPTfile(os.path.join(testdata_dir, 'bio_logic4.mpt'))
    assert_MPR_matches_MPT(mpr4, mpt4, comments)


def test_MPR5_matches_MPT5():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic5.mpr'))
    mpt, comments = MPTfile((re.sub(b'\tXXX\t', b'\t0\t', line) for line in
                             open(os.path.join(testdata_dir, 'bio_logic5.mpt'),
                                  mode='rb')))
    assert_MPR_matches_MPT(mpr, mpt, comments)


def test_MPR6_matches_MPT6():
    mpr = MPRfile(os.path.join(testdata_dir, 'bio_logic6.mpr'))
    mpt, comments = MPTfile(os.path.join(testdata_dir, 'bio_logic6.mpt'))
    mpr.data = mpr.data[:958]  # .mpt file is incomplete
    assert_MPR_matches_MPT(mpr, mpt, comments)


## Tests for issue #1 -- new dtypes ##


def test_CV_C01():
    mpr = MPRfile(os.path.join(testdata_dir, 'CV_C01.mpr'))
    mpt, comments = MPTfile(os.path.join(testdata_dir, 'CV_C01.mpt'))
    assert_MPR_matches_MPT(mpr, mpt, comments)


def test_CA_455nm():
    mpr = MPRfile(os.path.join(testdata_dir, '121_CA_455nm_6V_30min_C01.mpr'))
    mpt, comments = MPTfile(os.path.join(testdata_dir, '121_CA_455nm_6V_30min_C01.mpt'))
    assert_MPR_matches_MPT(mpr, mpt, comments)
