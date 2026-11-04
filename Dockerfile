FROM python:3.10-slim
RUN pip install --no-cache-dir pandas matplotlib
RUN useradd --create-home --uid 1000 sandbox
ENV MPLCONFIGDIR=/tmp/matplotlib
USER sandbox