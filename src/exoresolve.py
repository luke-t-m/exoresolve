from time import sleep
import subprocess
from datetime import time, datetime
import signal

SOMETIMES_TIME = time(19, 00)
SHUTDOWN_TIME = time(21, 00)
WAKEUP_TIME = time(4, 00)

DNS_IP = "1.1.1.1"

hovm = "/home/luke/.godscarp"
etc_conf = "/etc/dnsmasq.godscarp.conf"
always_files = [
    "/etc/hosts",
    "/etc/resolv.conf",
    "/etc/dnsmasq.conf",
    etc_conf,
]
sometimes_files = always_files + [
    f"{hovm}/godscarp.py",
    f"{hovm}/never.list",
    f"{hovm}/always.list",
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
            self.contents = gigaread(filename)

    def watch(self):
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
        if (not j.isalnum() and j != ".") or i == j == ".":
            return False
    return True


def parse_lines(raw):
    return [c for l in raw.strip().split("\n") if good_url(c := l.split("#")[0])]


def make_cfg(what, ip, urls):
    return "\n".join([f"{what}=/{url}/{ip}" for url in urls])


def white_cfg_from(filename):
    return make_cfg("server", DNS_IP, parse_lines(gigaread(filename)))


def main():
    catchable_sigs = set(signal.Signals) - {signal.SIGKILL, signal.SIGSTOP}
    for sig in catchable_sigs:
        signal.signal(sig, lambda *args: None)
    gigarun(["/usr/sbin/rmmod", "killhand"])
    gigarun(["/usr/sbin/insmod", f"{hovm}/killhand/killhand.ko"])

    always_watchers = make_watchers(always_files)
    sometimes_watchers = make_watchers(sometimes_files)
    harbinger_watcher = Watcher(f"{hovm}/harbinger")

    always_cfg = white_cfg_from(f"{hovm}/always.list")
    sometimes_cfg = always_cfg + "\n" * 3 + white_cfg_from(f"{hovm}/sometimes.list")
    always_watchers[etc_conf].update(always_cfg)
    sometimes_watchers[etc_conf].update(sometimes_cfg)

    while True:
        if harbinger_watcher.watch():
            always_cfg = white_cfg_from(f"{hovm}/always.list")
            sometimes_cfg = always_cfg + "\n" * 3 + white_cfg_from(f"{hovm}/sometimes.list")
            always_watchers[etc_conf].update(always_cfg)
            sometimes_watchers[etc_conf].update(sometimes_cfg)

        now = datetime.now().time()
        if is_time_between(SOMETIMES_TIME, SHUTDOWN_TIME, now):
            to_watch = sometimes_watchers
        else:
            to_watch = always_watchers

        for _, watcher in to_watch.items():
            if watcher.watch():
                gigarun(["systemctl", "restart", "dnsmasq.service"])
                gigarun(["killall", "firefox"])

        if is_time_between(SHUTDOWN_TIME, WAKEUP_TIME, now):
            for _, watcher in always_watchers.items():
                watcher.watch()
            gigarun(["shutdown", "now"])

        sleep(2)


main()