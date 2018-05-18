import pkg_resources
import sys

if sys.version_info < (3, 5):
    raise EnvironmentError("Python 3.5 or above is required")

from eth_account import Account  # noqa: E402
from enssubdomain.web3.main import Web3  # noqa: E402
from enssubdomain.web3.providers.rpc import (  # noqa: E402
    HTTPProvider,
)
from enssubdomain.web3.providers.eth_tester import (  # noqa: E402
    EthereumTesterProvider,
)
from enssubdomain.web3.providers.tester import (  # noqa: E402
    TestRPCProvider,
)
from enssubdomain.web3.providers.ipc import (  # noqa: E402
    IPCProvider,
)
from enssubdomain.web3.providers.websocket import (  # noqa: E402
    WebsocketProvider,
)

__version__ = pkg_resources.get_distribution("web3").version

__all__ = [
    "__version__",
    "Web3",
    "HTTPProvider",
    "IPCProvider",
    "WebsocketProvider",
    "TestRPCProvider",
    "EthereumTesterProvider",
    "Account",
]
