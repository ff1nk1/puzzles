LANGUAGE_CONFIGS = {
    "python": {
        "image": "python:3.13-slim",
        "extension": "py",
        "compile_cmd": None,  # Интерпретируемый язык
        "run_cmd": "python runner.py",
        "template": """
import sys

{USER_CODE_PLACEHOLDER}

if __name__ == '__main__':
    # Читаем аргументы из stdin построчно
    lines = [line.strip() for line in sys.stdin if line.strip()]
    if lines:
        # Так как типов мы не знаем, можно попытаться конвертировать в числа, если это возможно
        args = []
        for l in lines:
            try: args.append(int(l))
            except ValueError:
                try: args.append(float(l))
                except ValueError: args.append(l)
        
        # Вызываем функцию пользователя
        res = solution(*args)
        # Выводим в stdout только результат! А Python-бэкенд его прочитает
        print(res)
"""

    },
    "cpp": {
        "image": "gcc:14",  #
        "extension": "cpp",
        "compile_cmd": "g++ runner.cpp -o runner_bin",
        "run_cmd": "./runner_bin",
        "template": """
#include <iostream>

// Прототип. Мы предполагаем типы (или генерируем прототип динамически)
int solution(int a, int b); 

{USER_CODE_PLACEHOLDER}

int main() {
    int a, b;
    // Считываем чистые числа из stdin
    if (std::cin >> a >> b) {
        std::cout << solution(a, b) << std::endl;
    }
    return 0;
}
"""
    },
        "java": {
        "image": "eclipse-temurin:21-jdk-jammy",
        "extension": "java",
        "compile_cmd": "javac runner.java",
        "run_cmd": "java runner",
        "template": """
import java.util.Scanner;

public class runner {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);
        if (scanner.hasNextInt()) {
            int a = scanner.nextInt();
            int b = scanner.nextInt();
            
            // Теперь Solution находится снаружи, и этот вызов отработает идеально
            Solution userSolution = new Solution();
            System.out.println(userSolution.solution(a, b));
        }
    }
}

{USER_CODE_PLACEHOLDER}
"""


    }
}
