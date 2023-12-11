CONFIG_MODULE_SIG=n
CONFIG_MODULE_SIG_ALL=n

obj-m += killhand.o

PWD = $(CURDIR)

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules


clean:
	make -C /lib/modules/$(shell uname -r/build M=$(PWD) clean


