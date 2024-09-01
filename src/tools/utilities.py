import time
import os
import findDevices
import RFFunctions as tools
import Clicker

#-----------------Start Log Tailing ----------------#
def logTail(my_clicker, capture_log="./captures/capturedClicks.log", verbose=False):
    """This function acts like the Linux tail command, pulling new additions to a file 
    since it started running. It parses for payload lines used in analysis and graphing.

    Args:
        my_clicker (Clicker): The Clicker instance used for signal analysis.
        capture_log (str): The path to the capture log file.
        verbose (bool): If True, prints detailed information during execution.
    """
    try:
        with open(capture_log, 'r') as file:
            # Find the size of the file and move to the end
            st_size = os.stat(capture_log).st_size
            file.seek(st_size)

            while True:
                where = file.tell()
                line = file.readline()
                if not line:
                    time.sleep(1)
                    file.seek(where)
                else:
                    if "found" not in line:
                        presses = tools.parseSignalsLive(line)
                        my_clicker.keyfob_payloads = presses
                        percent = my_clicker.liveClicks()
                        if verbose:
                            print(f"Processed line: {line.strip()}")
                            print(f"Click match percentage: {percent}")
    except Exception as e:
        print(f"Error in logTail function: {e}")

#-----------------End Log Tailing ----------------#


#-----------------Start De Bruijn Creation ----------------#
def deBruijn(k, n):
    """This function creates the de Bruijn sequence for brute force attacks 
    of various lengths n. Example code acquired from de-bruijn wiki.

    Args:
        k (int or str): The alphabet size or the alphabet itself.
        n (int): The length of the sequences to generate.

    Returns:
        str: The de Bruijn sequence.
    """
    try:
        _ = int(k)
        alphabet = list(map(str, range(k)))

    except (ValueError, TypeError):
        alphabet = k
        k = len(k)

    a = [0] * k * n
    sequence = []

    def db(t, p):
        if t > n:
            if n % p == 0:
                sequence.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return "".join(alphabet[i] for i in sequence)

#-----------------End De Bruijn Creation ----------------#
