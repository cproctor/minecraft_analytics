# What needs to be done now?
# - Get the anvil data.
#   - Base64 encode it. 
#   - Drop it into the template.

from subprocess import run, DEVNULL
from segment.product.logs import SegmentLogs
from jinja2 import FileSystemLoader, Environment
import shutil
from pathlib import Path
import json
from base64 import b64encode
from segment.product.simulation.mc_world import MinecraftWorldView

class SegmentSimulation(SegmentLogs):
    """A three.js simulation.
    - Use the full log to compute the world's initial state.
    """

    expected_params = [
        "format",
        "export_filename",
        "bounding_box",
    ]

    optional_params = [
        "title",
        "use_cache",
        "debug",
    ]

    here = Path(__file__).parent
    bundle_path = here / 'js' / 'bundle.js'
    template_dir = here / 'html'
    template = 'template.html'
    initial_production_mca_path = "data/server/production-original/region"

    def export(self):
        self.generate_study_data_json()
        run('npm run build', cwd=self.here / 'js', shell=True, stdout=DEVNULL)
        env = Environment(loader=FileSystemLoader(self.template_dir))
        template = env.get_template(self.template)
        simulation_js = self.bundle_path.read_text()
        study_json = self.get_cached_study_data_path().read_text()

        with open(self.export_filename(), 'w') as fh:
            with open(self.bundle_path) as js_fh:
                fh.write(template.render({
                    'simulation_js': simulation_js,
                    'study_json': study_json,
                    'title': self.params.get('title', '')
                }))

    def generate_study_data_json(self):
        if not (self.params.get("use_cache") and self.get_cached_study_data_path().exists()):
            world = MinecraftWorldView(
                self.initial_production_mca_path,
                self.main_log_file,
                self.params['bounding_box'],
                self.segment_params['start'],
                self.segment_params['duration'],
            )
            base_layer, palette = world.get_base_layer_at_start()
            with open(self.get_cached_study_data_path(), 'w') as fh:
                json.dump({
                    'layers': {
                        'base': {
                            'start': b64encode(bytes(base_layer)).decode('ascii'),
                            'palette': palette
                        }
                    },
                    'params': {
                        'bounding_box': self.params['bounding_box']
                    }
                }, fh)

    def get_cached_study_data_path(self):
        ((x0, x1), (y0, y1), (z0, z1)) = self.params['bounding_box']
        start, end = self.get_start_end_times()
        return Path("data/cache") / f"simulation-{x0}-{x1}-{y0}-{y1}-{z0}-{z1}-{start}-{end}.json"

    def get_bounding_box_center(self):
        return [i0 + (i1 - i0) / 2 for i0, i1 in self.params['bounding_box']]

