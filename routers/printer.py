# routers/printer.py
import sys

if sys.platform == "win32":
    from .print_windows import router
elif sys.platform.startswith("linux"):
    try:
        import cups  # Check if pycups is available
        from .print_linux import router
    except ImportError:
        from .print_stub import router
else:
    from .print_stub import router
