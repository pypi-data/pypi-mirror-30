#!/usr/bin/env python3
#
# This file is part of sarracenia.
# The sarracenia suite is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2008-2015
#
# Questions or bugs report: dps-client@ec.gc.ca
# sarracenia repository: git://git.code.sf.net/p/metpx/git
# Documentation: http://metpx.sourceforge.net/#SarraDocumentation
#
# sr_audit.py : python3 program checking for bad exchange, queues... etc
#
#
# Code contributed by:
#  Michel Grenier - Shared Services Canada
#  Last Changed   : Feb  2 09:33:02 EST 2016
#
########################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, 
#  but WITHOUT ANY WARRANTY; without even the implied warranty of 
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA
#
#

import os,socket,sys,time,os.path

try :    
         from sr_amqp            import *
         from sr_instances       import *
         from sr_rabbit          import *
         from sr_util            import *
except : 
         from sarra.sr_amqp      import *
         from sarra.sr_instances import *
         from sarra.sr_rabbit    import *
         from sarra.sr_util      import *

class sr_audit(sr_instances):

    def add_exchange(self,e):
        self.logger.info("adding exchange '%s'" % e)
        self.hc.exchange_declare(e)

    def add_user(self,u,role):
        self.logger.info("adding user %s, reset: %s, set_passwords: %s" % (u, self.reset, self.set_passwords) )

        user_cred_qurl = self.admin.scheme + '://' + u + '@' + self.admin.hostname + '/'

        ok, details = self.credentials.get(user_cred_qurl)
        if not ok :
           self.logger.info("Entry missing for %s in %s" % ( user_cred_qurl, \
                   self.user_config_dir + os.sep + 'credentials.conf' ))
           return

        upw = details.url.password
         
        declare = "declare user name='%s' password=" % u
        if self.set_passwords:
            declare += "'%s' "  % upw

        if role == 'admin' :
           declare += " tags=administrator "
        else:
           declare += ' tags="" '

        dummy = run_rabbitmqadmin( self.admin,declare,self.logger )

        # admin and feeder gets the same permissions

        if role in ['admin,','feeder','manager']:
           # MG: before we had '.*' and it caused problem
           c="configure=.*"
           w="write=.*"
           r="read=.*"
           self.logger.info("permission user '%s' role %s  %s %s %s " % (u,'feeder',c,w,r))
           declare = "declare permission vhost=/ user='%s' %s %s %s"%(u,c,w,r)
           dummy = run_rabbitmqadmin( self.admin,declare,self.logger)
           return

        # source

        if role == 'source':
           c="configure='^q_%s.*|^xs_%s.*'" % ( u, u )
           w="write='^q_%s.*|^xs_%s.*'" % ( u, u )
           r="read='^q_%s.*|^x[lrs]_%s.*|^x.*public$'" % ( u, u )
           self.logger.info("permission user '%s' role %s  %s %s %s " % (u,'source',c,w,r))
           declare = "declare permission vhost=/ user='%s' %s %s %s"%(u,c,w,r)
           dummy = run_rabbitmqadmin( self.admin,declare,self.logger)
           # setting up default exchanges for a source
           self.hc.exchange_declare('xs_%s'%u)
           self.hc.exchange_declare('xr_%s'%u)
           # deprecated
           self.hc.exchange_declare('xl_%s'%u)
           return

        # PS asked not to implement this (Fri Mar  4 2016)
        # anonymous was special at a certain time ... historical reasons
        # anonymous should only be a subscribe... but it is a special case...
        # to work with old versions of subscribe : queue cmc* and configure permission on xpublic
        # this anonymous code will be deprecated at a certain point...

        #if u == 'anonymous' :
        #   c="configure='^q_%s.*|xpublic|^cmc.*$'"%u
        #   w="write='^q_%s.*|^xs_%s$|xlog|xreport|^cmc.*$'"%(u,u)
        #   r="read='^q_%s.*|^xr_%s$|xlog|xpublic|^cmc.*$'"%(u,u)
        #   self.logger.info("permission user %s role %s  %s %s %s " % (u,'source',c,w,r))
        #   declare = "declare permission vhost=/ user=%s %s %s %s"%(u,c,w,r)
        #   dummy = rabbitmqadmin( self.admin,declare,self.logger)
        #   return

        # subscribe

        if role == 'subscribe':
           c="configure='^q_%s.*'"%u
           w="write='^q_%s.*|^xs_%s$'"%(u,u)
           r="read='^q_%s.*|^x[lrs]_%s.*|^x.*public$'" % (u,u)
           self.logger.info("permission user '%s' role %s  %s %s %s " % (u,'source',c,w,r))
           declare = "declare permission vhost=/ user='%s' %s %s %s"%(u,c,w,r)
           dummy = run_rabbitmqadmin( self.admin,declare,self.logger )
           # setting up default exchanges for a subscriber
           self.hc.exchange_declare('xs_%s'%u)
           self.hc.exchange_declare('xr_%s'%u)
           # deprecated
           self.hc.exchange_declare('xl_%s'%u)
           return

    def close(self):
        self.logger.debug("sr_audit close")
        if self.hc :
           self.hc.close()
           self.hc = None

    def check(self):
        self.logger.debug("sr_audit check")

        self.hc = None

        # only one audit around
        self.nbr_instances = 1

        # audit must be user  admin
        self.pump_admin = hasattr(self,'admin')
        if not self.pump_admin :
           return

        # get other admins  users

        picked      = []
        self.admins = []
        self.logger.debug("users = %s" % self.users)
        for user in self.users :
            roles = self.users[user]
            if 'admin' in roles :
               self.admins.append(user)
               picked.append(user)

        # get feeder users

        self.feeders = []
        for user in self.users :
            roles = self.users[user]
            if 'feeder' in roles or 'manager' in roles and not user in picked :
               self.feeders.append(user)
               picked.append(user)

        # get source users

        self.sources = []
        for user in self.users :
            roles = self.users[user]
            if 'source' in roles and not user in picked :
               self.sources.append(user)
               picked.append(user)

        # get subscribe users

        self.subscribes = []

        for user in self.users :
            roles = self.users[user]
            if 'subscribe' in roles and not user in picked :
               self.subscribes.append(user)
               picked.append(user)

        # invalid roles left...
        for user in self.users :
            roles = self.users[user]
            if not user in picked :
                self.logger.error("unknown role '%s' for user '%s' " % (roles,user) )




    def delete_exchange(self,e):
        self.logger.info("deleting exchange %s" % e)
        self.hc.exchange_delete(e)

    def delete_queue(self,q):
        self.logger.info("deleting queue %s" % q)
        self.hc.queue_delete(q)

    def delete_user(self,u):
        self.logger.info("deleting user %s" % u)
        delete = "delete user name='%s'"%u
        dummy  = run_rabbitmqadmin( self.admin,delete,self.logger )

    def overwrite_defaults(self):
        self.logger.debug("sr_audit overwrite_defaults")
        self.sleep = 60

    def run_sr_setup(self):
        self.logger.debug("setting up exchanges and queues from all config")
        subprocess.check_call(['sr','declare'])
        subprocess.check_call(['sr','setup'])

    def verify_exchanges(self):
        self.logger.debug("sr_audit verify_exchanges")

        # get exchanges name (a list of dictionnaries)

        listdict = "list exchanges name"
        lst_dict = run_rabbitmqadmin( self.admin,listdict,self.logger )

        # loop build list of exchanges of interest
        # empty or rabbitmq-server defaults 'amq.' are taken off

        exchange_rab = ['amq.direct','amq.fanout','amq.headers','amq.match', \
                        'amq.rabbitmq.log','amq.rabbitmq.trace','amq.topic'  ]

        exchange_lst = []
        for edict in lst_dict :
            exchange = edict['name']
            if exchange == '' : continue
            # if you want sr_audit to get rid of rabbitmq-server amq.* default exchanges
            # just comment this next line
            if exchange in exchange_rab : continue
            exchange_lst.append(exchange)

        self.logger.info("sr_audit verify_exchanges, defined: %s" % lst_dict )

        for e in self.exchanges : 
            if e in exchange_lst :
               exchange_lst.remove(e)
               continue
            self.add_exchange(e)

        # all sources should have: xs_ and xr_"user"

        for u in self.sources+self.subscribes :
            
            tmp_lst = []
            tmp_lst.extend(exchange_lst)

            se = 'xs_' + u

            if not se in exchange_lst: self.add_exchange(se)
            
            for e in exchange_lst:
               if e.startswith(se) :  
                 if e != se : self.logger.warning("ok user source exchange %s" % e)
                 tmp_lst.remove(e)

            se = 'xr_' + u

            if not se in exchange_lst: self.add_exchange(se)

            for e in exchange_lst:
               if e.startswith(se) :  
                  if e != se : self.logger.warning("ok user report exchange %s" % e)
                  tmp_lst.remove(e)

            # remove once all users using version > 2.16.08a
            se = 'xl_' + u

            if not se in exchange_lst: self.add_exchange(se)

            for e in exchange_lst:
               if e.startswith(se) :  
                  if e != se : self.logger.warning("ok legacy user log exchange %s" % e)
                  tmp_lst.remove(e)

            exchange_lst = tmp_lst


        # all sources and subscribes should have: xs_"user"

        #for u in self.subscribes :
        #    se = 'xs_' + u
        #    self.add_exchange(e)

        #   for e in exchange_lst:
        #      if e.startswith(se) :  
        #         self.logger.warning("ok subscription exchange %s" % e)
        #         exchange_lst.remove(e)
                 

        # delete leftovers
        # MG : Peter specified that we may need other exchanges to work with 
        #      Such an exchange would be created manually and would start with 'x'
        #
        #      So  get rid of all exceeding 'xr_' 'xs_' exchanges as deprecated
        #      and get rid of all exchanges that do not start with 'x'

        for e in exchange_lst :

            # deprecated exchanges  (from deleted users?)
            if 'xs_' in e or 'xr_' in e or 'xl_' in e :
               self.logger.warning("exchange from no known user %s" % e)
               self.delete_exchange(e)

            # weird exchange... not starting with 'x'
            elif e[0] != 'x' :
               self.logger.warning("unknown exchange %s" % e)
               self.delete_exchange(e)

            # leading 'x' exchanges that might be there for a reason
            # leave but notify ...
            else:
               self.logger.info("noticed exchange %s leaving alone." % e)

    def verify_pulse(self):
        """
           Each pump should have a poll process that pulse a message to keep alive consuming processes
        """
        self.logger.info("sr_audit pulse configuration")

        if not self.admin :
           self.logger.warning("No pulse if no admin user set ")
           return 

        admin = self.admin.geturl()

        # remove the password from the URL...
        colon = admin.index(':',6)
        ampersand = admin.index('@',8)
        admin = admin[0:colon] + admin[ampersand:]

        self.logger.info("sr_audit pumps using account: %s for pulse" % admin )

        # poll directory must exists
        try    : os.makedirs(self.user_config_dir + "/poll", 0o775,True)
        except : pass

        cfn = self.user_config_dir + "/poll/pulse.conf"
        self.logger.info("sr_audit pulse configuration %s" % cfn )
        if not ( os.path.isfile(cfn) or os.path.isfile(cfn + ".off") ):
           self.logger.info("creating %s" % cfn ) 
           cf=open(cfn,'w')
           cf.write( '# Initial pulse emitting configuration, by sr_audit, tune to taste. \n')
           cf.write( '# To get original back, just remove this file, and run sr_audit (or wait a few minutes)\n' )
           cf.write( '# To suppress pulsing, rename this file to %s.off  \n\n' % os.path.basename(cfn) )
           cf.write( 'post_broker %s\n' % admin )
           cf.write( 'post_exchange xpublic\n')
           cf.write( 'do_poll poll_pulse\n' )
           cf.close()


    def verify_report_routing(self):
        """
           Each subscriber writes reports to xs_<user>.  These reports need to get back to sources.
           So for each subscriber, a shovel configuration is needed: that shovels from xs_<user> to xreport.
           For each source, a shovel configuration is needed that shovels from xreport to xr_<user>
           these configurations all need to be placed in the ~/.config/sarra/shovel directory.
           need to check if these files exist, and create only if they do not.
           also allow for the convention of .conf.off.  If such a file exists, do not create either.
        """
        self.logger.info("sr_audit report routing configuration")

        feeder = self.manager.geturl()

        # remove the password from the URL...
        colon = feeder.index(':',6)
        ampersand = feeder.index('@',8)
        feeder = feeder[0:colon] + feeder[ampersand:]

        self.logger.info("sr_audit pumps using account: %s for report routing" % feeder )

        # shovel directory must exists
        try    : os.makedirs(self.user_config_dir + "/shovel", 0o775,True)
        except : pass

        if self.report_daemons: 
           for u in self.sources :
             cfn = self.user_config_dir + "/shovel/rr_" + "xreport2" + u + ".conf"
             self.logger.info("sr_audit report routing configuration source: %s, shovel: %s" % ( u, cfn ) )
             if not ( os.path.isfile(cfn) or os.path.isfile(cfn + ".off") ):
                self.logger.info("creating %s" % cfn ) 
                cf=open(cfn,'w')
                cf.write( '# Initial report routing to sources configuration, by sr_audit, tune to taste. \n')
                cf.write( '#     To get original back, just remove this file, and run sr_audit (or wait a few minutes)\n' )
                cf.write( '#     To suppress report routing, rename this file to %s.off  \n\n' % os.path.basename(cfn) )
                cf.write( 'broker %s\n' % feeder )
                cf.write( 'exchange xreport\n' )
                cf.write( 'topic_prefix v02.report\n' )
                cf.write( 'subtopic #\n' )
                cf.write( 'accept_unmatch True\n' )
                cf.write( 'msg_by_source %s\n' % u  )
                cf.write( 'on_message msg_by_source\n' )
                cf.write( 'on_post None\n' )
                cf.write( 'report_back False\n' )
                cf.write( 'post_broker %s\n' % feeder )
                cf.write( 'post_exchange xr_%s\n' % u )
                cf.close()

           for u in self.sources+self.subscribes:
             cfn = self.user_config_dir + "/shovel/rr_" + u + "2xreport.conf"
             self.logger.info("sr_audit report routing configuration subscriber: %s, shovel: %s" % ( u, cfn ) )
             if not ( os.path.isfile(cfn) or os.path.isfile(cfn + ".off") ):
                self.logger.info("creating %s" % cfn ) 
                cf=open(cfn,'w')
                cf.write( '# Initial report routing configuration created by sr_audit, tune to taste.\n ')
                cf.write( '#     To get original back, just remove this file, and run sr_audit (or wait a few minutes)\n' )
                cf.write( '#     To suppress report routing, rename this file to %s.off  \n\n' % os.path.basename(cfn) )
                cf.write( 'broker %s\n' % feeder )
                cf.write( 'exchange xs_%s\n' % u )
                cf.write( 'topic_prefix v02.report\n' )
                cf.write( 'subtopic #\n' )
                cf.write( 'accept_unmatch True\n' )
                cf.write( 'msg_by_user %s\n' % u  )
                cf.write( 'on_message msg_by_user\n' )
                cf.write( 'on_post None\n' )
                cf.write( 'report_back False\n' )
                cf.write( 'post_broker %s\n' % feeder )
                cf.write( 'post_exchange xreport\n' )
                cf.close()


    def verify_users(self):
        self.logger.info("sr_audit verify_users")

        # get users name (a list of dictionnaries)

        listuser = "list users name"
        lst_dict = run_rabbitmqadmin( self.admin,listuser,self.logger )
        self.logger.info("sr_audit verify_users, defined: %s" % lst_dict )

        user_lst = []
        for edict in lst_dict :
            user = edict['name']
            if user == '' : continue
            user_lst.append(user)

        self.logger.info("sr_audit verify_users user_lst = %s" % user_lst)

        # admins

        self.logger.info("sr_audit verify_users admins = %s" % self.admins)
        for u in self.admins :
            if u in user_lst :
               user_lst.remove(u)
               if not self.reset:
                  continue
            self.add_user(u,'admin')

        # feeders

        self.logger.info("sr_audit verify_users feeders = %s" % self.feeders)
        for u in self.feeders:
            if u in user_lst :
               user_lst.remove(u)
               if not self.reset:
                  continue
            self.add_user(u,'feeder')

        # sources

        self.logger.info("sr_audit verify_users sources = %s" % self.sources)
        for u in self.sources :
            if u in user_lst :
               user_lst.remove(u)
               if not self.reset:
                  continue
            self.add_user(u,'source')

        # subscribes

        self.logger.info("sr_audit verify_users subscribes = %s" % self.subscribes)
        for u in self.subscribes:
            if u in user_lst :
               user_lst.remove(u)
               if not self.reset:
                  continue
            self.add_user(u,'subscribe')

        # delete leftovers
        for u in user_lst :
            self.logger.warning("unnecessary user %s" % u)
            self.delete_user(u)


    def verify_queues(self):
        self.logger.debug("sr_audit verify_queues")

        listq    = "list queues name messages state"
        lst_dict = run_rabbitmqadmin( self.admin,listq,self.logger )
        self.logger.debug("lst_dict = %s" % lst_dict)

        for edict in lst_dict :
            # skip empty name
            q = edict['name']
            if q == '' : continue
            # get queue size
            try    : qsize = int(edict['messages'])
            except : qsize = -1
            # FIXME MG : there is a problem with 'state'
            #            first : it is 'status' for older version of rabbitmq
            #            second: it is most of the time 'running' whatever the
            #                    state of the queue...
            #            so all queues are discarded (no further check)
            # skip running queue
            try    : s = edict['state']
            except : s= ''
            if s == 'running' :
               self.logger.debug("running queue %s (%d) discarded" % (q,qsize))
               continue
            self.logger.debug("verifying queue %s (%d)" % (q,qsize))

            # queue bigger than max_queue_size are deleted right away
            if qsize >= self.max_queue_size :
               self.logger.debug("queue too big %s (%d)" % (q,qsize))
               self.delete_queue(q)
               continue

            # queue name starting with cmc are tolerated for now
            # FIX ME, when sarra really well implemented/used delete cmc queue

            lq = len(q)
            if lq > 3 and q[:3] == 'cmc' :
               self.logger.debug("cmc queue tolerated %s " % q)
               continue

            # at this point any queue that does not start with sarra's default is deleted
            # so any queue should start with q_"username".

            if lq < 2 or q[:2] != 'q_'  :
               self.logger.debug("queue %s deleted: invalid name" % q)
               self.delete_queue(q)
               continue

            # extract username from queuename... 

            if self.users_flag :
               parts = q.split('.')
               username = parts[0][2:]

               # verify all valid usernames
               if username in self.admins                   or \
                  username in self.feeders                  or \
                  username in self.sources                  or \
                  username in self.subscribes:
                  self.logger.debug("queue ok, recognized username %s " % username)
                  continue

               # queue of with invalid or obsolete username
               self.logger.debug("queue %s deleted: invalid username" % q)
               self.delete_queue(q)


    def verify_pump(self):

        error   = 0
        warning = 0

        # verify admin user exists

        if not self.admin :
           self.logger.error("No admin user set ")
           self.logger.error("In default.conf use : feeder amqp://fdr_user@..")
           self.logger.error("                      admin username")
           self.logger.error("In credentials.conf : admin and feeder must be defined")
           error += 1

        # verify admin user works
        else:
           listu = "list users name"
           lst   = run_rabbitmqadmin( self.admin,listu,self.logger )
           if lst != [] :
              self.logger.info("**** admin account verified *****")
              self.logger.info("admin %s"   % self.admin.geturl())
           else:
              self.logger.error("**** account not working on broker ****")
              self.logger.error("admin %s"   % self.admin.geturl())
              error += 1
        
        # verify feeder exists
        # (was kept manager in code but feeder or manager in config file)
        if self.manager :
           self.logger.info("**** feeder account defined *****")
           self.logger.info("feeder %s" % self.manager.geturl())
        else:
           self.logger.error("feeder ... ")
           self.logger.error("No feeder set ")
           self.logger.error("Error: In default.conf use : feeder amqp://f_usern@...")
           self.logger.error("                             admin  a_username")
           self.logger.error("       In credentials.conf : admin and feeder must be defined")
           error += 1

        # verify if some users were defined
        if len(self.users) > 0 :
           self.logger.info("**** users defined *****")
           for u in self.users :
               self.logger.info("user %15s  roles %s" % (u,self.users[u]))
        else :
           self.logger.error("**** users.conf file not present *****")
           self.logger.error("Users should be defined in users.conf, ex.:")
           self.logger.error("root         admin")
           self.logger.error("feeder       feeder")
           self.logger.error("nws-internet source")
           self.logger.error("anonymous    subscribe")
           self.logger.error("After having declared users and roles in users.conf")
           self.logger.error("use: sr_audit --users foreground")
           self.logger.error("it creates users, set their permissions and declare their exchanges")
           self.logger.error("source users are also used in sr_log2source to make products log available to them")
           error += 1

        # verify if the pump have a cluster name set
        #if self.cluster :
        #   self.logger.info("**** cluster (pump name) defined *****")
        #   self.logger.info("cluster %s"   % self.cluster)
        #else :
        #   self.logger.error("**** cluster (pump name) undefined *****")
        #   self.logger.error("cluster clustername")
        #   self.logger.error("The cluster name must be set in default.conf")
        #   self.logger.error("AMQP message headers target one or a list of clusters")
        #   self.logger.error("If not set, no message can be processed.")
        #   error += 1

        #if self.cluster_aliases != [] :
        #   self.logger.info("**** cluster_aliases declared *****")
        #   self.logger.info("cluster_aliases %s"   % self.cluster_aliases)
        #else :
        #   self.logger.warning("**** cluster_aliases undefined but not mandatory *****")
        #   self.logger.warning("cluster_aliases clusteralias1,clusteralias2,...")
        #   self.logger.warning("It can be set in default.conf")
        #   self.logger.warning("It should be used when the cluster can be named in different ways. Ex.:")
        #   self.logger.warning("   cluster ddi")
        #   self.logger.warning("   cluster_aliases DDIDOR,ddi1.cmc,ddi2.cmc")
        #   warning += 1

        #if self.gateway_for != [] :
        #   self.logger.info("**** gateway_for declared *****")
        #   self.logger.info("gateway_for %s" % self.gateway_for)
        #else :
        #   self.logger.warning("**** gateway_for undeclared but not mandatory *****")
        #   self.logger.warning("gateway_for clustername1,clustername2,...")
        #   self.logger.warning("It can be set in default.conf")
        #   self.logger.warning("Use this option if this pump is a hop to other pumps for messages")
        #   self.logger.warning("Declare the pumps using their cluster names like this:")
        #   self.logger.warning("   gateway_for ddi.edm,ddi1.edm,ddi2.edm")
        #   warning += 1

        #if self.report_clusters != {} :
        #   self.logger.info("**** log2clusters.conf file present *****")
        #   self.logger.info("log2clusters.conf")
        #   for  i in self.report_clusters :
        #        cluster,broker,exchange = self.report_clusters[i]
        #        self.logger.info("name %s  url %s exchange %s" % (cluster,broker.geturl(),exchange))
        #else :
        #   self.logger.warning("**** log2clusters.conf file not present but not mandatory *****")
        #   self.logger.warning("Use this file if this cluster is a hop to other pumps'log.")
        #   self.logger.warning("Logs going back to clusters may need to go through this cluster ")
        #   self.logger.warning("You would set to target a cluster like this (one per line):")
        #   self.logger.warning("    #cluster_name url                                exchange")
        #   self.logger.warning("    ddi.edm       amqp://mgr_user@ddi.edm.ec.gc.ca   xreport")
        #   warning += 1

        self.logger.info(" %d error(s) and %d warning(s)" % (error,warning))

    def run(self):
        self.logger.info("sr_audit run")

        # loop : audit should never stop working   ;-)

        while True  :
                      #  heartbeat 
                      ok = self.heartbeat_check()

                      #  is it sleeping ?
                      if not self.has_vip() :
                         self.logger.debug("sr_audit does not have vip=%s, is sleeping" % self.vip)
                         time.sleep(5)
                         continue
                      else:
                         self.logger.debug("sr_audit is active on vip=%s" % self.vip)

                      self.logger.info("sr_audit waking up")
                      self.configure()

                      # do pump admin stuff ... if we are admin

                      if self.pump_admin :
                         self.run_pump_admin()

                      if self.users_flag or self.pump_flag : return

                      self.run_processes_sanity()

                      self.logger.info("audit is sleeping %d seconds " % self.sleep)
                      time.sleep(self.sleep)

    def run_processes_sanity(self):
        self.logger.info("sr_audit run_processes_sanity")

    def run_pump_admin(self):
        self.logger.info("sr_audit run_pump_admin")

        try   :
                # establish an amqp connection using admin

                self.hc = None

                try:
                        self.hc = HostConnect(logger = self.logger)
                        self.hc.loop = False
                        self.hc.set_pika(self.use_pika)
                        self.hc.set_url(self.admin)
                        self.hc.connect()
                except: pass

                if self.hc == None or self.hc.asleep or self.hc.connection == None:
                   self.logger.error("no connection to broker with admin %s" % self.admin.geturl())
                   try : self.hc.close()
                   except: pass
                   time.sleep(5)
                   return

                # verify pump before anything else...

                if self.pump_flag  : self.verify_pump()

                # verify setup : users/exchanges/queues

                if self.users_flag : 
                    # create report shovel configs first
                    self.verify_report_routing()
                    # create pulse configs
                    self.verify_pulse()
                    # verify users from default/credentials
                    self.verify_users()
                    # verify overall exchanges (once everything created)
                    self.verify_exchanges()
                    # setup all exchanges and queues from configs
                    self.run_sr_setup()

                # verify overall queues
                self.verify_queues()

                try : self.hc.close()
                except: pass

        except:
                (stype, svalue, tb) = sys.exc_info()
                self.logger.error("sr_audit/run_pump_admin Type: %s, Value: %s,  ..." % (stype, svalue))


    def reload(self):
        self.logger.info("%s reload" % self.program_name)
        self.close()
        self.configure()
        self.run()

    def start(self):
        self.logger.info("%s %s start" % (self.program_name, sarra.__version__) )
        self.run()

    def stop(self):
        self.logger.info("%s stop" % self.program_name)
        self.close()
        os._exit(0)

    def cleanup(self):
        self.logger.info("%s %s cleanup" % (self.program_name, sarra.__version__) )
        self.close()
        os._exit(0)

    def declare(self):
        self.logger.info("%s %s declare" % (self.program_name, sarra.__version__) )
        self.close()
        os._exit(0)

    def setup(self):
        self.logger.info("%s setup" % self.program_name)
        self.close()
        os._exit(0)
                 
