FROM mambaorg/micromamba
ENV OMEINFO_VERSION=2.0.0
COPY ./conda_requirements.yml /tmp/
COPY ./app /app
COPY omeinfo.py /app/
COPY ./kg_legend.txt /app/
COPY ./rurality_legend.txt /app/
WORKDIR "/app"
RUN micromamba install -y -n base -f /tmp/conda_requirements.yml
ARG MAMBA_DOCKERFILE_ACTIVATE=1
ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python3" ]
CMD [ "app.py" ]
