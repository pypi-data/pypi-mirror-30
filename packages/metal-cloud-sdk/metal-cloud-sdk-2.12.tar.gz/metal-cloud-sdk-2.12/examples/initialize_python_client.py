import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from BSI.BSI import BSI
from JSONRPC.Plugins.Client.SignatureAdd import SignatureAdd
from JSONRPC.Plugins.Client.DebugLogger import DebugLogger
from BSI.BSIFilter import BSIFilter

class BSIClient(object):
    """
    """
    @staticmethod
    def init():
        strAPIKey = "00:pl34s3c0pyth34p1k3yfr0mth3bs14dm1n1nt3rf4c3" # the API key can be found in the interface myBigstep > Metal Cloud > API
        dictParams = {
            "strJSONRPCRouterURL": "https://fullmetal.bigstep.com/api"
        }

        """
        Instantiate the Python Client.
        """
        bsi = BSI.getInstance(
            dictParams,
            [
                SignatureAdd(strAPIKey, {}),
                DebugLogger(True, "DebugLogger.log"),
                BSIFilter()
            ]
        )

        return bsi