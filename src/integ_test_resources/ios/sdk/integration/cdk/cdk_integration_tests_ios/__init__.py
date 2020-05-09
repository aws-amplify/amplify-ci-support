import os
import sys

sys.path.append(
    os.path.join(
        # include the amplify-ci-support resources from the ./common dir.
        os.path.dirname(os.path.abspath(__file__)),
        "../../../../..",
    )
)
