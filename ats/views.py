import re

from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"


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
        if file.name == "snippet.md":
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
    return render(request, "ats/candidates.html", {})
