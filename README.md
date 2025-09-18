# maria-pipeline

![CI](https://github.com/vlad181920/maria-pipeline/actions/workflows/ci.yml/badge.svg)

Самонавчальний пайплайн **Марія**:
- Thought pipeline з внутрішнім діалогом і оцінкою думок  
- Web Learn сервер із **clean-режимом** (HTML → чистий текст; теги `["web","clean"]`)  
- Запуск підагентів із **дедупом** і **файловим локом**  
- Нічні та **smoke** скрипти для швидкої перевірки

## Вимоги
- macOS, Python 3.10+ (рекомендовано venv)
- bash/zsh

## Швидкий старт
```bash
./tools/run_web_learn.sh
./tools/run_pipeline_daemon.sh
./tools/pipeline_status.sh
./tools/smoke.sh


Test PR at чт 18 вер 2025 19:49:48 CEST
