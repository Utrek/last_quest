#!/bin/bash

# Запуск тестов с покрытием
pytest --cov=shop --cov-report=term-missing --cov-report=html