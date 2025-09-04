# Документация по реализации Healthcheck для soter_market

---

## src/app/main.py

### Фрагмент:
```python
@app.get("/health", tags=["Healthcheck"])
async def healthcheck():
    return {"status": "ok"}
```
**Что делает:**
- Это публичный HTTP-эндпоинт `/health`.
- Возвращает статус 200 OK и JSON `{ "status": "ok" }`.
- Используется для проверки "живости" сервиса (healthcheck).
- Не требует авторизации, не зависит от базы данных, Redis и других сервисов.
- Может вызываться Docker, Kubernetes, мониторингом или вручную через браузер/curl.

### Фрагмент:
```python
EXCLUDED_PATHS = {
    ...
    "/health",  # Healthcheck теперь публичный
}

def _is_excluded_path(path: str) -> bool:
    ...
    return any(
        path.startswith(prefix)
        for prefix in ["/docs", "/redoc", "/static", "/auth", "/hello", "/health"]
    )
```
**Что делает:**
- Добавляет `/health` в список путей, которые не требуют авторизации.
- Благодаря этому, middleware не будет проверять токен для `/health`.
- Это важно, чтобы healthcheck всегда был доступен для Docker и мониторинга.

---

## docker-compose.yml

### Фрагмент:
```yaml
  market:
    ...
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 3
```
**Что делает:**
- Добавляет секцию healthcheck для сервиса приложения.
- Docker будет каждые 10 секунд отправлять запрос на `/health` внутри контейнера.
- Если сервис не отвечает 3 раза подряд, Docker считает контейнер "unhealthy" и может его перезапустить.
- Это важно для автоматического мониторинга и самовосстановления микросервиса.

---

## src/tests/integration_tests/test_health.py

### Фрагмент:
```python
@pytest.mark.asyncio
async def test_healthcheck(ac):
    response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```
**Что делает:**
- Интеграционный тест для эндпоинта `/health`.
- Проверяет, что ответ всегда 200 OK и JSON ровно `{ "status": "ok" }`.
- Гарантирует, что healthcheck работает корректно и публично.
- Использует асинхронный клиент (ac), который создаётся фикстурой.

---

## src/tests/conftest.py

### Фрагмент:
```python
def open_mock_json(model: str):
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(base_dir, f"mock_{model}.json")
    with open(file_path, encoding="utf-8") as file:
        return json.load(file)
```
**Что делает:**
- Вспомогательная функция для загрузки мок-данных из файлов.
- Используется для подготовки тестовой базы данных.
- Не влияет на работу healthcheck, но нужна для корректного запуска всех тестов.

---

## Зависимости и архитектура

- **main.py** зависит только от FastAPI и стандартных библиотек.
- **docker-compose.yml** зависит от наличия эндпоинта `/health` в приложении.
- **test_health.py** зависит от фикстуры асинхронного клиента и публичности `/health`.
- **conftest.py** и mock-файлы нужны для корректной работы всех тестов, но не влияют на сам healthcheck.

---

## Как это работает вместе
1. FastAPI-приложение поднимает эндпоинт `/health`.
2. Docker автоматически проверяет этот эндпоинт через healthcheck.
3. Интеграционный тест гарантирует, что `/health` всегда работает и публичен.
4. Если что-то ломается — healthcheck быстро покажет проблему, а Docker может перезапустить сервис.

---

## Для чего это нужно (простыми словами)
- **Healthcheck** — это "пульс" микросервиса. Если он отвечает — сервис жив.
- **Docker healthcheck** — автоматическая проверка, чтобы сервис не "завис" незаметно.
- **Тест** — гарантия, что healthcheck не сломается случайно при изменениях кода.
- **Публичность** — чтобы мониторинг и Docker всегда могли проверить сервис без авторизации.

---

**Если потребуется — могу добавить схему или картинку, как всё связано. Если что-то неясно — спрашивай!**
