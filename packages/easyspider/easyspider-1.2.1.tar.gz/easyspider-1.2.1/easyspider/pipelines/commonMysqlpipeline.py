# -*- coding: utf-8 -*-
# @Author: hang.zhang
# @Date:   2018-03-05 19:10:07
# @Last Modified by:   hang.zhang
# @Last Modified time: 2018-03-05 20:44:27
import json
import time
import logging
import hashlib
from DBService import MysqlService
from twisted.internet.threads import deferToThread
from easyspider.pipelines.commonpipeline import commonpipeline
logger = logging.getLogger(__name__)


def md5_from_dict(item):
    """注意一个严重问题：！！
            Duplicate entry '001071' for key 'hash_check_item'")

            >>> md5_from_dict({"code": "001071"})
            '05e9ab87d2f88fbc29cf070b6241c0ea'
            >>> md5_from_dict({"code": u"001071"})
            '98f46fdaffc7e924e1c565c9f182ee6e'

    带不带u 差距巨大
    """
    sort_list = sorted(item.iteritems(), key=lambda x: x[0])
    # 全部统一成str
    sort_list = map(lambda s: map(str, s), sort_list)
    return hashlib.md5(str(sort_list)).hexdigest()

# insert_or_update 为了标志是否进行过操作，一定要加上一个时间的字段，必须要有时间


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


# class commonMysqlpipeline(object):
class commonMysqlpipeline(commonpipeline):

    def __init__(self, settings):
        self.mysql_host = settings.get("MYSQL_HOST")
        self.mysql_user = settings.get("MYSQL_USER")
        self.mysql_password = settings.get("MYSQL_PASSWORD")
        self.mysql_port = settings.get("MYSQL_PORT")
        self.mysql_db = settings.get("MYSQL_DB")
        self.mysql_table = settings.get("MYSQL_TABLE")

        self.server = MysqlService(
            self.mysql_host, self.mysql_user, self.mysql_password, self.mysql_port)
        self.server.select_db(self.mysql_db)

    @classmethod
    def from_settings(cls, settings):
        return cls(settings)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings)

    # def process_item(self, item, spider, response):
    #     d = deferToThread(self._process_item, item, spider, response)

    #     def error_back(err):
    #         # 既然出错，那么就要block_callback记录，重新放回起始队列
    #         r_copy = response.copy()
    #         r_copy.request.meta["easyspider"]["from_retry"] = 9999
    #         # 带上item 方便检查错误在哪
    #         msg = "Error processing %s ; %s" % (json.dumps(item), err.getTraceback())
    #         spider.put_back_2_start_url(response,
    #                                     exc_info=msg,
    #                                     )

    #     d.addErrback(error_back)
    #     return d

    def _process_item(self, item, spider, response):
        _save_item = item.copy()
        if not _save_item.get("save_mysql", True):
            return item
        _save_item.pop("crawled_urls_path")
        # _save_item.pop("crawled_url")
        _save_item.pop("spider")
        _save_item.pop("crawled_server")
        _save_item.pop("crawled_time")
        # 用什么校验，来防止重复插入
        hash_check_item = _save_item.pop("hash_check_item", None)
        self._insert_or_update(_save_item, spider, hash_check_item=hash_check_item)
        return item

    def _insert_or_update(self, item, spider, table=None, db=None, hash_check_item=None):
        if not hash_check_item:
            _hash_check_item = item
        else:
            _hash_check_item = {}
            for check_item in hash_check_item:
                _hash_check_item[check_item] = item.get(check_item)
        hash_code = md5_from_dict(_hash_check_item)

        if not table:
            # current_table = "%s.%s" % (self.mysql_db, self.mysql_table)
            current_table = self.mysql_table
        else:
            current_table = table
        if not db:
            current_db = self.mysql_db
        else:
            current_db = db
        hashcode_list = self.server.query('select id from %s.%s where hash_check="%s";' % (
            current_db, current_table, hash_code))
        if hashcode_list:
            record_id = hashcode_list[0].get("id")
            item["last_checktime"] = current_time()
            update_sql = self.server.update_sql_from_map(
                current_table, {"id": record_id}, item, current_db).replace("%", "%%")
            logger.debug(
                "already have record, update last_checktime, running sql is %s" % update_sql)
            self.server.execute(update_sql)
        else:
            item["hash_check"] = hash_code
            item["last_checktime"] = current_time()
            sql = self.server.join_sql_from_map(
                current_table, item, current_db).replace("%", "%%")
            logger.debug("find a new record, insert sql is %s" % sql)
            self.server.execute(sql)
