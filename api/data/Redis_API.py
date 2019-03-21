# -*- coding=utf-8 -*-
import redis
from django.conf import settings


class RedisBase(object):
    REDIS_POOL = 10000
    
    @staticmethod
    def getRedisConnection(db):
        '''根据数据源标识获取Redis连接池'''
        if db==RedisBase.REDIS_POOL:
            args = settings.REDIS_KWARGS_LPUSH
            if settings.REDIS_LPUSH_POOL == None:
                settings.REDIS_LPUSH_POOL = redis.ConnectionPool(host=args.get('host'), port=args.get('port'), db=args.get('db'))
            pools = settings.REDIS_LPUSH_POOL  
        connection = redis.Redis(connection_pool=pools)
        return connection



class RedisAPI(object):	
    class AnsibleModel(object):
        @staticmethod
        def lpush(redisKey,data):
            try:
                redisConn = RedisBase.getRedisConnection(RedisBase.REDIS_POOL)
                redisConn.lpush(redisKey, data)
                redisConn = None 
            except:
                return False
        
        @staticmethod
        def rpop(redisKey):
            try:
                redisConn = RedisBase.getRedisConnection(RedisBase.REDIS_POOL)
                data = redisConn.rpop(redisKey) 
                redisConn = None
                return data    
            except:
                return False        
        @staticmethod
        def delete(redisKey):
            try:
                redisConn = RedisBase.getRedisConnection(RedisBase.REDIS_POOL)
                data = redisConn.delete(redisKey) 
                redisConn = None
                return data  
            except:
                return False  