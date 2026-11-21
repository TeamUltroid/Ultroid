import sys
import time

# Stands in for the bot: says how it was started, later for a later client.
time.sleep(0.4 * (int(sys.argv[-1]) - 1))
print("client started with", sys.argv[1:], flush=True)
sys.exit(3 if sys.argv[1] == "fail" else 0)
