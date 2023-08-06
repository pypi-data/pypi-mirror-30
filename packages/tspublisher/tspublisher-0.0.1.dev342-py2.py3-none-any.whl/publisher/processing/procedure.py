from publisher.processing.data_sources.asset import convert_files
from publisher.processing.data_sources.overview import get_overview_and_devices
from publisher.processing.data_sources.eula import copy_eula_to_procedure
from publisher.processing.data_sources.organisation import get_organisation_from_channel
from publisher.processing.data_sources.author import get_author_from_db
from publisher.processing.data_sources.production_csv import get_production_csv_data, \
    get_procedure_details, get_procedure_phase_list
from publisher.processing.data_sources.step import get_step_data
from publisher.processing.data_sources.thumbnail import update_thumbnails, update_phase_thumbnails
from publisher.processing.data_sources.utils import YamlObject
from publisher.processing.models import Procedure, Phase
from publisher.processing.utils.file import ProcedureFileManager


def create_procedure(procedure_code):

    procedure = Procedure()
    procedure.code = procedure_code

    phase = Phase()
    phase.code = "{0}_001".format(procedure_code)
    procedure.phases.append(phase)

    procedure_files = ProcedureFileManager(procedure)

    create_yaml_file(procedure, procedure_files.procedure_file)
    create_yaml_file(phase, procedure_files.phase_files[0].phase_file)

    return procedure, procedure_files


def initialize_procedure(procedure_code):
    procedure = build_procedure_object(procedure_code)
    procedure_files = ProcedureFileManager(procedure)

    return procedure, procedure_files


def build_procedure_object(procedure_code):
    data = get_production_csv_data()

    procedure = Procedure()
    procedure.code = procedure_code
    procedure.name, procedure.specialties, procedure.channel = get_procedure_details(procedure_code, data)

    phases_data = get_procedure_phase_list(procedure_code, data)
    procedure.phases = map(lambda p: build_phase_object(procedure_code, p), phases_data)

    return procedure


def build_phase_object(procedure_code, phase_data):

    phase = Phase()

    phase.procedureCode = procedure_code
    phase.code = phase_data['phase_code']
    phase.name = phase_data['phase_name']
    phase.released_as = phase_data['released_as']

    return phase


def build_procedure(procedure_code, graphics=True, pip_graphics=True, widget_graphics=True, thumbnails=True,
                    step_numbers=True, info_step=True, country_restriction=""):

    procedure, procedure_files = initialize_procedure(procedure_code)
    procedure.overview, procedure.devices = get_overview_and_devices(procedure.phases[0],
                                                                     procedure_files.asset_directory)

    procedure.organisation = get_organisation_from_channel(procedure.channel)
    procedure.author = get_author_from_db(procedure_code)
    procedure.eulaFile = copy_eula_to_procedure(procedure_code, procedure_files.asset_directory)

    if thumbnails:
        update_thumbnails(procedure, procedure_files.asset_directory)

    create_yaml_file(procedure, procedure_files.procedure_file)

    for phase in procedure.phases:

        print "\nCreating phase page: %s" % phase.code
        phase_files = next(pf for pf in procedure_files.phase_files if pf.phase_code == phase.code)
        build_phase(phase, phase_files, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers=step_numbers,
                    info_step=info_step, country_restriction=country_restriction)


def build_phase(phase, phase_files, graphics, pip_graphics, widget_graphics, thumbnails, step_numbers=True,
                info_step=True, supported_app="TouchSurgery", country_restriction=""):

    phase.learnObjectives, phase.testObjectives = get_step_data(phase.code)
    phase.countryRestriction = country_restriction
    phase.phaseDir = phase_files.asset_directory

    phase.supported_app = supported_app
    phase.stepNumbers = step_numbers
    phase.infoStep = info_step

    create_yaml_file(phase, phase_files.phase_file)

    if thumbnails:
        update_phase_thumbnails(phase, phase_files.asset_directory)

    convert_files(phase, phase_files.base_directory, graphics, pip_graphics, widget_graphics)


def create_yaml_file(obj, output_file):

    yaml = YamlObject()

    yaml_stream = open(output_file, "wb")

    obj.dump(yaml, yaml_stream)

    # Check yaml validity by loading file
    yaml_stream = open(output_file, "r")
    yaml.load(yaml_stream)
