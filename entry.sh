

# shellcheck disable=SC2093
# shellcheck disable=SC2046
exec $(python mmservice/entrypoint "$PYTHON")
python main.py
