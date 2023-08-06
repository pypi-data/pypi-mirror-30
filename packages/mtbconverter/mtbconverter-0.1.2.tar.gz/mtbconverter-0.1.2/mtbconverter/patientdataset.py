"""This reflects a patient data set structure
which consumes multiple datasetinstances in order
to link them by their reference number"""

from .mtbconverter_exceptions import NoReferenceIdFound
import mtbconverter.cxxpy as cx

class PatientDataSet():

    def __init__(self, qbic_pat_id, qbic_sample_id,
        datetime, datasetinstance_list):
        self._qbic_pat_id = qbic_pat_id
        self._qbic_sample_id = qbic_sample_id
        self._datetime = datetime
        self._datasetinstance_list = datasetinstance_list

    def patientdataset(self):
        # Create the patient data set
        patient_data_set = cx.PatientDataSetType(Source='XMLIMPORT')
        patient_data_set.OrganisationUnitRefs = ['QBIC']

        # Create ID container with QBIC patient id first
        id_container = cx.IDContainerType()
        id_flexible = cx.FlexibleIDType(key='QBIC_PAT_ID', value_=self._qbic_pat_id)
        id_container.append(id_flexible)
        patient_data_set.IDContainer = id_container

        # Create the sample data for the patient
        sample_data = cx.SampleDataType()
        master_sample = cx.MasterSampleType()
        sample_id_container = cx.SampleIDContainerType()

        master_sample = cx.MasterSampleType(Source='XMLIMPORT',
            SampleTypeCatalogueTypeRef='TISSUE_OTH', SampleReceptacleTypeRef='ORG',
            SampleKind='TISSUE', SopDeviation='false', HasChildren='false', SampleLocationRef='QBIC_STORAGE')
        sample_id_container = cx.SampleIDContainerType()
        flex_id_1 = cx.FlexibleIDType(key='SAMPLEID', value_=self._qbic_sample_id + '_VIRT')
        flex_id_2 = cx.FlexibleIDType(key='QBIC_SAMPLE_ID', value_=self._qbic_sample_id + '_VIRT')

        # Add the flex IDs to the sample container
        sample_id_container.append(flex_id_1)
        sample_id_container.append(flex_id_2)

        sampling_date = cx.DateType(Date=self._datetime, Precision='EXACT')
        master_sample.SampleIDContainer = sample_id_container

        init_amount = cx.VolumeType(Volume='1.0000', Unit='PC')

        master_sample.AmountRest = init_amount
        master_sample.InitialAmount = init_amount
        master_sample.SamplingDate = sampling_date
        master_sample.RepositionDate = sampling_date
        master_sample.FirstRepositionDate = sampling_date

        # Now extract the reference number of the dataset instances
        flex_dsref_list = []
        for flex_ds_instance in self._datasetinstance_list:
            ref = flex_ds_instance.reference()
            if not ref:
                raise NoReferenceIdFound("No reference id has been found"
                " for the given flexible dataset (SampleId: {})".format(self._qbic_sample_id))
            flex_dsref_list.append(ref)
        
    
        master_sample.FlexibleDataSetRef = flex_dsref_list
        sample_data = cx.SampleDataType()
        sample_data.append(master_sample)

        patient_data_set.SampleData = sample_data

        return patient_data_set           
