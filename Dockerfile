# syntax=docker/dockerfile:1
FROM cr.yandex/crpfskvn79g5ht8njq0k/mmcore:latest
WORKDIR /mmservice
COPY $HOME/.aws /.aws
COPY --link . .
ENV PYTHON="$MAMBA_ROOT_PREFIX/bin/python"
ENV PATH=$PATH:"$MAMBA_ROOT_PREFIX/bin/python"
RUN /usr/local/bin/_entrypoint.sh python -m pip install -r req.txt
CMD ["main.py"]

