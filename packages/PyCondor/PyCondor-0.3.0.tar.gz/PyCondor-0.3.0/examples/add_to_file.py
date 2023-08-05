#!/usr/bin/env python

import os
import datetime

filepath = os.path.abspath('test_file.txt')
with open(filepath, 'a') as f:
    datetime_str = datetime.datetime.now().strftime('%I:%M%p on %B %d, %Y')
    f.write(f'{datetime_str}\n')
