# -*- coding:utf-8 -*-
# Created by qinwei on 2017/11/13
#
import atexit
import queue
import threading
from time import sleep, time

from hunters.config import DEFAULT_BROWSER_CONFIG


class BrowserPool(object):
    """
    浏览器池
    用一个池来装连接, 提供给Spider
    """

    def __init__(self, browser_config=DEFAULT_BROWSER_CONFIG, init_count=5, max_count=20, min_idle=5, timeout=3):
        self._browser_config = browser_config
        self._init_count = init_count
        self._max_count = max_count
        self._min_idle = min_idle
        self._timeout = timeout
        self._pool = list()
        self._current_used_count = 0
        self._lock = threading.Lock()

        self.init_pool()

    def init_pool(self):
        for item in range(self._init_count):
            self._pool.append(self._browser_config.new_browser())

    def get(self):
        browser_ = None
        with self._lock:
            if len(self._pool) > 0:
                browser_ = self._pool.pop(0)
            elif self._current_used_count < self._max_count:
                browser_ = self._browser_config.new_browser()
            self._current_used_count += 1
        return browser_

    def return_resource(self, browser):
        self._pool.append(browser)
        self._current_used_count -= 1

    def close_all(self):
        for item in self._pool:
            item.close()
            item.quit()


class ResourcePool(object):
    """
    一个抽象的池, 对实现Factory接口的池
    """

    def __init__(self, factory=None, init_count=5, max_count=20, min_idle=5, timeout=3, init_pool=False):
        self._factory = factory
        self._init_count = init_count
        self._max_count = max_count
        self._min_idle = min_idle
        self._timeout = timeout
        self._pool = queue.Queue()
        self._current_used_count = 0
        self._resource_config = factory.config()
        self._lock = threading.Lock()
        self._init_lock = threading.RLock()
        self._is_init = init_pool
        self._resource_use = dict()
        self._resource_map = dict()

    def init_pool(self):
        for item in range(self._init_count):
            self._pool.put(self.new_instance())

        atexit.register(self.close_all)

    def new_instance(self):
        return self._factory.new_instance()

    def get(self):
        with self._init_lock:
            if not self._is_init:
                self.init_pool()
                self._is_init = True

        while True:
            resource = self._get()
            if resource is None:
                print("Wait For Resource thread[{}]".format(threading.current_thread().ident))
                sleep(1)
            else:
                return resource

    def _get(self):
        resource = None
        with self._lock:
            try:
                resource = self._pool.get_nowait()
            except queue.Empty:
                if self._current_used_count < self._max_count:
                    resource = self.new_instance()
                else:
                    return resource

            self._current_used_count += 1
            resource_id = self.___id_key(resource)
            self._resource_use.setdefault(resource_id, {"count": 0, "resource": resource, "last_time": time()})
            self._resource_use[resource_id]["count"] += 1
            self._resource_use[resource_id]["last_time"] = time()
            print("RESOURCE ID:{}, use:{}".format(resource_id, self._resource_use[resource_id]["count"]))
            for k, v in self._resource_use.items():
                print("ID:{}, COUNT:{}".format(k, v.get("count")))
            return resource

    @staticmethod
    def ___id_key(resource):
        return "id " + str(id(resource))

    def return_resource(self, browser):
        with self._lock:
            self._pool.put(browser)
            self._current_used_count -= 1

    def return_broken_resource(self, browser):
        # close broken resource
        self._resource_use.pop(self.___id_key(browser))
        self.close_item(browser)
        # create a new one to pool
        self.return_resource(self.new_instance())

    def close_all(self):
        self._factory.destroy_all(self._pool)

    def close_item(self, instance):
        self._factory.destroy(instance)
