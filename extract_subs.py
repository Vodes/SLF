# ruff: noqa: F405 F403
from muxtools import *
import os
import shutil
import re
from vspreview import is_preview, set_output
from vsmuxtools import FileInfo
from muxtools.subtitle.sub import LINES
from muxtools.subtitle.basesub import _Line


STRIP_TAGS_REGEX = r'\{[^}]*\}'

REMOVE_HEADERS = [("Original Translation", None), ("Original Editing", None), ("Original Timing", None), ("Synch Point", None), ("Script Updated By", None), ("Update Details", None), ("Timer", None)]

episode = "25"

Setup(episode, None, clean_work_dirs=True, debug=False)

cr = ensure_path(R"F:\Sources\Shangri-La\CR", None) / f"[CR] Shangri-La Frontier - S01E{episode} [720p].mkv"
cr_trim = (-24, None)

amazon = ensure_path(R"F:\Sources\Shangri-La\Shangri-La.Frontier.S01.288p.AMZN.WEB-DL.DDP2.0.H.264", None) / f"Shangri-La.Frontier.S01E{episode}.288p.AMZN.WEB-DL.DDP2.0.H.264.mkv"
amazon_trim = (122 - 24, None)

premux = ensure_path(R"E:\Encoding Stuff\# Doing\Shangri\premux-new", None) / f"Shangri-La Frontier - {episode} (premux).mkv"

def split_into_theater_and_regular(sub: SubFile) -> tuple[SubFile, SubFile]:
    sub2 = sub.clean_extradata().clean_garbage().copy()
    sub2.file = sub2.file.rename(get_workdir() / "theater.ass")
    
    def theaterstuff(lines: LINES, keep: bool) -> LINES:
        start: _Line | None = None
        for line in lines:
            filtered = re.sub(STRIP_TAGS_REGEX, '', line.text).strip()
            filtered = filtered.casefold()
            if filtered == "SLF Theater!".casefold() or filtered == "ShanFro".casefold() or filtered == "SLF Mini".casefold():
                start = line
                break
        if start:
            info(f"Found theater start at {format_timedelta(start.start)}: {start.text}")
            return [line for line in lines if ((line.start >= start.start) if keep else (line.start < start.start))]
        
        info("No theater found!")
        return lines if not keep else []
    
    return (sub.manipulate_lines(lambda lines: theaterstuff(lines, False)), sub2.manipulate_lines(lambda lines: theaterstuff(lines, True)))

def fix_ep10(sub: SubFile) -> SubFile:
    def intersting_fax_removal(lines: LINES):
        for line in lines:
            if "0.1.2" in line.text:
                line.text = line.text.replace("fax0.1.2", "fax0.12")
                info(f"Found sussy fax line: {line.text}")
    
    return sub.manipulate_lines(intersting_fax_removal)

if is_preview():
    set_output(FileInfo(premux).src_cut, 0, "Premux")
    cr_src = FileInfo(cr, trim=cr_trim).src_cut.resize.Bicubic(1920, 1080)
    set_output(cr_src, 1, "CR")
    amzn_src = FileInfo(amazon, trim=amazon_trim).src_cut.resize.Bicubic(1920, 1080)
    set_output(amzn_src, 2, "Amazon")
else:
    eng_audio = do_audio(amazon, find_tracks(amazon, lang="en", type=TrackType.AUDIO)[0].relative_id, amazon_trim, output=f"./audio/{episode}-en")
    ger_audio = do_audio(amazon, find_tracks(amazon, lang="de", type=TrackType.AUDIO)[0].relative_id, amazon_trim, output=f"./audio/{episode}-de")

    if ger_audio.container_delay != 0:
        with open(f"./audio/{episode}-post-trim-delay.txt", "w") as f:
            f.write(str(ger_audio.container_delay))

    eng = (SubFile.from_mkv(cr, find_tracks(cr, lang="en", type=TrackType.SUB)[0].relative_id)
        .unfuck_cr()
        .resample(premux, use_arch=True)
        .restyle(GJM_GANDHI_PRESET)
        .set_headers((ASSHeader.LayoutResX, 1920), (ASSHeader.LayoutResY, 1080), (ASSHeader.YCbCr_Matrix, "TV.709"), *REMOVE_HEADERS)
    )
    ger = SubFile.from_mkv(cr, find_tracks(cr, lang="de", type=TrackType.SUB)[0].relative_id).unfuck_cr(alt_styles=["overlap"])
    ger = fix_ep10(ger)
    ger = (ger.resample(premux, use_arch=True)
        .restyle(GJM_GANDHI_PRESET)
        .set_headers((ASSHeader.LayoutResX, 1920), (ASSHeader.LayoutResY, 1080), (ASSHeader.YCbCr_Matrix, "TV.709"), *REMOVE_HEADERS)
        .purge_macrons()
    )

    # This just opens the sub in aegisub lol, shifting there just to be safe and to do a quick spot check
    os.startfile(ger.file)
    input("Shift german now")

    os.startfile(eng.file)
    input("Shift english now")

    eng, eng_theater = split_into_theater_and_regular(eng)

    sub_dir = ensure_path(f"./subs/{episode}", None)
    sub_dir.mkdir(exist_ok=True, parents=True)

    eng_signs = eng.copy().separate_signs(heuristics=True)
    eng = eng.separate_signs(heuristics=True, inverse=True, print_heuristics=False)
    shutil.move(eng.file, sub_dir / "eng-cr-dialogue.ass")
    shutil.move(eng_signs.file, sub_dir / "eng-cr-signs.ass")
    shutil.move(eng_theater.file, sub_dir / "eng-cr-theater.ass")

    ger_signs = ger.clean_garbage().clean_extradata().copy().separate_signs(heuristics=True)
    ger = ger.separate_signs(heuristics=True, inverse=True, print_heuristics=False)
    shutil.move(ger.file, sub_dir / "ger-cr-dialogue.ass")
    shutil.move(ger_signs.file, sub_dir / "ger-cr-signs.ass")
    

