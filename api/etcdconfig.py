# -*- coding: utf-8 -*-
import etcd


class EtcdConfig(object):
    """
    @sumary 
    api of etcd service 
    """
    def __init__(self, key, value):
        self.connect = etcd.Client(host='10.107.12.4', port=2379) 
        self.key = key
        self.value = value

    def get_value(self):
        "get key of value"
        return self.connect.get(self.key).value

    def set_value(self):
        """
        @example
        self.connect.set('/backend/server/pay/C/117', '{"host":"10.108.5.55:9103", "weight":"20", "fails":"5", "timeout":"60"}')                
        """
        self.connect.set(self.key, self.value)
        #self.connect.write(self.key, self.value)
    
    def delete_value(self):
        """
        @example
	    self.connect.delete('/backend/server/app/C/117/00000000000000000007') 
        """
        self.connect.delete(self.key)

"""例子"""
"""
if __name__ == '__main__':
    etcd_config = EtcdConfig('/nginx/upstream/spay/HK/C/117/101', '{"host":"10.109.5.133:9118", "weight":"20", "fails":"5", "timeout":"60"}')
    #etcd_config = EtcdConfig('/nginx/upstream/pay/HK/C/117/101', '{"host":"10.108.5.54:9103", "weight":"20", "fails":"5", "timeout":"60"}')
    etcd_config.update_value()
    #new_value = etcd_config.get_value()
    #etcd_config.set_value()
"""