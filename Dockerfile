# ── Stage: base image ──────────────────────────────────────────────────────
# We use the official slim Python image.
# "slim" = stripped-down Debian; smaller than the full image, no dev tools.
FROM python:3.12-slim

# ── Metadata ────────────────────────────────────────────────────────────────
LABEL maintainer="you@example.com"
LABEL description="Local Cash Flow Analyzer"

# ── Set working directory inside the container ──────────────────────────────
# Think of this as "cd /app" — all subsequent commands run from here.
WORKDIR /app

# ── Install Python dependencies ─────────────────────────────────────────────
# We copy requirements FIRST (before the script) so Docker can cache this
# layer. If you only change the .py file later, Docker won't re-run pip.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy the application code ────────────────────────────────────────────────
COPY cash_flow_analyzer.py .

# ── Default command ───────────────────────────────────────────────────────────
# This runs when you do: docker run <image>
CMD ["python", "cash_flow_analyzer.py"]