# ===================================
# MAIN
# ===================================

def main():


    args,action,config,old = startup_args(sys.argv)

    # config is optional so check the argument
    if config != None:
       cfg = sr_config()
       cfg.defaults()
       cfg.general()
       ok,config = cfg.config_path('audit',config,mandatory=False)
       if not ok :
          args.append(config)
          config = None

    audit = sr_audit(config,args)

    if old :
       audit.logger.warning("Should invoke 1: %s [args] action config" % sys.argv[0])

    if hasattr( audit.admin, 'username') :
        audit.logger.debug("Admin set to %s @ %s " % ( audit.admin.username, audit.admin.hostname ) )
    else:
        audit.logger.info("%s has no admin set..." % audit.program_name)
        action = 'stop'

    if   action == 'foreground' : audit.foreground_parent()
    elif action == 'reload'     : audit.reload_parent()
    elif action == 'restart'    : audit.restart_parent()
    elif action == 'start'      : audit.start_parent()
    elif action == 'stop'       : audit.stop_parent()
    elif action == 'status'     : audit.status_parent()
    elif action == 'sanity'     : audit.status_parent(sanity=True)

    elif action == 'cleanup'    : audit.cleanup()
    elif action == 'declare'    : audit.declare()
    elif action == 'setup'      : audit.setup()
    elif action == 'remove'     : pass  # not implemented yet
    else :
           audit.logger.error("action unknown %s" % action)
           os._exit(1)

    os._exit(0)

# =========================================
# direct invocation
# =========================================

if __name__=="__main__":
   main()
