import threading
import time

from whatap.trace.trace_context_manager import TraceContextManager
from whatap.util.date_util import DateUtil
from whatap.util.hexa32 import Hexa32

from whatap.util.linked_map import LinkedMap
from resource import getrusage, RUSAGE_SELF


class TraceContext(object):
    transfer_id = None
    
    def __init__(self):
        self.host = ''
        self.elapsed = 0
        
        self.isStaticContents = 'false'
        
        self.id = TraceContextManager.getId()
        self.thread = threading.current_thread()
        self.thread_id = TraceContextManager.start(self, self.thread.ident)
        
        self.caller_pcode = 0
        self.caller_oid = 0
        self.caller_seq = 0
        
        self.start_time = 0
        self.start_cpu = 0
        self.start_malloc = 0
        
        self.status = 0
        
        self.service_hash = 0
        self.service_name = ''
        self.remoteIp = ''
        self.error = 0
        self.error_step = ''
        self.http_method = ''
        self.http_query = ''
        self.http_content_type = ''
        
        self.sql_count = 0
        self.sql_time = 0
        self.sql_insert = 0
        self.sql_update = 0
        self.sql_delete = 0
        self.sql_select = 0
        self.sql_others = 0
        
        self.executed_sqlhash = 0
        self.active_sqlhash = 0
        self.active_dbc = 0
        self.active_crud = 0
        
        self.httpc_checked = False
        self.httpc_count = 0
        self.httpc_time = 0
        self.httpc_url = ''
        
        self.active_httpc_hash = 0
        self.httpc_host = ''
        self.httpc_port = 0
        
        self.mtid = 0
        self.mdepth = 0
        self.mcaller = 0
        self.mcallee = 0
        
        self.userid = ''
        self.userAgent = 0
        self.userAgentString = ''
        self.referer = ''
        self.login = ''
        self.userTransaction = 0
        self.debug_sql_call = False
        self.lastSqlStep = None
        self.profileActive = 0
        
        self.jdbc_updated = False
        self.jdbc_update_record = 0
        self.jdbc_identity = 0
        self.jdbc_commit = 0
        self.resultSql = LinkedMap()
        
        self.rs_count = 0
        self.rs_time = 0
        self.db_opening = False
        
        self.lctx = {}
    
    def getElapsedTime(self, time=None):
        if not time:
            time = DateUtil.now()
        return time - self.start_time
    
    def getCpuTime(self):
        return int(time.clock_gettime(time.CLOCK_REALTIME))
    
    def getMemory(self):
        # https://docs.python.org/3/library/resource.html?highlight=resource#resource-usage
        return int(getrusage(RUSAGE_SELF)[3] + getrusage(RUSAGE_SELF)[4])
    
    def resetStartTime(self):
        self.start_time = 0
    
    def transfer(self):
        if self.transfer_id:
            return self.transfer_id
        
        sb = []
        sb.append(Hexa32.toString32(self.mtid))
        sb.append(str(self.mdepth + 1))
        sb.append(Hexa32.toString32(self.id))
        transfer_id = ','.join(sb)
        return transfer_id
    
    def setTransfer(self, key):
        x = key.index(',')
        if x:
            self.mtid = Hexa32.toLong32(key[0:x])
            y = key.index(',', x + 1)
            if y:
                self.mdepth = int(key[x + 1:y])
                self.mcaller = Hexa32.toLong32(key[y + 1:])
    
    def setTxid(self, myid):
        self.id = Hexa32.toLong32(myid)
