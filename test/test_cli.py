"""
Testing CLI module
"""
import os

import pytest
from click.testing import CliRunner

from vcf2neo.cli import load_vcf

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_DATA_DIR = os.path.join(CURR_DIR, "test_data/")
TEST_VCF = os.path.join(CURR_DIR, "test_data/test_snpeff_annotated.vcf")


@pytest.fixture(scope="module")
def cli_runner():
    runner = CliRunner()
    return runner


def test_load_vcf(cli_runner):
    result = cli_runner.invoke(
        load_vcf,
        ['-p', 'MDR', '-a', 'Rifampicin', '-a', 'Isoniazid', TEST_DATA_DIR]
    )
    assert result.exit_code == 0
