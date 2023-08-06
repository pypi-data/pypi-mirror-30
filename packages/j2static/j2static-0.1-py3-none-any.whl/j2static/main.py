#! /usr/bin/env python3

import pathlib
import shutil

from j2static import build

def find_all(dirpath):
    files = []
    for path in dirpath.iterdir():
        if path.is_file():
            files.append(path)
        else:
            files.extend( find_all(path) )
    return files

def generate(args, outdir='site/'):
    out_path = pathlib.Path(outdir)
    template_path = pathlib.Path(args.template_dir)

    generator = build.get_builder("html", args.template_dir)

    for path in find_all(template_path):
        relative_path = path.relative_to(template_path)
        out_file = out_path / relative_path
        if generator.filter(path):
            generator.generate(str(relative_path), out_file)
        elif path.is_file() and relative_path.name[0] != '_':
            out_file.parent.mkdir(exist_ok=True, parents=True)
            shutil.copy(path, out_file)
