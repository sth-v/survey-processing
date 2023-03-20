# syntax=docker/dockerfile:1
FROM sthv/mmcore:amd64
WORKDIR /mmservice
COPY --link . .
ENV PYTHON="$MAMBA_ROOT_PREFIX/bin/python"
ENV PATH=$PATH:"$MAMBA_ROOT_PREFIX/bin/python"
ENV HASURA_GQL_ENDPOINT=https://viewer.contextmachine.online/v1/graphql
ENV CONFIGS_URL=http://storage.yandexcloud.net/box.contextmachine.space/share/configs/survey.yaml
RUN /usr/local/bin/_entrypoint.sh python -m pip install -r req.txt
CMD ["main.py"]

