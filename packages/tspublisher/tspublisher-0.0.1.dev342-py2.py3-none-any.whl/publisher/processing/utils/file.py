import os

from publisher import settings


class ProcedureFileManager(object):

    def __init__(self, procedure):
        self._prcocedure_code = procedure.code
        self._ensure_structure_exists()

        self.phase_files = map(lambda p: PhaseFileManager(p, self.base_directory), procedure.phases)

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, self._prcocedure_code)

    @property
    def procedure_file(self):
        return os.path.join(self.base_directory, 'procedure.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')


class PhaseFileManager(object):

    def __init__(self, phase, procedure_directory):
        self.procedure_directory = procedure_directory
        self.phase_code = phase.code

        self._ensure_structure_exists()

    def _ensure_structure_exists(self):
        for d in [self.base_directory, self.asset_directory, self.translation_directory]:
            if not os.path.exists(d):
                os.makedirs(d)

    @property
    def base_directory(self):
        return os.path.join(self.procedure_directory, self.phase_code)

    @property
    def phase_file(self):
        return os.path.join(self.base_directory, 'phase.yml')

    @property
    def asset_directory(self):
        return os.path.join(self.base_directory, 'assets')

    @property
    def translation_directory(self):
        return os.path.join(self.base_directory, 'translations')
