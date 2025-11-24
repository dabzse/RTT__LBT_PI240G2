import os
import re

from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.http import FileResponse, Http404

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"
SNIPPET_NAME = "snippet.md"


def _read_job_title(job_md_path: Path) -> str:
    """Return the first non-empty line of a job markdown as a cleaned title."""
    try:
        text = job_md_path.read_text(encoding="utf-8")
        first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
        return first_line.lstrip('#').strip()
    except (OSError, UnicodeDecodeError):
        return job_md_path.stem


def _list_submissions_for(job_id: str) -> list:
    """Return a list of submission dicts for `jobs/<job_id>/`.

    Each item is {name, url} where url is the public path used by the template.
    """
    subs = []
    subs_dir = JOBS_DIR / job_id
    if not (subs_dir.exists() and subs_dir.is_dir()):
        return subs

    for sub in sorted(subs_dir.iterdir()):
        if sub.is_file():
            subs.append({
                "name": sub.name,
                "url": f"/jobs/{job_id}/{sub.name}",
                "classification": classify_submission(sub),
            })
    return subs


def classify_submission(path: Path) -> str:
    """Classify a submission file as 'good', 'maybe', or 'bad'.

    Rules:
    - If extension is .pdf and the PDF appears to contain selectable text (heuristic), return 'good'.
      If the PDF appears to be image-only (scanned), return 'bad'.
    - If extension is one of readable types (doc, docx, odt, xls, xlsx, ods, ppt, pptx, odp, md, html, txt), return 'maybe'.
    - Otherwise return 'bad'.

    This uses a lightweight heuristic for PDFs to avoid heavy dependencies.
    """
    try:
        suffix = path.suffix.lower().lstrip('.')
    except Exception:
        return 'bad'

    readable = {"doc", "docx", "odt", "xls", "xlsx", "ods", "ppt", "pptx", "odp", "md", "html", "txt"}

    if suffix == 'pdf':
        # Heuristic: inspect the first N bytes for text operators or font objects.
        try:
            with open(path, 'rb') as f:
                data = f.read(65536)  # read first 64KB
        except Exception:
            return 'bad'

        # If we find font or text operators, assume PDF contains selectable text
        text_indicators = [b'/Font', b'/Type /Font', b'BT', b'Tj', b'Tf']
        image_indicators = [b'/XObject', b'/Subtype /Image', b'/Image', b'/Filter /DCTDecode', b'/JPXDecode']

        has_text = any(tok in data for tok in text_indicators)
        has_image = any(tok in data for tok in image_indicators)

        # If text found -> good. If only images -> bad. If ambiguous, prefer 'bad' conservatively.
        if has_text and not has_image:
            return 'good'
        if has_image and not has_text:
            return 'bad'
        # ambiguous: check for presence of long stretches of ASCII text
        try:
            ascii_ratio = sum(1 for b in data if 32 <= b < 127) / max(1, len(data))
        except Exception:
            ascii_ratio = 0
        if ascii_ratio > 0.25:
            return 'good'
        return 'bad'

    if suffix in readable:
        return 'maybe'

    return 'bad'


def home(request):
    snippet_html = load_snippet()
    return render(request, "ats/home.html", {"snippet_html": snippet_html})

@csrf_exempt
def ajax_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "Hibás hitelesítés!"})
    return JsonResponse({"success": False, "error": "Érvénytelen kérés."})


# def login_view(request):
#     if request.method == "POST":
#         username = request.POST.get("username")
#         password = request.POST.get("password")
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             messages.info(request, "Sikeres bejelentkezés.")
#             return render(request, "ats/home.html", {})
#         else:
#             messages.error(request, "Érvénytelen bejelentkezési adatok.")
#         return render(request, "ats/login.html", {})


def logout_view(request):
    logout(request)
    messages.info(request, "Sikeres és biztonságos kijelentkezés.")
    return redirect("home")


