FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libcairo2 \
    libcairo2-dev \
    libpango1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-0 \
    libgdk-pixbuf2.0-dev \
    shared-mime-info \
    fonts-noto-color-emoji \
    && apt-get clean

COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . /app/

# Expose port
EXPOSE 8000

# Run the server
CMD ["gunicorn", "saleanalytic.wsgi:application", "--bind", "0.0.0.0:8000"]
