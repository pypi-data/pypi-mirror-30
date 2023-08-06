from typing import List, Optional, Dict, Iterator
import tempfile
import logging

import bugzoo
import bugzoo.localization.suspiciousness as metrics
from bugzoo.core.fileline import FileLine, FileLineSet
from bugzoo.core.bug import Bug
from bugzoo.core.patch import Patch
from bugzoo.core.coverage import TestSuiteCoverage
from bugzoo.core.spectra import Spectra
from bugzoo.localization import SuspiciousnessMetric
from bugzoo.testing import TestCase

import darjeeling.filters as filters
from .donor import DonorPool
from .transformation import TransformationDatabase
from .source import SourceFile


class Problem(object):
    """
    Used to provide a description of a problem (i.e., a bug), and to hold
    information pertinent to its solution (e.g., coverage, transformations).
    """
    def __init__(self,
                 bz: bugzoo.BugZoo,
                 bug: Bug,
                 *,
                 suspiciousness_metric: Optional[SuspiciousnessMetric] = None,
                 in_files: List[str],
                 restrict_to_lines: Optional[FileLineSet] = None,
                 cache_coverage: bool = True,
                 verbose: bool = False
                 ) -> None:
        """
        Constructs a Darjeeling problem description.

        Params:
            bug: A description of the faulty program.
            in_files: An optional list that can be used to restrict the set of
                transformations to those that occur in any files belonging to
                that list. If no list is provided, all source code files will
                be included.
            in_functions: An optional list that can be used to restrict the set
                of transformations to those that occur in any function whose
                name appears in the given list. If no list is provided, no
                filtering of transformations based on the function to which
                they belong will occur.
        """
        assert len(in_files) > 0
        self.__bug = bug
        self.__verbose = verbose

        self.__logger = \
            logging.getLogger('darjeeling.problem').getChild(bug.name)
        # TODO stream logging info for now
        self.__logger.setLevel(logging.DEBUG)
        self.__logger.addHandler(logging.StreamHandler())
        self.__logger.debug("creating problem for bug: %s", bug.name)

        if suspiciousness_metric is None:
            self.__logger.debug("no suspiciousness metric provided: using Tarantula as a default.")
            suspiciousness_metric = metrics.tarantula

        # fetch coverage information
        if cache_coverage:
            self.__logger.debug("fetching coverage information from BugZoo")
            self.__coverage = bz.bugs.coverage(bug)
            self.__logger.debug("fetched coverage information from BugZoo")
        else:
            self.__logger.debug("computing coverage information")
            try:
                container = bz.containers.provision(bug)
                self.__coverage = bz.coverage.coverage(container, bug.tests)
            finally:
                del bz.containers[container.uid]
            self.__logger.debug("computed coverage information")

        # restrict coverage information to specified files
        self.__logger.debug("restricting coverage information to files:\n* %s",
                            '\n* '.join(in_files))
        self.__coverage = self.__coverage.restricted_to_files(in_files)
        self.__logger.debug("restricted coverage information.")

        # determine the passing and failing tests by using coverage information
        self.__logger.debug("using test execution used to generate coverage to determine passing and failing tests")

        self.__tests_failing = set()
        self.__tests_passing = set()
        for test_name in self.__coverage:
            test = bug.harness[test_name]
            test_coverage = self.__coverage[test_name]
            if test_coverage.outcome.passed:
                self.__tests_passing.add(test)
            else:
                self.__tests_failing.add(test)

        # TODO throw an error if there are no failing tests
        self.__logger.info("determined passing and failing tests")
        self.__logger.info("* passing tests: %s", ', '.join([t.name for t in self.__tests_passing]))
        self.__logger.info("* failing tests: %s", ', '.join([t.name for t in self.__tests_failing]))

        # determine the implicated lines
        # 0. we already restricted to lines that occur in specified files
        # 1. restrict to lines covered by failing tests
        # 3. restrict to lines with suspiciousness greater than zero
        # 4. restrict to lines that are optionally provided
        self.__logger.info("Determining implicated lines")
        self.__lines = self.__coverage.failing.lines

        if restrict_to_lines is not None:
            self.__lines = self.__lines.intersection(restrict_to_lines)

        # cache contents of implicated files
        # FIXME this method of construction is slow and error-prone
        self.__logger.debug("storing contents of source code files")
        self.__sources = \
            {fn: SourceFile.load(bz, bug, fn) for fn in self.__lines.files}
        self.__logger.debug("finished storing contents of source code files")

        # restrict attention to statements
        # FIXME for now, we approximate this -- going forward, we can use
        #   Rooibos to determine transformation targets
        line_content_filters = [
            filters.ends_with_semi_colon,
            filters.has_balanced_delimiters
        ]
        for fltr_content in line_content_filters:
            fltr_line = \
                lambda fl: fltr_content(self.__sources[fl.filename][fl.num])
            self.__lines = self.__lines.filter(fltr_line)

        # TODO raise an exception if there are no implicated lines

        # once again, restrict coverage to implicated files to save memory,
        # then generate a spectra and use it to compute the localization
        self.__coverage = \
            self.__coverage.restricted_to_files(self.__lines.files)
        self.__spectra = Spectra.from_coverage(self.__coverage)

        # report implicated lines and files
        self.__logger.info("implicated lines [%d]:\n%s",
                           len(self.__lines), self.__lines)
        self.__logger.info("implicated files [%d]:\n* %s",
                           len(self.__lines.files),
                           '\n* '.join(self.__lines.files))

        # FIXME remove files that are no longer implicated from the cache


    @property
    def bug(self) -> Bug:
        """
        A description of the bug, provided by BugZoo.
        """
        return self.__bug

    @property
    def tests(self) -> Iterator[TestCase]:
        """
        Returns an iterator over the tests for this problem.
        """
        for test in self.__tests_failing:
            yield test
        for test in self.__tests_passing:
            yield test

    @property
    def tests_failing(self) -> Iterator[TestCase]:
        """
        Returns an iterator over the failing tests for this problem.
        """
        return self.__tests_failing.__iter__()

    @property
    def tests_passing(self) -> Iterator[TestCase]:
        """
        Returns an iterator over the passing tests for this problem.
        """
        return self.__tests_passing.__iter__()

    @property
    def coverage(self) -> TestSuiteCoverage:
        """
        Line coverage information for each test within the test suite for the
        program under repair.
        """
        return self.__coverage

    @property
    def spectra(self) -> Spectra:
        """
        Provides a concise summary of the number of passing and failing tests
        that cover each implicated line.
        """
        return self.__spectra

    @property
    def lines(self) -> Iterator[FileLine]:
        """
        Returns an iterator over the lines that are implicated by the
        description of this problem.
        """
        return self.__lines.__iter__()

    def source(self, fn: str) -> SourceFile:
        """
        Returns the contents of a given source code file for this problem.
        """
        return self.__sources[fn]

    def check_sanity(self,
                     expected_to_pass: List[TestCase],
                     expected_to_fail: List[TestCase]
                     ) -> bool:
        """

        Parameters:
            expected_to_pass: a list of test cases for the program that are
                expected to pass.
            expected_to_fail: a list o test cases for the program that are
                expected to fail.

        Returns:
            True if the outcomes of the test executions match those that are
            expected by the parameters to this method.

        Raises:
            errors.UnexpectedTestOutcomes: if the outcomes of the program
                under test, observed while computing coverage information for
                the problem, differ from those that were expected.
        """
        # determine passing and failing tests
        self.__logger.debug("sanity checking...")
        raise NotImplementedError
