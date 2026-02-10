set shell := ['bash', '-cu']

default:
    @just --list

serve:
    @uv run main.py
