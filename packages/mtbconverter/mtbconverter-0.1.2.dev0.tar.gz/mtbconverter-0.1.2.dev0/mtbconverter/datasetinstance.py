"""Data-set instance represents a CentraXX FlexibleDataSetInstance
type for the patient import"""

import uuid
import datetime
import mtbparser.snv_utils
import mtbconverter.cxxpy as cx
from .cx_utils import *

class DataSetInstance():

    def __init__(self, header_type, snv_item, date, version, instance):
        """DataSetInstance object
        _header_type: The header type of enum mtbparser.snv_utils.SSnvHeader, ...
        _snv_item: An entry of class mtbparser.snv_items.SNVItems()
        _date: ISO 8601 formatted timestamp
        _version: A version tag as string
        _instance: An incremental integer for the instance
        _reference: A random uuid4 id for cross referencing
        """
        self._header_type = header_type
        self._snv_item = snv_item
        self._date = date
        self._version = version
        self._instance = instance
        self._reference = str(uuid.uuid4())

    def reference(self):
        """Return the uuid4 reference id"""
        return self._reference

    def datasetinstance(self):
        """Return a FlexibleDataSetInstance object"""
        timestamp = datetime.datetime.now().isoformat(timespec='milliseconds')
        flex_dataset = cx.FlexibleDataSetInstanceType()
        flex_dataset.FlexibleDataSetTypeRef = self._version
        flex_dataset.FlexibleDataSetInstanceRef = self._reference
        flex_dataset.InstanceName = '{}_increment{}_{}'.format(
            self._version, self._instance, timestamp)
        flex_dataset.DateType = cx.DateType(Date=timestamp, Precision='EXACT')
        snv_columns = []
        for key, value in self._snv_item.get_item().items():
            value_type = self._valuetypefromfield(key)
            value_type.FlexibleValueTypeRef = CV_PREFIX + key.lower()
            if value_type.__class__.__name__ == 'FlexibleEnumerationDataType':
                value_type.Value = [CV_PREFIX + value]
            else: 
                value_type.Value = value
            snv_columns.append(value_type)
        
        dec_type = []
        enum_type = []
        int_type = []
        str_type = []

        for col in snv_columns:
            class_type = col.__class__.__name__
            if "String" in class_type:
                str_type.append(col)
            if "Enum" in class_type:
                enum_type.append(col)
            if "Integer" in class_type:
                int_type.append(col)
            if "Decimal" in class_type:
                dec_type.append(col)

        flex_dataset.StringValue = str_type
        flex_dataset.EnumerationValue = enum_type
        flex_dataset.IntegerValue = int_type
        flex_dataset.DecimalValue = dec_type

        return flex_dataset

    def _valuetypefromfield(self, field):
        """Determine value type from a field"""
        if field.lower() in ['tumor_content', 'allele_frequency_tumor', 'coverage']:
            return cx.FlexibleDecimalDataType()
        if field.lower() in ['genotype', 'mutational_load', 'ref', 'chromosomes', 'chr']:
            return cx.FlexibleEnumerationDataType()
        if field.lower() in ['start', 'end']:
            return cx.FlexibleIntegerDataType()
        return cx.FlexibleStringDataType()
        