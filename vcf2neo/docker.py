"""
Interface to handle Docker
"""
import os
import random
import time
from shlex import shlex
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError, check_call

from tqdm import tqdm


class Docker(object):
    # TODO: Where are we getting the reference database?
    def __init__(self, refdb=None):
        self.name = "vcf2neo_" + str(random.randint(0, 1000))
        self.refdb = refdb
        self.container = None

    @staticmethod
    def new_split(value):
        lex = shlex(value)
        lex.quotes = '"'
        lex.whitespace_split = True
        lex.commenters = ''
        return list(lex)

    def run(self):
        cmd_str = "docker run --rm -P -v {refdb}:/data -e NEO4J_UID={uid} -e NEO4J_GID={gid} " \
                  "-e NEO4J_AUTH=none -e NEO4J_MONITOR_TRAFFIC=false --name {name} thoba/neo4j_galaxy_ie:v1".format(
            refdb=self.refdb, name=self.name, uid=os.getuid(), gid=os.getgid())
        cmd = self.new_split(cmd_str)
        self.container = Popen(cmd, stdout=PIPE, stderr=STDOUT)
        for i in tqdm(xrange(10), ascii=True, desc="Waiting for Neo4j"):
            time.sleep(1)
        print("Neo4j up!")

    def port(self):
        cmd_str = "docker inspect " \
                  "--format='{{(index (index .NetworkSettings.Ports \"7474/tcp\") 0).HostPort}}' %s" % self.name
        try:
            output = check_output(cmd_str, shell=True)
        except CalledProcessError:
            print("Error running {} on {}".format(cmd_str, self.name))
            exit(1)
        else:
            return output

    def stop(self):
        cmd_str = "docker stop {}".format(self.name)
        cmd = self.new_split(cmd_str)
        try:
            check_call(cmd)
        except CalledProcessError:
            print("Error running: docker stop {}".format(self.name))
            exit(1)
        else:
            print("Successfully stopped {}!".format(self.name))
            return True
