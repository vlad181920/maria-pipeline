# maria-pipeline

Самонавчальний пайплайн **Марія**:
- Thought pipeline з внутрішнім діалогом і оцінкою думок
- Web Learn сервер з **clean-режимом** (HTML → чистий текст; теги `["web","clean"]`)
- Запуск підагентів із **дедупом** і **файловим локом**
- Нічні та **smoke** скрипти для швидкої перевірки

## Вимоги
- macOS, Python 3.10+ (рекомендовано venv)
- bash або zsh

## Швидкий старт (macOS)
```bash
./tools/run_web_learn.sh
./tools/run_pipeline_daemon.sh
./tools/pipeline_status.sh
./tools/smoke.sh