def jobs_list(request):
    """Összes álláshirdetés kilistázása"""
    jobs = []
    for file in JOBS_DIR.glob("[0-9]*-*.md"):
        if file.name == SNIPPET_NAME:
            continue
        job_id = file.stem.split("-")[0].strip("[]")
        try:
            text = file.read_text(encoding="utf-8")
            first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
            title = first_line.lstrip('#').strip()
        except (OSError, UnicodeDecodeError):
            title = file.stem

        jobs.append({
            "id": job_id,
            "filename": file.name,
            "title": title,
        })

    try:
        jobs.sort(key=lambda j: int(j['id']))
    except (ValueError, TypeError):
        pass
    return render(request, "ats/jobs.html", {"jobs": jobs})


def job_detail(request, job_id=None):
    """Egy adott álláshirdetés részlete"""
    snippet_html = load_snippet()

    if job_id is None:
        context = {
            "job": None,
            "content": f"<h1>Nincs álláshirdetés kiválasztva</h1>{snippet_html}",
        }
        return render(request, "ats/job.html", context)

    job_files = list(JOBS_DIR.glob(f"{job_id}-*.md"))
    if not job_files:
        context = {
            "job": None,
            "content": snippet_html,
        }
        return render(request, "ats/job.html", context)

    job_file = job_files[0]
    raw = job_file.read_text(encoding="utf-8")
    lines = raw.splitlines()
    first_index = None
    for idx, ln in enumerate(lines):
        if ln.strip():
            first_index = idx
            break

    if first_index is None:
        position = job_file.stem
        body_md = ""
    else:
        position = lines[first_index].lstrip('#').strip() or job_file.stem
        rest = lines[first_index+1:]
        if rest and not rest[0].strip():
            rest = rest[1:]
        body_md = "\n".join(rest).strip()

    def _normalize_nested_lists(md_text: str) -> str:
        """2/4 szóközös beágyazott listák normalizálása"""
        if not md_text:
            return md_text

        lines = md_text.splitlines()
        out_lines = []
        in_fence = False
        fence_re = re.compile(r'^```')
        for ln in lines:
            if fence_re.match(ln):
                in_fence = not in_fence
                out_lines.append(ln)
                continue
            if in_fence:
                out_lines.append(ln)
                continue

            m = re.match(r'^( {2})([-*+]\s+)(.*)$', ln)
            if m:
                out_lines.append('    ' + m.group(2) + m.group(3))
                continue
            m2 = re.match(r'^( {2})(\d+\.\s+)(.*)$', ln)
            if m2:
                out_lines.append('    ' + m2.group(2) + m2.group(3))
                continue

            out_lines.append(ln)

        return "\n".join(out_lines)

    if body_md:
        body_md = _normalize_nested_lists(body_md)
    content = markdown.markdown(body_md, extensions=["extra", "sane_lists"]) if body_md else ""

    context = {
        "job": job_id,
        "position": position,
        "content": content + snippet_html,
    }
    return render(request, "ats/job.html", context)


def load_snippet():
    snippet_file = JOBS_DIR / "snippet.md"
    if snippet_file.exists():
        raw = snippet_file.read_text(encoding="utf-8")
        def _normalize(md_text: str) -> str:
            if not md_text:
                return md_text
            lines = md_text.splitlines()
            out_lines = []
            in_fence = False
            fence_re = re.compile(r'^```')
            for ln in lines:
                if fence_re.match(ln):
                    in_fence = not in_fence
                    out_lines.append(ln)
                    continue
                if in_fence:
                    out_lines.append(ln)
                    continue
                m = re.match(r'^( {2})([-*+]\s+)(.*)$', ln)
                if m:
                    out_lines.append('    ' + m.group(2) + m.group(3))
                    continue
                m2 = re.match(r'^( {2})(\d+\.\s+)(.*)$', ln)
                if m2:
                    out_lines.append('    ' + m2.group(2) + m2.group(3))
                    continue
                out_lines.append(ln)
            return "\n".join(out_lines)

        normalized = _normalize(raw)
        return markdown.markdown(normalized, extensions=["extra", "sane_lists"])
    return "<p>(üres)</p>"


