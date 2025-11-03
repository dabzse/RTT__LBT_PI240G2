from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

import markdown

BASE_DIR = Path(__file__).resolve().parent.parent
JOBS_DIR = BASE_DIR / "jobs"


def home(request):
    return render(request, "ats/home.html", {})

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
    return render(request, "ats/logout.html", {})


def jobs_list(request):
    """Összes álláshirdetés kilistázása"""
    jobs = []
    for file in JOBS_DIR.glob("[*-]*.md"):  # pl: [1-]backend.md
        if file.name == "snippet.md":
            continue
        job_id = file.stem.split("-")[0].strip("[]")
        jobs.append({
            "id": job_id,
            "filename": file.name,
            "title": file.stem,  # később az md első sorát is veheted
        })
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

    job_files = list(JOBS_DIR.glob(f"[{job_id}-]*.md"))
    if not job_files:
        context = {
            "job": None,
            "content": f"<h1>Nincs ilyen álláshirdetés</h1>{snippet_html}",
        }
        return render(request, "ats/job.html", context)

    job_file = job_files[0]
    content = markdown.markdown(job_file.read_text(encoding="utf-8"))
    context = {
        "job": job_id,
        "content": content + snippet_html,
    }
    return render(request, "ats/job.html", context)


def load_snippet():
    snippet_file = JOBS_DIR / "snippet.md"
    if snippet_file.exists():
        return markdown.markdown(snippet_file.read_text(encoding="utf-8"))
    return "<p>(üres)</p>"
