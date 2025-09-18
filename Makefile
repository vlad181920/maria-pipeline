.PHONY: help run-web run-pipeline status smoke stop clean-caches

help:
\t@echo "Targets:"
\t@echo "  make run-web        - стартує web_learn"
\t@echo "  make run-pipeline   - стартує thought pipeline daemon"
\t@echo "  make status         - показує статуси"
\t@echo "  make smoke          - швидка перевірка (API + pipeline + список агентів)"
\t@echo "  make stop           - зупиняє daemon та web_learn"
\t@echo "  make clean-caches   - чистить __pycache__"

run-web:
\t./tools/run_web_learn.sh

run-pipeline:
\t./tools/run_pipeline_daemon.sh
\t./tools/pipeline_status.sh

status:
\t./tools/status_all.sh

smoke:
\t./tools/smoke.sh

stop:
\t./tools/stop_pipeline_daemon.sh || true
\t./tools/stop_web_learn.sh || true

clean-caches:
\tfind . -type d -name "__pycache__" -exec rm -rf {} +
