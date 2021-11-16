from pathlib import Path
import shutil

class BaseModel:
    """An abstract class representing an analysis.
    """
    expected_params = [
        'model',
        'export_dir',
    ]
    optional_params = [
    ]
    def __init__(self, params):
        self.params = params
    
    def validate(self, strict=True):
        """Model-specific validation. Returns a list of errors.
        """
        errors = []
        for param in self.expected_params:
            if param not in self.params:
                errors.append("Model {} requires param {}".format(
                    self.__class__.__name__,
                    param
                ))
        for param in self.params:
            if param not in self.expected_params and param not in self.optional_params:
                errors.append("Model {} received unexpected param {}".format(
                    self.__class__.__name__,
                    param
                ))
        if strict and errors:
            raise ValueError("Errors in model params: " + "\n".join(errors))
        else:
            return errors

    def prepare_export_dir(self, clean=False):
        """Prepares the export dir"""
        if clean:
            if self.export_dir().exists():
                if self.export_dir().is_dir() and self.has_subdirectories(self.export_dir()):
                    err = (
                        "The provided export path {} has subdirectories. "
                        "This is forbidden as a safety measure to prevent accidental deletion."
                    )
                    raise ValueError(err.format(export_dir))
            shutil.rmtree(self.export_dir())
        else:
            if self.export_dir().exists():
                raise ValueError("{} exists. Can't overwrite without --clean".format(self.export_dir()))
        self.export_dir().mkdir()
           
    def export(self):
        """Exports this product.
        """
        raise NotImplemented()

    def export_dir(self):
        return Path(self.params['export_dir'])

    def has_subdirectories(self, path):
        "Checks whether a path has subdirectories"
        for p in path.iterdir():
            if p.is_dir():
                return True

