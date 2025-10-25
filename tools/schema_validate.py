#!/usr/bin/env python3
import sys, json

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def main():
    if len(sys.argv) < 3:
        print("usage: schema_validate.py <schema.json> <data.json|->", file=sys.stderr)
        sys.exit(1)
    try:
        import jsonschema
    except ImportError:
        print("ERROR: pip install jsonschema", file=sys.stderr)
        sys.exit(2)

    schema = load(sys.argv[1])
    data = json.load(sys.stdin) if sys.argv[2] == "-" else load(sys.argv[2])
    jsonschema.validate(instance=data, schema=schema)
    print("OK")

if __name__ == "__main__":
    main()
