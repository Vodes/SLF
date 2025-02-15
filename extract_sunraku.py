# ruff: noqa: F405 F403
from muxtools import *
import os
import shutil
import re


STRIP_TAGS_REGEX = r'\{[^}]*\}'

REMOVE_HEADERS = [("Original Translation", None), ("Original Editing", None), ("Original Timing", None), ("Synch Point", None), ("Script Updated By", None), ("Update Details", None), ("Timer", None)]

DEFAULT_DIALOGUE_STYLES.append("Default Alt")

for i in range(1, 26):
    ep = f"{i:02d}"
    Setup(ep, None, clean_work_dirs=True, debug=False)
    info("Extracting EP" + ep)

    sunraku = GlobSearch(f"*Sunraku*Shangri-La Frontier - S01E{ep} *.mkv", dir=R"Z:\BDs\Sunraku SLF")

    eng = SubFile.from_mkv(sunraku, find_tracks(sunraku, lang="en", type=TrackType.SUB)[0].relative_id) \
        .set_headers((ASSHeader.LayoutResX, 1920), (ASSHeader.LayoutResY, 1080), (ASSHeader.YCbCr_Matrix, "TV.709"), *REMOVE_HEADERS)

    signs = eng.copy().separate_signs(heuristics=True)
    eng = eng.separate_signs(inverse=True, heuristics=True, print_heuristics=False)

    sub_dir = ensure_path(f"./subs/{ep}", None)
    sub_dir.mkdir(exist_ok=True, parents=True)

    shutil.move(eng.file, sub_dir / "eng-sunraku-dialogue.ass")
    shutil.move(signs.file, sub_dir / "eng-sunraku-signs.ass")
    