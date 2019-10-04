#!/usr/bin/env python

import time
import pigpio
import sys

msg = sys.argv[1]

pi = pigpio.pi()

if not pi.connected:
   exit(0)

h = pi.spi_open(0, 40000)

stop = time.time() + 120.0

n = 0

while time.time() < stop:

   n += 1
   pi.spi_xfer(h, "This is message number {}\n".format(n))
   time.sleep(1)

pi.spi_close(h)

pi.stop()
