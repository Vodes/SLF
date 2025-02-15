# ruff: noqa: F405 F403
from muxtools import *
from muxtools.subtitle.sub import LINES
import re
import shutil
from datetime import timedelta

STRIP_TAGS_REGEX = r'\{[^}]*\}'

def strip_long_ass_sign(sub: SubFile) -> SubFile:
    def process(lines: LINES) -> LINES:
        new_lines = []
        for line in lines:
            filtered = re.sub(STRIP_TAGS_REGEX, '', line.text).strip()
            filtered = filtered.casefold()
            if filtered == "SLF Theater".casefold() or filtered == "ShanFro-Theater".casefold():
                if (line.end - line.start) > timedelta(seconds=20):
                    info(f"Found long ass line at {line.start}: {line.text}")
                    continue
            new_lines.append(line)
        return new_lines

    return sub.manipulate_lines(process)

for file in GlobSearch("ger-cr-signs.ass", allow_multiple=True).paths:
    sub = strip_long_ass_sign(SubFile(file))
    shutil.move(sub.file, file)

for file in GlobSearch("eng-cr-theater.ass", allow_multiple=True).paths:
    sub = strip_long_ass_sign(SubFile(file))
    shutil.move(sub.file, file)