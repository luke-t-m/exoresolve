from time import sleep
import subprocess
from datetime import time, datetime
import signal

SOMETIMES_TIME = time(19, 00)
SHUTDOWN_TIME = time(21, 00)
WAKEUP_TIME = time(4, 00)

DNS_IP = "1.1.1.1"
hovm = "/usr/local/exoresolve"
dnsmasq_conf = f"{hovm}/dnsmasq.conf"

always_files = [
    "/etc/resolv.conf",
    "/etc/dnsmasq.conf",
    dnsmasq_conf,
    f"{hovm}/lists/never.list",
    "/etc/hosts",
]
sometimes_files = always_files + [
    f"{hovm}/exoresolve.py",
    f"{hovm}/lists/always.list",
    f"{hovm}/lists/sometimes.list",
    "/etc/rc.local",
]


def gigaread(filename):
    try:
        with open(filename) as file:
            contents = file.read()
    except Exception:
        contents = ""
    return contents


def gigawrite(filename, contents):
    gigarun(["chattr", "-ia", filename])
    with open(filename, "w") as file:
        file.write(contents)


def gigarun(args):
    try:
        subprocess.run(args)
    except Exception:
        pass


class Watcher:
    def __init__(self, filename, contents=None):
        self.filename = filename
        if contents:
            self.contents = contents
        else:
            self.contents = None

    def watch(self):
        if self.contents is None:
            self.update(gigaread(self.filename))

        if gigaread(self.filename) != self.contents:
            gigawrite(self.filename, self.contents)
            return True
        return False

    def update(self, new_contents):
        self.contents = new_contents


def is_time_between(begin, end, time):
    if begin < end:
        return time >= begin and time <= end
    else:  # it's midnight!
        return time >= begin or time <= end


def make_watchers(filenames_list):
    return {filename: Watcher(filename) for filename in filenames_list}


def good_url(url):
    if len(url) == 0 or not url[0].isalnum() or not url[-1].isalnum():
        return False
    for i, j in zip(url[:-1], url[1:]):
        if (not j.isalnum() and j not in ".-") or i == j == ".":
            return False
    return True


def parse_lines(raw):
    return [c for l in raw.strip().split("\n") if good_url(c := l.split("#")[0])]


def make_cfg(what, ip, urls):
    return "\n".join([f"{what}=/{url}/{ip}" for url in urls])


def white_cfg_from(filename):
    return make_cfg("server", DNS_IP, parse_lines(gigaread(filename)))


def main():
    # Make all catchable signal's handlers do nothing.
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, lambda *args: None)
    # Load in killhand module which finds this process and overwrites the supposedly "uncatchable" signals' handlers.
    gigarun(["/usr/sbin/rmmod", "killhand"])
    gigarun(["/usr/sbin/insmod", f"{hovm}/killhand.ko"])
    gigarun(["/usr/sbin/rmmod", "killhand"])
    # Disable module loading till reboot.
    #gigawrite("/proc/sys/kernel/modules_disabled", "1")

    always_watchers = make_watchers(always_files)
    sometimes_watchers = make_watchers(sometimes_files)
    harbinger_watcher = Watcher(f"{hovm}/harbinger")

    always_cfg = "address=/#/127.0.0.1\n" + white_cfg_from(f"{hovm}/lists/always.list")
    sometimes_cfg = always_cfg + "\n" * 3 + white_cfg_from(f"{hovm}/lists/sometimes.list")
    always_watchers[dnsmasq_conf].update(always_cfg)
    sometimes_watchers[dnsmasq_conf].update(sometimes_cfg)

    while True:
        if harbinger_watcher.watch():
            always_cfg = white_cfg_from(f"{hovm}/lists/always.list")
            sometimes_cfg = always_cfg + "\n" * 3 + white_cfg_from(f"{hovm}/lists/sometimes.list")
            always_watchers[dnsmasq_conf].update(always_cfg)
            sometimes_watchers[dnsmasq_conf].update(sometimes_cfg)

        now = datetime.now().time()
        if is_time_between(SOMETIMES_TIME, SHUTDOWN_TIME, now):
            to_watch = sometimes_watchers
        else:
            to_watch = always_watchers

        for _, watcher in to_watch.items():
            if watcher.watch():
                gigarun(["systemctl", "restart", "dnsmasq.service"])
                gigarun(["killall", "firefox"])
                gigarun(["killall", "chrome"])

        if is_time_between(SHUTDOWN_TIME, WAKEUP_TIME, now):
            for _, watcher in always_watchers.items():
                watcher.watch()
            gigarun(["shutdown", "now"])

        sleep(2)


main()
