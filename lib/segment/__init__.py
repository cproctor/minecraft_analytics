# Working with segmentation parameters

import shutil
import yaml
from datetime import datetime
from pathlib import Path
from .product import PRODUCT_FORMATS

class Segment:
    """Represents segment--a slice of time across all data files. Params should include:
        - start: UTC timestamp like 2021-07-28 18:30:00
        - end: UTC timestamp like 2021-07-28 19:00:00
        - products: A list of dicts describing products to produce and source files from which to draw.
          File paths are relative to the `data` dir. For example:
            - format: transcript
              source: transcripts/2021_07_21_workshop_3_zoom_transcript.vtt
            - format: video
              audio_source: audio/2021_07_14_workshop_2.m4a 
              video_source: replay/2021_07_14_Workshop_2.mp4
            - format: logs
    """

    def __init__(self, params):
        self.params = params

    def export(self, clean=False):
        """Creates a directory at `export_dir` with the specified segment products.
        When `clean`, deletes and recreates `export_dir` if it exists.
        Otherwise, raises an error if `export_dir` exists and is not empty.
        (This is safer, but `clean` allows us to re-run a command repeatedly
        without having to clear out the results each time.)

        TODO:
        - For each product, initialize and 
            - Actually implement the product export methods.
        """
        self.params["export_time"] = datetime.utcnow()
        export_dir = Path(self.params["export_dir"])
        self.prepare_export_dir(export_dir, clean=clean)
        (export_dir / "params.yaml").write_text(yaml.dump(self.params))

    def prepare_export_dir(self, export_dir, clean=False):
        """Prepares the export dir"""
        if clean:
            if export_dir.exists():
                if export_dir.is_dir() and self.has_subdirectories(export_dir):
                    err = (
                        "The provided export path {} has subdirectories. "
                        "This is forbidden as a safety measure to prevent accidental deletion."
                    )
                    raise ValueError(err.format(export_dir))
            shutil.rmtree(export_dir)
        else:
            if export_dir.exists():
                raise ValueError("{} exists. Can't overwrite without --clean".format(export_dir))
        export_dir.mkdir()
        for product_params in self.params['products']:
            product_class = PRODUCT_FORMATS[product_params['format']]
            product = product_class(self.params, product_params)
            product.export()
            

    def dry_run(self, clean=False):
        """Returns a list of steps which would be taken by `export`.
        """
        return []

    def validate(self, strict=True):
        """Validates params, raising an exception when `strict`.
        Returns a (possibly-empty) list of errors.

        TODO Should conduct the following tests, collecting a list of errors. If
        there are any errors, print the errors and raise ValueError.
        Check that:
          - export_dir is set
          - start and end are timestamps
          - start < end
          - products key is present. For each product:
            - Must have `format` key, and format must be in FORMATS
        """
        errors = []
        # Main validation should happen here.
        if not self.params.get("export_dir"):
            errors.append("Params must have 'export_dir'")

        # Iterate over products, delegating validation to each format class.
        if 'products' in self.params:
            for i, product_params in enumerate(self.params['products']):
                if 'format' in product_params:
                    pfmt = product_params['format']
                    if pfmt in PRODUCT_FORMATS:
                        product_class = PRODUCT_FORMATS[pfmt]
                        product = product_class(self.params, product_params)
                        errors += product.validate()
                    else:
                        errors.append("Invalid format '{}' in product {}".format(pfmt, i))
                else:
                    errors.append("Product {} must have 'format'".format(i))
        else:
            errors.append("Params must have 'products'")
        if strict and errors:
            err_msg = self.format_error_list(errors)
            raise ValueError("Invalid segment params:\n{}".format(err_msg))
        return errors

    def format_error_list(self, errors):
        """A helper which returns errors as a formatted list."""
        return '\n'.join(" - {}".format(err) for err in errors)

    def has_subdirectories(self, path):
        "Checks whether a path has subdirectories"
        for p in path.iterdir():
            if p.is_dir():
                return True

