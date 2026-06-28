import base64
import json
import asyncio
import docker

from backend.api.languages.used_lang import LANGUAGE_CONFIGS
async def check_solution(code: str, input_data: list, language: str, tl: float = 2.0):
    if language not in LANGUAGE_CONFIGS:
        return {
            "verdict": "Container Error",
            "test_id": None,
            "detail": f"Язык '{language}' не поддерживается тестирующей системой."
        }

    cfg = LANGUAGE_CONFIGS[language]
    loop = asyncio.get_running_loop()
    local_client = docker.from_env()

    raw_template = cfg['template']
    full_script_text = raw_template.replace("{USER_CODE_PLACEHOLDER}", code)
    encoded_script = base64.b64encode(full_script_text.encode('utf-8')).decode('utf-8')

    container = None
    try:
        container = await loop.run_in_executor(None, lambda: local_client.containers.run(
            image=cfg['image'],
            command="sleep 300",
            network_disabled=True,
            mem_limit="256m",
            memswap_limit="256m",
            nano_cpus=250000000,
            detach=True,
        ))

        filename = f"runner.{cfg['extension']}"
        setup_cmd = f"sh -c \"echo '{encoded_script}' | base64 -d > {filename}\""
        await loop.run_in_executor(None, lambda: container.exec_run(cmd=setup_cmd))

        if cfg.get("compile_cmd"):
            compile_result = await loop.run_in_executor(
                None, lambda: container.exec_run(cmd=cfg["compile_cmd"])
            )
            if compile_result.exit_code != 0:
                return {
                    "verdict": "Compilation Error",
                    "test_id": None,
                    "detail": f"Ошибка компиляции:\n{compile_result.output.decode('utf-8')}"
                }

        for index, test in enumerate(input_data, start=1):
            args_dict = json.loads(test.input_data)

            plain_input = "\n".join(str(val) for val in args_dict.values()) + "\n"
            encoded_input = base64.b64encode(plain_input.encode('utf-8')).decode('utf-8')

            exec_command = f"sh -c \"echo '{encoded_input}' | base64 -d | timeout {tl} {cfg['run_cmd']}\""
            exec_result = await loop.run_in_executor(None, lambda: container.exec_run(cmd=exec_command))

            if exec_result.exit_code == 124:
                return {
                    "verdict": "Time Limit Exceeded",
                    "test_id": test.id,
                    "detail": f"Превышено время выполнения на тесте №{index} ({tl} сек.)"
                }
            if exec_result.exit_code == 137:
                return {
                    "verdict": "Time Limit Exceeded",
                    "test_id": test.id,
                    "detail": f"Исчерпан лимит памяти на тесте №{index}"
                }

            response = exec_result.output.decode('utf-8').strip()

            if exec_result.exit_code != 0:
                return {
                    "verdict": "Runtime Error",
                    "test_id": test.id,
                    "detail": f"Ошибка выполнения (Runtime Error). Лог: {response}"
                }

            if not response:
                return {
                    "verdict": "Runtime Error",
                    "test_id": test.id,
                    "detail": f"Контейнер вернул пустой ответ на тесте №{index}."
                }

            # Сравниваем чистый вывод программы с ожидаемым результатом напрямую
            user_output = response.strip()
            expected_output = str(test.expected_output).strip()

            if user_output != expected_output:
                return {
                    "verdict": "Wrong Answer",
                    "test_id": test.id,
                    "detail": f"Тест №{index} провален. Ожидалось: {expected_output}, Получено: {user_output}"
                }

        return {"verdict": "Accepted", "test_id": None, "detail": "Все тесты успешно пройдены!"}

    except Exception as e:
        return {"verdict": "Container Error", "test_id": None, "detail": str(e)}

    finally:
        if container:
            try:
                await loop.run_in_executor(None, container.kill)
            except Exception:
                pass
            try:
                await loop.run_in_executor(None, container.remove)
            except Exception:
                pass
