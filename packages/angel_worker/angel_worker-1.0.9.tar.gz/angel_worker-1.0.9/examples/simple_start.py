#! /usr/bin/env python
# -*- coding: utf-8 -*-
# @Time         2017-11-30
# @Email        2273337844@qq.com
# @Copyright    © 2017 Lafite93


if __name__ == "__main__":
    from angel_worker import worker
    worker.serve_forever(debug=True)
