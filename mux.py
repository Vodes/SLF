# ruff: noqa: F405 F403
from muxtools import *
from muxtools.subtitle.sub import LINES

def make_default_sign_style(sub: SubFile, style_name = "Default-Sign") -> SubFile:
    doc = sub._read_doc()
    styles = doc.styles
    for i, style in enumerate(doc.styles):
        if style.name == "Default":
            style.name = style_name
            styles[i] = style

    doc.styles = styles
    sub._update_doc(doc)

    def swap_styles(lines: LINES):
        for line in lines:
            if line.style == "Default":
                line.style = style_name
    return sub.manipulate_lines(swap_styles)

GJM_GANDHI_PRESET.append(edit_style(gandhi_default, "Default Alt"))

episode = int(input("Please enter an episode number: "))

setup = Setup(
    f"{episode:02d}",
    None,
    show_name="Shangri-La Frontier",
    out_name=R"$show$ - S01E$ep$ (BD 1080p HEVC) [Vodes]",
    mkv_title_naming=R"$show$ - S01E$ep$ - $title$",
    out_dir="Shangri-La Frontier S01 (BD 1080p HEVC) [Dual-Audio] [Vodes]",
    clean_work_dirs=False,
)
ep = setup.episode

premux = ensure_path(R"E:\Encoding Stuff\# Doing\Shangri\premux-new", None) / f"Shangri-La Frontier - {ep} (premux).mkv"

# Audio handling
delay = 0
if (delay_file := ensure_path(f"./audio/{ep}-post-trim-delay.txt", None)).exists():
    with open(delay_file, "r") as f:
        delay = int(f.readline().strip())

eng_amzn = AudioTrack(f"./audio/{ep}-en.eac3", "English 2.0 (Amazon)", "en", delay=delay)
ger_amzn = AudioTrack(f"./audio/{ep}-de.eac3", "German 2.0 (Amazon)", "de", delay=delay)

# Sub handling
eng_theater = SubFile(f"./subs/{ep}/eng-cr-theater.ass").change_layers()
eng_theater_signs = make_default_sign_style(eng_theater.copy().separate_signs(heuristics=True), "Default-Sign-CR")

eng_signs = SubFile(f"./subs/{ep}/eng-sunraku-signs.ass")
eng_signs = make_default_sign_style(eng_signs)

eng_full = SubFile(f"./subs/{ep}/eng-cr-dialogue.ass") \
    .change_layers() \
    .merge(eng_signs) \
    .merge(eng_theater)

eng_full_sunraku = SubFile(f"./subs/{ep}/eng-sunraku-dialogue.ass") \
    .restyle(GJM_GANDHI_PRESET) \
    .merge(eng_signs) \
    .merge(eng_theater)

eng_signs_only = eng_signs.merge(eng_theater_signs)

ger_full = SubFile([f"./subs/{ep}/ger-cr-dialogue.ass", f"./subs/{ep}/ger-cr-signs.ass"]).change_layers()
ger_signs = SubFile(f"./subs/{ep}/ger-cr-signs.ass")

fonts = [f.collect_fonts(use_system_fonts=False, error_missing=True) for f in (eng_full_sunraku, eng_full, ger_full)][-1]

if ep == "01":
    fonts.append(Chapters([
        (0, "Prologue"),
        (3861, "Opening"),
        (6018, "Episode"),
        (31472, "Epilogue"),
        (34117, "SLF Theater")
    ]))
elif ep == "13":
    fonts.append(Chapters([
        (0, "Intro"),
        (1008, "Opening"),
        (3165, "Part A"),
        (18390, "Part B"),
        (28952, "Ending"),
        (31097, "Epilogue"),
        (33039, "SLF Theater")
    ]))

mux(
    Premux(premux, mkvmerge_args="--no-global-tags" if ep != "13" else "--no-global-tags --no-chapters"), eng_amzn, ger_amzn,
    eng_full.to_track("English [Crunchyroll modified]", "en", True, False),
    eng_full_sunraku.to_track("English [Sunraku]", "en", False, False),
    eng_signs_only.to_track("English Signs/Songs", "en", False, True),
    ger_full.to_track("German [Crunchyroll]", "de", True, False),
    ger_signs.to_track("German Signs/Songs", "de", False, True),
    *fonts,
    tmdb=TmdbConfig(205050, 1, order=TMDBOrder.PRODUCTION)
)

setup.edit("out_dir", "Shangri-La Frontier S01 (BD 1080p AV1) [Dual-Audio] [MiniVodes]")
setup.edit("out_name", "$show$ - S01E$ep$ (BD 1080p AV1) [MiniVodes]")

if ep in ["01", "13"]:
    fonts = fonts[:-1]

mux(
    Premux(f"./mini-premux/Shangri-La Frontier - S01E{ep} (mini-premux).mkv"),
    eng_full.to_track("English [Crunchyroll modified]", "en", True, False),
    eng_full_sunraku.to_track("English [Sunraku]", "en", False, False),
    eng_signs_only.to_track("English Signs/Songs", "en", False, True),
    ger_full.to_track("German [Crunchyroll]", "de", True, False),
    ger_signs.to_track("German Signs/Songs", "de", False, True),
    *fonts,
    tmdb=TmdbConfig(205050, 1, order=TMDBOrder.PRODUCTION)
)