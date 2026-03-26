FROM python:3.11-slim

# Install system dependencies: Chrome, fonts, ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg2 \
    unzip \
    ffmpeg \
    libass-dev \
    fonts-liberation \
    fonts-noto-cjk \
    fonts-noto \
    xvfb \
    x11vnc \
    novnc \
    websockify \
    fluxbox \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create directories
RUN mkdir -p output temp chrome_profile templates assets/bgm assets/sfx

# Generate BGM and SFX assets
RUN chmod +x assets/generate_assets.sh && bash assets/generate_assets.sh

# Expose ports: 8000 = Web UI, 6080 = noVNC
EXPOSE 8000 6080

# Entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
