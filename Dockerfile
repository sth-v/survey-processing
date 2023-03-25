# syntax=docker/dockerfile:1
FROM cr.yandex/crpfskvn79g5ht8njq0k/mmcore:latest
WORKDIR /mmservice
COPY --link . .
ENV PYTHON="$MAMBA_ROOT_PREFIX/bin/python"
ENV PATH=$PATH:"$MAMBA_ROOT_PREFIX/bin/python"
ENV STORAGE=http://storage.yandexcloud.net
ENV CONFIGS_URL=http://storage.yandexcloud.net/box.contextmachine.space/share/configs/survey.yaml
RUN /usr/local/bin/_entrypoint.sh python -m pip install -r req.txt
CMD ["main.py"]

