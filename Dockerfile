# Dockerfile

FROM python:3.10

WORKDIR /app

# Copy requirements.txt first and install dependencies
COPY requirements.txt .
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files in current folder to /app in container
COPY . .

EXPOSE 5000

CMD ["python", "app.py"]