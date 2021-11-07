import yaml
import pandas as pd
from pathlib import Path
from dateutil import parser
from subprocess import run
import re
import json

METADATA_SUFFIX = ".meta.yaml"
AUDIO_FILE_TYPES = ["m4a", "mp4"]

def get_metadata_df(data_dir):
    metadata = []
    for f in Path(data_dir).glob("**/*" + METADATA_SUFFIX):
        md = yaml.safe_load(f.read_text())
        if "begin" in md: print(f)
        if md.get("start"):
            md["start"] = parser.parse(md["start"])
        md["metadata_path"] = str(f.relative_to(data_dir))
        filepath = f.parent / f.name[:-len(METADATA_SUFFIX)]
        if filepath.exists():
            md["path"] = str(filepath.relative_to(data_dir))
            md["file_type"] = filepath.suffix[1:]
        if is_audio(filepath):
            audio_md = get_audio_metadata(filepath)
            md["start"] = md.get("start", audio_md.get("start"))
            md["duration"] = md.get("duration", audio_md.get("duration"))
        if isinstance(md.get("duration"), str):
            md["duration"] = ts2s(md["duration"])
        metadata.append(md)
    return pd.DataFrame.from_records(metadata, )

def is_audio(filepath):
    "Checks whether a file is audio"
    return filepath.suffix[1:].lower() in AUDIO_FILE_TYPES

def get_audio_metadata(filepath):
    "Extracts encoded metadata from audio files"
    output = run(
        'ffprobe -v quiet -print_format json -show_format "{}"'.format(filepath.resolve()), 
        shell=True, 
        capture_output=True, 
        text=True
    )
    result = json.loads(output.stdout)
    md = {
        "start": result.get('format', {}).get('tags', {}).get('creation_time'),
        "duration": result.get('format', {}).get('duration')
    }
    if md.get("duration"):
        md['duration'] = float(md['duration'])
    return md

def ts2s(ts):
    "Convert duration timestamp (03:12:45) to seconds"
    h, m, s = ts.split(":")
    return int(h)*60*60 + int(m)*60 + float(s)
