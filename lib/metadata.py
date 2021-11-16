import yaml
import pandas as pd
import numpy as np
from pathlib import Path
from subprocess import run
import re
import json
from dateutil import parser

METADATA_SUFFIX = ".meta.yaml"
AUDIO_FILE_TYPES = ["m4a", "mp4"]

def get_metadata_df(data_dir, time=None):
    """Builds a metadata dataframe.
    """
    metadata = []
    for f in Path(data_dir).glob("**/*" + METADATA_SUFFIX):
        md = get_media_metadata(f)
        metadata.append(md)
    df = pd.DataFrame.from_records(metadata)
    df = df[['observer', 'device', 'file_type', 'start', 'end', 'duration', 'path', 'metadata_path']]
    df = df.sort_values("start").reset_index(drop=True)
    if time:
        df = df[(df.start <= time) & (df.end >= time)]
    return df

def get_media_metadata(metadata_path):
    """Reads metadata from x.meta.yaml and infers additional metadata.
    """
    metadata_path = Path(metadata_path)
    md = yaml.safe_load(metadata_path.read_text())
    md["metadata_path"] = str(metadata_path)
    filepath = metadata_path.parent / metadata_path.name[:-len(METADATA_SUFFIX)]
    if filepath.exists():
        md["path"] = str(filepath)
        md["file_type"] = filepath.suffix[1:]
    if is_audio(filepath):
        audio_md = get_audio_metadata(filepath)
        md["start"] = md.get("start", audio_md.get("start"))
        md["duration"] = md.get("duration", audio_md.get("duration"))
    if md.get("start"):
        md["start"] = np.datetime64(md["start"])
    if isinstance(md.get("duration"), str):
        md["duration"] = ts2s(md["duration"])
    if md.get("start") and md.get("duration"):
        md["end"] = md["start"] + np.timedelta64(int(md["duration"]), 's')
    return md

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
    if md.get("start"):
        md["start"] = parser.parse(md["start"])
    if md.get("duration"):
        md['duration'] = float(md['duration'])
    return md

def ts2s(ts):
    "Convert duration timestamp (03:12:45) to seconds"
    try:
        h, m, s = ts.split(":")
        return int(h)*60*60 + int(m)*60 + int(s)
    except ValueError:
        m, s = ts.split(":")
        return int(m)*60 + int(s)

