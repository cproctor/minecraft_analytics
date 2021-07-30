# Working with segmentation parameters

from .product import PRODUCT_FORMATS

class Segment:
    """Represents segment--a slice of time across all data files. Params should include:
        - begin: UTC timestamp like 2021-07-28 18:30:00
        - end: UTC timestamp like 2021-07-28 19:00:00
        - products: A list of dicts describing products to produce and source files from which to draw.
          File paths are relative to the `data` dir. For example:
            - format: transcript
              source: data/minecraft_audio_transcripts/2021_07_21_workshop_3_zoom_transcript.vtt
            - format: video
              audio_source: data/minecraft_audio_recordings/2021_07_14_workshop_2.m4a 
              video_source: data/data/minecraft_replay_videos/2021_07_14_Workshop_2.
            - format: logs
    """

    def __init__(self, params):
        self.params = params

    def export(self, export_path, clean=False):
        """Creates a directory at `export_path` with the specified segment products.
        When `clean`, deletes and recreates `export_path` if it exists.
        Otherwise, raises an error if `export_path` exists and is not empty.
        (This is safer, but `clean` allows us to re-run a command repeatedly
        without having to clear out the results each time.)

        TODO:
        - Implement `clean` behavior as specified above.
        - Write the params into export_dir/params.yaml, including a new key of
          export:timestamp: when the export happened.
        - For each product, initialize and 
            - Actually implement the product export methods.
        """
        raise NotImplemented()

    def dry_run(self, export_path, clean=False):
        """Returns a list of steps which would be taken by `export`.
        """
        return []

    def validate(self, strict=True):
        """Validates params, raising an exception when `strict`.
        Returns a (possibly-empty) list of errors.

        TODO Should conduct the following tests, collecting a list of errors. If
        there are any errors, print the errors and raise ValueError.
        Check that:
          - begin and end are timestamps
          - begin < end
          - products key is present. For each product:
            - Must have `format` key, and format must be in FORMATS
        """
        errors = []
        # Main validation should happen here.

        # Iterate over products, delegating validation to each format class.
        if 'products' in self.params:
            for i, product_params in enumerate(self.params['products']):
                if 'format' in product_params:
                    pfmt = product_params['format']
                    if pfmt in PRODUCT_FORMATS:
                        product_class = PRODUCT_FORMATS[pfmt]
                        product = product_class(product_params)
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

    def validate_product(self, product):
        """A helper for iterating over products in `validate`
        Product should be a dict. Returns a list of strings describing errors.
        """
        return []

    def format_error_list(self, errors):
        """A helper which returns errors as a formatted list."""
        return '\n'.join(" - {}".format(err) for err in errors)

