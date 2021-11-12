from pathlib import Path

class SegmentProduct:
    """An abstract class which models a product to be produced from a segment.
    Required methods are validate and export.
    """
    expected_params = [
        "format",
        "export_filename",
    ]
    optional_params = []

    def __init__(self, segment_params, product_params):
        self.segment_params = segment_params
        self.params = product_params

    def validate(self):
        """Product-specific validation. Returns a list of errors.
        """
        errors = []
        for param in self.expected_params:
            if param not in self.params:
                errors.append("Product {} requires param {}".format(
                    self.__class__.__name__,
                    param
                ))
        for param in self.params:
            if param not in self.expected_params and param not in self.optional_params:
                errors.append("Product {} received unexpected param {}".format(
                    self.__class__.__name__,
                    param
                ))
        return errors

    def export(self):
        """Exports this product.
        """
        raise NotImplemented()

    def export_filename(self, filename_key='export_filename'):
        """Returns a fully-qualified export filename"""
        export_dir = Path(self.segment_params['export_dir'])
        export_filename = export_dir / self.params[filename_key]
        return export_filename.resolve()