def candidates_list(request):
    """Listázza az álláshirdetéseket és a hozzájuk érkezett fájlokat (jelentkezéseket).

    Minden `jobs/[id]-*.md` fájl első nem-üres sora a pozíció neve.
    A `jobs/<id>/` könyvtár tartalmát megszámoljuk és felsoroljuk kattintható linkként.
    """
    jobs_info = []
    for file in JOBS_DIR.glob("[0-9]*-*.md"):
        if file.name == SNIPPET_NAME:
            continue
        job_id = file.stem.split("-")[0].strip("[]")
        # skip special ambiguous buckets here; we'll handle them separately
        if job_id in ("00", "0"):
            continue
        try:
            text = file.read_text(encoding="utf-8")
            first_line = next((ln for ln in text.splitlines() if ln.strip()), "")
            title = first_line.lstrip('#').strip()
        except (OSError, UnicodeDecodeError):
            title = file.stem

        # submissions directory is jobs/<id>/
        subs_dir = JOBS_DIR / job_id
        submissions = []
        if subs_dir.exists() and subs_dir.is_dir():
            for sub in sorted(subs_dir.iterdir()):
                if sub.is_file():
                    submissions.append({
                        "name": sub.name,
                        "url": f"/jobs/{job_id}/{sub.name}",
                    })

            # compute classification counts from submissions
            good = sum(1 for s in submissions if s.get("classification") == "good")
            maybe = sum(1 for s in submissions if s.get("classification") == "maybe")
            bad = sum(1 for s in submissions if s.get("classification") == "bad")

            jobs_info.append({
                "id": job_id,
                "title": title,
                "submissions_count": len(submissions),
                "submissions": submissions,
                "submissions_good_count": good,
                "submissions_maybe_count": maybe,
                "submissions_bad_count": bad,
            })

    try:
        jobs_info.sort(key=lambda j: int(j['id']))
    except (ValueError, TypeError):
        pass

    # Build ambiguous buckets separately for jobs/00 and jobs/0
    ambiguous_00 = None
    ambiguous_0 = None

    subs_00 = _list_submissions_for("00")
    if subs_00:
        ambiguous_00 = {
            "id": "00",
            "title": "Nem teljesen tisztázott",
            "submissions_count": len(subs_00),
            "submissions": subs_00,
            "submissions_good_count": sum(1 for s in subs_00 if s.get("classification") == "good"),
            "submissions_maybe_count": sum(1 for s in subs_00 if s.get("classification") == "maybe"),
            "submissions_bad_count": sum(1 for s in subs_00 if s.get("classification") == "bad"),
        }

    subs_0 = _list_submissions_for("0")
    if subs_0:
        ambiguous_0 = {
            "id": "0",
            "title": "0 (előző ver.)",
            "submissions_count": len(subs_0),
            "submissions": subs_0,
            "submissions_good_count": sum(1 for s in subs_0 if s.get("classification") == "good"),
            "submissions_maybe_count": sum(1 for s in subs_0 if s.get("classification") == "maybe"),
            "submissions_bad_count": sum(1 for s in subs_0 if s.get("classification") == "bad"),
        }

    return render(request, "ats/candidates.html", {"jobs": jobs_info, "ambiguous_00": ambiguous_00, "ambiguous_0": ambiguous_0})


def job_download(_request, job_id, filename):
    """Serve a file from jobs/<job_id>/ safely.

    This is a small helper used by the candidates list links which point
    to `/jobs/<id>/<filename>`. It ensures path traversal isn't possible
    and returns a `FileResponse` for the file if present.
    """
    try:
        # build expected directory and file paths
        dir_path = (JOBS_DIR / str(job_id)).resolve()
        file_path = (JOBS_DIR / str(job_id) / filename).resolve()
    except Exception as exc:
        raise Http404("Fájl nem található") from exc

    # ensure file_path is inside dir_path
    sep = os.path.sep
    if not (str(file_path).startswith(str(dir_path) + sep) or str(file_path) == str(dir_path)):
        raise Http404("Érvénytelen útvonal")

    if not file_path.exists() or not file_path.is_file():
        raise Http404("Fájl nem található")

    return FileResponse(open(file_path, "rb"), as_attachment=False, filename=file_path.name)
