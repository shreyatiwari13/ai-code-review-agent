import sys
import traceback

sys.path.insert(0, "C:/Users/Admin/OneDrive/project/ai-code-review-agent")

try:
    import backend.main as m
    print("IMPORT_OK")
except Exception:
    traceback.print_exc()
    raise
