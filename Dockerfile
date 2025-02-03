# Use a Python 3.11 image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core library that provides libgobject-2.0.so.0
    libglib2.0-0 \
    # This package provides libnssutil3.so, libsmime3.so, and libnss3.so
    libnss3 \
    # Also usually needed by Chrome/Chromium
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libx11-6 \
    libxcomposite1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxrandr2 \
    libxkbcommon0 \
    libgbm1 \
    libdrm2 \
    libxcb1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    fonts-liberation \
    # for display
    xvfb \
    xauth \
    && rm -rf /var/lib/apt/lists/*


# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
# (Caches and binds for optimal performance and reproducibility)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev


# Then, add the rest of the project source code and install it
# Installing separately from dependencies allows optimal layer caching
COPY browser_use/ /app/browser_use
ADD consumer.py /app
ADD app.py /app
ADD db.py /app
ADD uv.lock /app
ADD pyproject.toml /app
ADD .python-version /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

RUN patchright install chromium

# Reset the entrypoint, don't invoke `uv` automatically
ENTRYPOINT ["uv", "run", "consumer.py"]