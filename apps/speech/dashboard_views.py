from django.shortcuts import render


def diagnostics_dashboard_view(request):
    """Render the diagnostics dashboard page."""
    return render(request, "diagnostics/dashboard.html")
