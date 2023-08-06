from genologics.descriptors import StringDescriptor, EntityListDescriptor, BooleanDescriptor, IntegerDescriptor
from genologics.entities import File
from genologics.constants import nsmap


class ProcessTypeParameter(object):

    instance = None
    name = None
    root = None
    tag = 'parameter'

    string = StringDescriptor('string')
    run_program_per_event = StringDescriptor('run-program-per-event')
    channel = StringDescriptor('channel')
    invocation_type = StringDescriptor('invocation-type')
    file = EntityListDescriptor(nsmap('file:file'), File)

    def __init__(self, pt_instance, node):
        self.instance = pt_instance
        self.root = node
        self.name = self.root.attrib['name']

    def get(self):
        pass

class ProcessTypeProcessInput(object):

    instance = None
    name = None
    root = None
    tag = ''

    artifact_type = StringDescriptor('artifact-type')
    display_name = StringDescriptor('display-name')
    remove_working_flag = BooleanDescriptor('remove-working-flag')

    def __init__(self, pt_instance, node):
        self.instance = pt_instance
        self.root = node

    def get(self):
        pass

class ProcessTypeProcessOutput(object):

    instance = None
    name = None
    root = None
    tag = ''

    artifact_type = StringDescriptor('artifact-type')
    display_name = StringDescriptor('display-name')
    output_generation_type = StringDescriptor('output-generation-type')
    variability_type = StringDescriptor('variability-type')
    number_of_outputs = IntegerDescriptor('number-of-outputs')
    output_name = StringDescriptor('output-name')

    def __init__(self, pt_instance, node):
        self.instance = pt_instance
        self.root = node

    def get(self):
        pass
