"""
PC Control Agent - Main Entry Point
Usage: python agent.py "your command here"
       python agent.py  (interactive mode)
"""

import sys
from core.controller import PCController
from core.logger import AgentLogger

def main():
    logger = AgentLogger()
    controller = PCController(logger)

    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        result = controller.execute(command)
        print(f"[{'OK' if result['success'] else 'FAIL'}] {result['message']}")
    else:
        print("PC Control Agent — type 'exit' to quit\n")
        while True:
            try:
                command = input(">> ").strip()
                if command.lower() in ("exit", "quit"):
                    break
                if not command:
                    continue
                result = controller.execute(command)
                print(f"[{'OK' if result['success'] else 'FAIL'}] {result['message']}\n")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
