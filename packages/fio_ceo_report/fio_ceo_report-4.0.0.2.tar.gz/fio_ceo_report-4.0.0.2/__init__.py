# -*- coding: utf-8 -*-
"""
    __init__.py

"""
from trytond.pool import Pool
from ceo_report import CEOReport, GenerateCEOReport, GenerateCEOReportStart


def register():
    Pool.register(
        GenerateCEOReportStart,
        module='ceo_report', type_='model'
    )
    Pool.register(
        CEOReport,
        module='ceo_report', type_='report'
    )
    Pool.register(
        GenerateCEOReport,
        module='ceo_report', type_='wizard'
    )
