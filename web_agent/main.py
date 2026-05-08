"""
Web Agent - Entry Point
Usage: python main.py "your search query"
       python main.py  (interactive)
"""
import sys
from agent.controller import WebAgent

def main():
    agent = WebAgent()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        result = agent.run(query)
        print("\n" + "="*60)
        print(result)
    else:
        print("Web Agent — type 'exit' to quit\n")
        while True:
            try:
                query = input(">> ").strip()
                if query.lower() in ("exit", "quit"): break
                if not query: continue
                result = agent.run(query)
                print("\n" + "="*60)
                print(result)
                print("="*60 + "\n")
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    main()
